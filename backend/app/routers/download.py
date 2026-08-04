"""Signed download authorization API (BE-09).

Serves the typed grant contract ``GET
/api/v1/tools/{tool}/tasks/{task_id}/download/{output}``: a short-lived
presigned R2 GET URL for exactly one output of a task whose record is
terminal-eligible — state ``done``, result present, opaque object refs
(DEC-174) holding *output*. Signing is delegated to the BE-03
:class:`app.utils.r2.R2Client` ``generate_signed_url``
``min(remaining, 300 s)`` contract (DEC-170) — this module never
re-implements lifetime math. The grant echoes the authoritative artifact
``expires_at`` unchanged (DEC-075), so a refreshed URL for the same valid
result never extends retention.

Fail-closed authorization (arch 15, DEC-175): unknown ids, expired ids,
tool mismatches, non-ready or cancelled states, object-missing records,
out-of-range outputs, and the deadline race
(:class:`app.utils.r2.ObjectExpiredError`) all map to the same stable 404
not-found envelope — none of them can be distinguished by probing, and no
response ever exposes ids, object keys, buckets, signed URLs, filenames,
or provider details. Store unavailability and R2 client failures propagate
to the generic 500 envelope (class name logged server-side only). Success
responses carry ``Cache-Control: no-store``: the body embeds a credential.

Dependencies resolve per app through the BE-06 seam pattern: the store
comes from ``app.routers.status.get_task_store`` (consumed, never edited);
the R2 client from :func:`get_r2_client` (``app.state.r2_client`` when
preset, else lazily constructed from ``app.state.settings`` with a process
environment fallback, cached on ``app.state.r2_client``). The router is
mounted in ``app/main.py`` by the single wiring owner.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, cast

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from app.config import Settings, load
from app.queue.store import TaskNotFoundError, TaskRecord, TaskStore
from app.routers.status import get_task_store
from app.tasks.state_machine import JobState
from app.utils.r2 import ObjectExpiredError, R2Client

__all__ = [
    "DownloadContext",
    "DownloadGrant",
    "authorize_download",
    "get_download_context",
    "get_r2_client",
    "get_task_store",
    "router",
]

router = APIRouter(prefix="/api/v1", tags=["download"])


class DownloadGrant(BaseModel):
    """Short-lived signed download grant for one task output.

    ``url`` is the presigned GET URL (valid for ``min(remaining, 300 s)``,
    never beyond the artifact); ``expires_at`` is the authoritative artifact
    expiry — unchanged by any refresh (DEC-075).
    """

    model_config = ConfigDict(extra="forbid")

    url: str = Field(title="URL")
    expires_at: datetime = Field(title="Expires at")


def get_r2_client(request: Request) -> R2Client:
    """Resolve the R2 client for *request*: preset override, else lazy per-app.

    Mirrors :func:`app.routers.status.get_task_store` exactly; the cast of
    ``request.app`` is the repo's single documented crossing point.
    """
    application = cast(FastAPI, request.app)
    cached = getattr(application.state, "r2_client", None)
    if isinstance(cached, R2Client):
        return cached
    settings = getattr(application.state, "settings", None)
    if not isinstance(settings, Settings):
        settings = load()
    client = R2Client(settings)
    application.state.r2_client = client
    return client


@dataclass(frozen=True)
class DownloadContext:
    """The store and R2 client resolved per request (single typed seam)."""

    store: TaskStore
    r2: R2Client


def get_download_context(
    store: Annotated[TaskStore, Depends(get_task_store)],
    r2: Annotated[R2Client, Depends(get_r2_client)],
) -> DownloadContext:
    """Compose the store and R2 client dependencies into one typed context."""
    return DownloadContext(store=store, r2=r2)


def authorize_download(record: TaskRecord, tool: str, *, output: int) -> str | None:
    """The opaque object key grantable for *record*, or ``None`` (fail closed).

    Only a ``done`` task whose result is present and whose object refs hold
    *output* may be granted; a tool mismatch and every other condition
    return ``None``, so the route maps all of them to the same stable 404
    envelope. The store's state machine already guarantees the done/result
    pairing; the guard keeps the function total over arbitrary records.
    """
    if record.tool != tool:
        return None
    if record.state is not JobState.DONE or record.result is None:
        return None
    if output < 0 or output >= len(record.objects):
        return None
    return record.objects[output]


@router.get(
    "/tools/{tool}/tasks/{task_id}/download/{output}",
    response_model=DownloadGrant,
    summary="Signed download",
)
def get_signed_download(
    tool: str,
    task_id: str,
    output: Annotated[int, Path(ge=0)],
    context: Annotated[DownloadContext, Depends(get_download_context)],
    response: Response,
) -> DownloadGrant:
    """Issue a short-lived signed URL for one output of a done task.

    Every denial raises the same stable 404 envelope (unknown, expired,
    mismatch, non-ready, object-missing, out-of-range, deadline race);
    store and R2 failures propagate to the generic 500 envelope. The signed
    URL lifetime is delegated to BE-03's ``min(remaining, 300 s)`` contract.
    """
    try:
        record = context.store.get(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404) from None
    key = authorize_download(record, tool, output=output)
    if key is None:
        raise HTTPException(status_code=404)
    try:
        url = context.r2.generate_signed_url(key, expires_at=record.expires_at)
    except ObjectExpiredError:
        raise HTTPException(status_code=404) from None
    response.headers["Cache-Control"] = "no-store"
    return DownloadGrant(url=url, expires_at=record.expires_at)
