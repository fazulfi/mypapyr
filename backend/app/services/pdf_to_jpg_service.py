"""PDF-to-JPG tool service: rendering helper and job executor (TL-06).

:func:`extract_pages_as_jpg` renders selected PDF pages to JPEG bytes via
pypdfium2 at one documented quality profile (DPI 150); the
:class:`PdfToImageExecutor` is the :class:`JobExecutor` implementation that
downloads the sanitized PDF input from R2, renders every page under the BE-08
per-tool execution cap, uploads each JPEG as a new opaque object, and
idempotently deletes the consumed input (FOUND-01).

Pickle-safety contract (SubprocessJobRunner pickles the executor, worker.py
302-304): the executor holds only picklable construction data (the frozen
:class:`Settings` dataclass and the module-level renderer function) and builds
its R2 client, task store, and boto3 read client lazily on first
:meth:`execute` inside the child process.

Privacy contract (DEC-175): logs carry operation names and exception class
names only.
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from io import BytesIO
from typing import Any, Protocol, cast

from app.config import Settings
from app.queue.store import (
    StoreUnavailableError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.schemas.job import ErrorSummary, ResultSummary
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client
from app.worker.worker import (
    ENGINE_ERROR_FALLBACK,
    ClaimedJob,
    ExecutionKind,
    ExecutionOutcome,
    ProgressReporter,
)

logger = logging.getLogger(__name__)

_REFUSED_ERROR = ErrorSummary(
    code="engine_error", category="engine", retryable=False, message_key="error.engineError"
)
_STORE_UNAVAILABLE_ERROR = ErrorSummary(
    code="store_unavailable", category="engine", retryable=True, message_key="error.engineError"
)

RENDER_DPI = 150
_MIN_DPI = 72
_MAX_DPI = 300
_MAX_PAGE_PIXELS = 16_000_000
_POINTS_PER_INCH = 72

Renderer = Callable[..., list[bytes]]


def extract_pages_as_jpg(
    data: bytes,
    *,
    pages: list[int] | None = None,
    dpi: int = 150,
    pdfium_module: Any | None = None,
    page_size_points: tuple[float, float] | None = None,
) -> list[bytes]:
    if not _MIN_DPI <= dpi <= _MAX_DPI:
        raise ValueError("DPI must be between 72 and 300")
    if page_size_points is not None:
        width = round(page_size_points[0] * dpi / _POINTS_PER_INCH)
        height = round(page_size_points[1] * dpi / _POINTS_PER_INCH)
        if width * height > _MAX_PAGE_PIXELS:
            raise ValueError("page exceeds 16 MP")
    if pdfium_module is None:
        pdfium_module = cast(Any, importlib.import_module("pypdfium2"))
    document = pdfium_module.PdfDocument(data)
    selected = list(range(len(document))) if pages is None else pages
    output: list[bytes] = []
    for index in selected:
        if index < 0 or index >= len(document):
            raise ValueError("page index out of range")
        page = document[index]
        bitmap = page.render(scale=dpi / 72)
        image = bitmap.to_pil().convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=90, optimize=True)
        output.append(buffer.getvalue())
    return output


class S3ReadClient(Protocol):
    def get_object(self, **kwargs: object) -> dict[str, object]: ...


def _build_read_client(settings: Settings) -> S3ReadClient:
    boto3 = cast(Any, importlib.import_module("boto3"))
    botocore_config = cast(Any, importlib.import_module("botocore.config"))
    endpoint = settings.r2_endpoint or (
        f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
    )
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name=settings.r2_region,
        config=botocore_config.Config(
            signature_version="s3v4",
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )
    return cast(S3ReadClient, client)


class PdfToImageExecutor:
    def __init__(self, *, settings: Settings, renderer: Renderer | None = None) -> None:
        self._settings = settings
        self._renderer: Renderer = renderer if renderer is not None else extract_pages_as_jpg
        self._store: TaskStore | None = None
        self._r2: R2Client | None = None
        self._read_client: S3ReadClient | None = None

    @property
    def _get_store(self) -> TaskStore:
        if self._store is None:
            self._store = TaskStore(self._settings)
        return self._store

    @property
    def _get_r2(self) -> R2Client:
        if self._r2 is None:
            self._r2 = R2Client(self._settings)
        return self._r2

    @property
    def _get_read_client(self) -> S3ReadClient:
        if self._read_client is None:
            self._read_client = _build_read_client(self._settings)
        return self._read_client

    def _resolve_record(
        self, job: ClaimedJob
    ) -> ExecutionOutcome | tuple[TaskRecord, tuple[str, ...]]:
        try:
            record = self._get_store.get(job.task_id)
        except TaskNotFoundError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)
        except StoreUnavailableError:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=_STORE_UNAVAILABLE_ERROR)
        if record.state is not JobState.PROCESSING or not record.objects:
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=_REFUSED_ERROR)
        return record, record.objects

    def _download(self, key: str) -> bytes:
        response = self._get_read_client.get_object(Bucket=self._get_r2.bucket_name, Key=key)
        body = response.get("Body")
        read = getattr(body, "read", None)
        if not callable(read):
            raise KeyError(key)
        data = read()
        if isinstance(data, str):
            return data.encode("utf-8")
        return bytes(data)

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        del report
        resolved = self._resolve_record(job)
        if isinstance(resolved, ExecutionOutcome):
            return resolved
        record, input_keys = resolved

        try:
            data = self._download(input_keys[0])
        except Exception as exc:
            logger.error(
                "pdf-to-jpg input download failed",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)

        try:
            images = self._renderer(data, pages=None, dpi=RENDER_DPI)
        except Exception as exc:
            logger.error(
                "pdf-to-jpg render failed",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)

        output_keys: list[str] = []
        for image in images:
            output_key = self._get_r2.build_object_key(extension="jpg")
            self._get_r2.upload_object(
                output_key,
                image,
                content_type="image/jpeg",
                expires_at=record.expires_at,
            )
            output_keys.append(output_key)

        for key in input_keys:
            try:
                self._get_r2.delete_object(key)
            except Exception as exc:
                logger.error(
                    "pdf-to-jpg input delete failure",
                    extra={"fields": {"error": type(exc).__name__}},
                )

        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS,
            result=ResultSummary(output_count=len(images), total_bytes=sum(len(i) for i in images)),
            objects=tuple(output_keys),
        )
