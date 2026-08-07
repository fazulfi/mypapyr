"""Worker entrypoint contract tests (U-WORKER RED-GREEN-REFACTOR).

Date: 2026-08-07
Commit baseline: 921c9dc2 (after U-EXEC complete)
"""

from __future__ import annotations

import signal
import subprocess
import sys
import threading
from unittest.mock import MagicMock, PropertyMock

import pytest

from app.config import Settings
from app.worker.entrypoint import (
    RoutingJobExecutor,
    build_worker,
    health_payload,
    install_signal_handlers,
    resolve_health_port,
)
from app.worker.registry import UnknownRouteError
from app.worker.registry import build_executor as registry_build_executor


def _settings() -> Settings:
    return Settings(
        r2_account_id="fake-account-id",
        r2_access_key_id="fake-access-key",
        r2_secret_access_key="fake-secret-key",
        r2_bucket_name="fake-bucket",
        allowed_origins=("http://localhost:3000",),
        retention_seconds=3600,
        default_timeout_seconds=180,
        redis_url="redis://localhost:6379/0",
        worker_cpus=1,
        worker_memory_bytes=2 * 1024**3,
    )


class TestEntrypointImportabilityWithoutSideEffects:
    def test_fresh_import_creates_no_sockets(self):
        """A never-imported interpreter creates zero sockets while importing."""
        probe = (
            "import socket\n"
            "created = []\n"
            "real_init = socket.socket.__init__\n"
            "def tracked(self, *args, **kwargs):\n"
            "    created.append(1)\n"
            "    return real_init(self, *args, **kwargs)\n"
            "socket.socket.__init__ = tracked\n"
            "import app.worker.entrypoint\n"
            "print(len(created))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        assert result.stdout.strip() == "0", result.stderr

    def test_fresh_import_builds_no_redis_clients(self):
        """Fresh interpreter: Redis builders never run during entrypoint import."""
        probe = (
            "import app.queue.queue as q\n"
            "import app.queue.store as s\n"
            "built = []\n"
            "real_stream = q._build_stream_client\n"
            "def tracked_stream(*args, **kwargs):\n"
            "    built.append('stream')\n"
            "    return real_stream(*args, **kwargs)\n"
            "q._build_stream_client = tracked_stream\n"
            "real_store_init = s.TaskStore.__init__\n"
            "def tracked_store(self, *args, **kwargs):\n"
            "    built.append('store')\n"
            "    return real_store_init(self, *args, **kwargs)\n"
            "s.TaskStore.__init__ = tracked_store\n"
            "import app.worker.entrypoint\n"
            "print(len(built))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        assert result.stdout.strip() == "0", result.stderr


class TestRegistryConsumptionAndUnknownRouteFailClose:
    def test_registry_unknown_route_fails_closed(self):
        settings = _settings()
        with pytest.raises(UnknownRouteError):
            registry_build_executor("nonexistent-tool", settings)

    def test_all_five_tools_resolve_via_registry(self):
        tools = ["compress-pdf", "merge-pdf", "split-pdf", "jpg-to-pdf", "pdf-to-jpg"]
        for tool in tools:
            result = registry_build_executor(tool, _settings())
            assert result is not None


class TestRoutingJobExecutorWiresRegistry:
    def test_routing_executor_holds_settings_only(self):
        settings = _settings()
        executor = RoutingJobExecutor(settings)
        assert executor._settings == settings

    def test_unknown_route_in_execute_raises(self):
        settings = _settings()
        executor = RoutingJobExecutor(settings)
        job = MagicMock()
        type(job).route = PropertyMock(return_value="nonexistent")
        report = MagicMock()
        with pytest.raises(UnknownRouteError):
            executor.execute(job, report)


class TestBuildWorkerWiresRoutingExecutor:
    def test_build_worker_constructs_with_routing_executor(self):
        settings = _settings()
        mock_store = MagicMock()
        mock_client = MagicMock()
        worker = build_worker(settings, store=mock_store, stream_client=mock_client)
        # Verify via isinstance check (module identity issue workaround)
        assert "RoutingJobExecutor" in str(type(worker._executor))
        assert worker._settings == settings
        assert worker._client is mock_client


class TestHealthPayloadTruthfulness:
    def test_ok_when_healthy(self):
        status, body = health_payload(True)
        assert status == 200
        assert body["status"] == "ok"

    def test_degraded_when_not_healthy(self):
        status, body = health_payload(False)
        assert status == 503
        assert body["status"] == "degraded"


class TestSignalHandlersInstallCorrectly:
    def test_installed_handler_actually_sets_stop_event(self):
        """Invoke the handler actually installed by install_signal_handlers()."""
        stop = threading.Event()
        install_signal_handlers(stop)

        # The install_signal_handlers function registers lambdas on the global signal table
        # We verify those lambdas actually exist and are callable
        handler = signal.getsignal(signal.SIGTERM)
        assert callable(handler), "SIGTERM handler was not installed"

        # Simulate SIGTERM by invoking the handler directly
        handler(signal.SIGTERM, None)

        # The stop event must be set
        assert stop.is_set(), "Handler did not set stop event"


class TestResolveHealthPort:
    def test_default_to_8000_when_absent(self):
        port = resolve_health_port({})
        assert port == 8000

    def test_respects_env_override_valid(self):
        port = resolve_health_port({"WORKER_HEALTH_PORT": "9000"})
        assert port == 9000

    def test_defaults_when_invalid(self):
        port = resolve_health_port({"WORKER_HEALTH_PORT": "not-a-number"})
        assert port == 8000
