"""Production worker entrypoint: registry wiring, loop, health, graceful stop."""

from __future__ import annotations

import http.server
import json
import logging
import os
import signal
import threading
from collections.abc import Callable, Mapping
from functools import partial

from app.config import Settings
from app.queue.queue import StreamsRedisLike
from app.queue.store import TaskStore
from app.worker.registry import build_executor
from app.worker.worker import (
    ClaimedJob,
    ExecutionOutcome,
    JobWorker,
    ProgressReporter,
    WorkerOptions,
    WorkerUnavailableError,
)

logger = logging.getLogger(__name__)

DEFAULT_POLL_INTERVAL_SECONDS = 1.0
DEFAULT_HEALTH_PORT = 8000
HEALTH_PORT_ENV_VAR = "WORKER_HEALTH_PORT"
HEALTH_PATH = "/health"
_MAX_PORT_NUMBER = 65535


class RoutingJobExecutor:
    """Registry-consuming executor: delegates each job to its route's executor."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        return build_executor(job.route, self._settings).execute(job, report)


def build_worker(
    settings: Settings,
    *,
    store: TaskStore | None = None,
    stream_client: StreamsRedisLike | None = None,
    options: WorkerOptions | None = None,
) -> JobWorker:
    """Build JobWorker with registry wiring and test injection seams."""
    task_store = store if store is not None else TaskStore(settings)
    return JobWorker(
        settings,
        task_store,
        client=stream_client,
        executor=RoutingJobExecutor(settings),
        options=options,
    )


def health_payload(healthy: bool) -> tuple[int, dict[str, str]]:
    """Closed-literal health contract: 200 ok, 503 degraded."""
    if healthy:
        return 200, {"status": "ok"}
    return 503, {"status": "degraded"}


def _worker_is_healthy(worker: JobWorker) -> bool:
    return worker.healthy


def make_health_handler(
    is_healthy: Callable[[], bool],
) -> type[http.server.BaseHTTPRequestHandler]:
    """Bind the health predicate into a minimal GET-only request handler."""

    class _HealthHandler(http.server.BaseHTTPRequestHandler):
        server_version = "papyr-worker"
        sys_version = ""

        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            if self.path != HEALTH_PATH:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            code, body = health_payload(bool(is_healthy()))
            payload = json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return _HealthHandler


class HealthServer:
    """Threaded loopback-safe HTTP server serving only ``/health``."""

    def __init__(
        self,
        is_healthy: Callable[[], bool],
        *,
        host: str = "0.0.0.0",
        port: int = DEFAULT_HEALTH_PORT,
    ) -> None:
        self._server = http.server.ThreadingHTTPServer(
            (host, port), make_health_handler(is_healthy)
        )
        self._server.daemon_threads = True
        self._thread: threading.Thread | None = None

    @property
    def port(self) -> int:
        return int(self._server.server_address[1])

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            kwargs={"poll_interval": 0.25},
            name="papyr-worker-health",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2.0)


def resolve_health_port(env: Mapping[str, str] | None = None) -> int:
    """Resolve ``WORKER_HEALTH_PORT``; invalid or absent values keep 8000."""
    source = os.environ if env is None else env
    raw = source.get(HEALTH_PORT_ENV_VAR)
    if raw is not None and raw.strip():
        try:
            parsed = int(raw.strip())
        except ValueError:
            return DEFAULT_HEALTH_PORT
        if 0 < parsed <= _MAX_PORT_NUMBER:
            return parsed
    return DEFAULT_HEALTH_PORT


def install_signal_handlers(stop: threading.Event) -> None:
    """Route SIGTERM/SIGINT to ``stop.set()`` (main thread only)."""

    def _handler(signum: int, frame: object) -> None:
        del signum, frame
        stop.set()

    for signo in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(signo, _handler)
        except (ValueError, OSError, RuntimeError):
            logger.warning(
                "worker signal handler not installed",
                extra={"fields": {"signal": int(signo)}},
            )


class WorkerLoop:
    """Drives ``run_once`` until the stop event; graceful, fail-closed."""

    def __init__(
        self,
        worker: JobWorker,
        *,
        stop: threading.Event | None = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
        health: HealthServer | None = None,
    ) -> None:
        self._worker = worker
        self._stop = stop if stop is not None else threading.Event()
        self._poll_interval = poll_interval
        self._health = health

    @property
    def stop_event(self) -> threading.Event:
        return self._stop

    def run(self) -> int:
        try:
            self._worker.run_once()
        except WorkerUnavailableError:
            logger.warning(
                "worker degraded before first health report",
                extra={"fields": {"error": "WorkerUnavailableError"}},
            )
        if self._health is not None:
            self._health.start()
        try:
            while not self._stop.is_set():
                try:
                    self._worker.run_once()
                except WorkerUnavailableError:
                    logger.warning(
                        "worker pass degraded",
                        extra={"fields": {"error": "WorkerUnavailableError"}},
                    )
                self._stop.wait(self._poll_interval)
        finally:
            if self._health is not None:
                self._health.stop()
            self._worker.close()
        return 0


def run(
    settings: Settings,
    *,
    stop: threading.Event | None = None,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    health_port: int = DEFAULT_HEALTH_PORT,
) -> int:
    """Build the worker plus health server and run until stopped."""
    worker = build_worker(settings)
    health = HealthServer(partial(_worker_is_healthy, worker), port=health_port)
    loop = WorkerLoop(worker, stop=stop, poll_interval=poll_interval, health=health)
    return loop.run()


def main(env: Mapping[str, str] | None = None) -> int:
    """Load settings fail-fast, install signal handlers, run the worker."""
    from app.utils.logging import setup_logging  # noqa: PLC0415

    settings = Settings.from_env(os.environ if env is None else env)
    setup_logging(settings.log_level)
    stop = threading.Event()
    install_signal_handlers(stop)
    return run(settings, stop=stop, health_port=resolve_health_port(env))
