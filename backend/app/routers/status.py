"""Task status API (BE-06).

Serves the typed status contract ``GET
/api/v1/tools/{tool}/tasks/{task_id}/status`` from BE-04
:class:`app.queue.store.TaskStore` records and the locked
``app.tasks.state_machine`` vocabulary — this router consumes both, it does
not re-implement them. Responses carry state, authoritative timestamps, the
authoritative expiry, measurable progress, and safe error categories
(DEC-033, DEC-070); filenames, passwords, signed URLs, object keys, and
content never appear (DEC-174 records plus the READ-ONLY ``TaskStatus``
schema).

Unknown or expired ids and tool mismatches return the stable 404 not-found
envelope (arch 13.5). Redis removes expired keys, so the store cannot
distinguish an unknown id from an expired one; both are equally
non-revealing. Store failures fail closed through the generic 500 envelope
(exception class name only, logged server-side). Status reads never extend
retention.

The router is mounted by ``app/main.py`` (single wiring owner, BE-01 row;
``app/routers/__init__.py`` carries no re-exports). The store dependency
resolves per app: ``app.state.task_store`` when preset (test/wiring seam),
otherwise a lazily constructed store bound to ``app.state.settings``
(falling back to the process environment), cached on
``app.state.task_store``.
"""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response

from app.config import Settings, load
from app.queue.store import TaskNotFoundError, TaskRecord, TaskStore
from app.schemas.job import TaskStatus
from app.tasks.state_machine import JobState

__all__ = ["get_task_store", "router", "status_payload"]

router = APIRouter(prefix="/api/v1", tags=["status"])


def get_task_store(request: Request) -> TaskStore:
    """Resolve the store for *request*: preset override, else lazy per-app.

    ``request.app`` is typed as a bare ``ASGIApp`` by Starlette; the cast is
    the single documented crossing point (repo pattern, cf. BE-04
    ``_build_client``) onto the factory instance whose ``state`` carries
    the settings and the cached store.
    """
    application = cast(FastAPI, request.app)
    cached = getattr(application.state, "task_store", None)
    if isinstance(cached, TaskStore):
        return cached
    settings = getattr(application.state, "settings", None)
    if not isinstance(settings, Settings):
        settings = load()
    store = TaskStore(settings)
    application.state.task_store = store
    return store


def status_payload(record: TaskRecord) -> TaskStatus:
    """Build the status contract payload from a store record (1:1 mapping).

    ``cancellable`` mirrors the state machine: only ``queued`` records can
    be cancelled (state_machine: user cancellation is only expressible from
    ``queued``). The store enforces the result/error pairing on terminal
    transitions, so the ``TaskStatus`` consistency validator always passes.
    """
    return TaskStatus(
        task_id=record.task_id,
        tool=record.tool,
        state=record.state,
        created_at=record.created_at,
        accepted_at=record.accepted_at,
        updated_at=record.updated_at,
        expires_at=record.expires_at,
        progress=record.progress,
        result=record.result,
        error=record.error,
        queued_at=record.queued_at,
        started_at=record.started_at,
        completed_at=record.completed_at,
        cancellable=record.state is JobState.QUEUED,
    )


@router.get(
    "/tools/{tool}/tasks/{task_id}/status",
    response_model=TaskStatus,
    summary="Task status",
)
def get_task_status(
    tool: str,
    task_id: str,
    store: Annotated[TaskStore, Depends(get_task_store)],
    response: Response,
) -> TaskStatus:
    """Serve the authoritative status for *task_id* under its *tool*.

    Unknown or expired ids raise the stable 404 not-found envelope; a task
    whose record names a different tool is equally non-revealing (404), so
    the path parameter never leaks a task's real tool association. Success
    responses carry ``Cache-Control: no-store``: the body is per-capability
    timing/progress metadata and a shared proxy must never replay it.
    """
    try:
        record = store.get(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404) from None
    if record.tool != tool:
        raise HTTPException(status_code=404)
    response.headers["Cache-Control"] = "no-store"
    return status_payload(record)
