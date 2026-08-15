"""JPG-to-PDF tool service: image normalizer and job executor.

Owned by TL-05 (execution-matrix.md). The :class:`images_to_pdf` function
converts multiple image bytes into one PDF using img2pdf; the
:class:`ImageToPdfExecutor` is the :class:`JobExecutor` implementation that
downloads the sanitized image inputs from R2, converts them under the BE-08
per-tool execution cap, uploads the single PDF output as a new opaque object,
and idempotently deletes the consumed inputs (FOUND-01).

Pickle-safety contract (SubprocessJobRunner pickles the executor, worker.py
302-304): the executor holds only picklable construction data — the frozen
:class:`Settings` dataclass — and builds its R2 client, task store, and
boto3 read client lazily on first :meth:`execute` inside the child process
(live redis.Redis / boto3 clients are not picklable). The admission router
never constructs the executor.

Privacy contract (DEC-175): logs carry operation names and exception class
names only; no task ids, object keys, origins, or payload details ever
reach telemetry.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Any, BinaryIO, Protocol, cast

from PIL import Image, ImageOps

from app.config import Settings
from app.queue.store import (
    StoreUnavailableError,
    TaskNotFoundError,
    TaskRecord,
    TaskStore,
)
from app.routers.capabilities import TOOL_LIMITS, ToolId
from app.schemas.job import ErrorSummary, ResultSummary
from app.services.paper_policy import PaperStandard
from app.tasks.state_machine import JobState
from app.utils.r2 import R2Client
from app.worker.worker import (
    ENGINE_ERROR_FALLBACK,
    ClaimedJob,
    ExecutionKind,
    ExecutionOutcome,
    ProgressReporter,
)

# Decompression-bomb safeguard (kept enabled per external-dependency guidance).
Image.MAX_IMAGE_PIXELS = 20_000_000

logger = logging.getLogger(__name__)

_REFUSED_ERROR = ErrorSummary(
    code="engine_error",
    category="engine",
    retryable=False,
    message_key="error.engineError",
)
_STORE_UNAVAILABLE_ERROR = ErrorSummary(
    code="store_unavailable",
    category="engine",
    retryable=True,
    message_key="error.engineError",
)


@dataclass(frozen=True)
class ImageToPdfRequest:
    images: tuple[bytes | BinaryIO, ...]
    paper: PaperStandard = PaperStandard.A4
    per_image_orientation: bool = True


def _normalise_image(data: bytes | BinaryIO) -> bytes:
    raw = data if isinstance(data, bytes) else data.read()
    with Image.open(BytesIO(raw)) as image:
        image.load()
        oriented = ImageOps.exif_transpose(image).convert("RGB")
        output = BytesIO()
        oriented.save(output, format="JPEG", quality=95)
        return output.getvalue()


def images_to_pdf(req: ImageToPdfRequest, *, timeout: float | None = None) -> bytes:
    del timeout
    if not req.images:
        raise ValueError("at least one image is required")
    normalised = [_normalise_image(item) for item in req.images]
    try:
        img2pdf = cast(Any, importlib.import_module("img2pdf"))
    except ImportError:
        img2pdf = None
    if img2pdf is None:
        images = [Image.open(BytesIO(item)).convert("RGB") for item in normalised]
        output = BytesIO()
        images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
        return output.getvalue()
    kwargs: dict[str, object] = {}
    kwargs["pagesize"] = (
        img2pdf.papersizes["letter"]
        if req.paper is PaperStandard.LETTER
        else img2pdf.papersizes["a4"]
    )
    return cast(bytes, img2pdf.convert(normalised, **kwargs))


class S3ReadClient(Protocol):
    def get_object(self, **kwargs: object) -> dict[str, object]: ...


def _build_read_client(settings: Settings) -> S3ReadClient:
    boto3 = cast(Any, importlib.import_module("boto3"))
    botocore_config = cast(Any, importlib.import_module("botocore.config"))
    endpoint = settings.r2_endpoint or f"https://{settings.r2_account_id}.r2.cloudflarestorage.com"
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name=settings.r2_region,
        config=botocore_config.Config(
            signature_version="s3v4", retries={"max_attempts": 2, "mode": "standard"}
        ),
    )
    return cast(S3ReadClient, client)


class ImageToPdfExecutor:
    def __init__(self, *, settings: Settings) -> None:
        self._settings = settings
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

    def execute(self, job: ClaimedJob, report: ProgressReporter) -> ExecutionOutcome:
        del report
        resolved = self._resolve_record(job)
        if isinstance(resolved, ExecutionOutcome):
            return resolved
        record, input_keys = resolved

        try:
            images = tuple(self._download(key) for key in input_keys)
        except Exception as exc:
            logger.error(
                "jpg-to-pdf input download failed",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)

        timeout = float(TOOL_LIMITS[ToolId.JPG_TO_PDF].max_execution_seconds)
        try:
            output = images_to_pdf(ImageToPdfRequest(images=images), timeout=timeout)
        except Exception as exc:
            logger.error(
                "jpg-to-pdf conversion failed",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ExecutionOutcome(kind=ExecutionKind.FAILURE, error=ENGINE_ERROR_FALLBACK)

        output_key = self._get_r2.build_object_key(extension="pdf")
        self._get_r2.upload_object(
            output_key,
            output,
            content_type="application/pdf",
            expires_at=record.expires_at,
        )
        for key in input_keys:
            try:
                self._get_r2.delete_object(key)
            except Exception as exc:
                logger.error(
                    "jpg-to-pdf input delete failure",
                    extra={"fields": {"error": type(exc).__name__}},
                )

        return ExecutionOutcome(
            kind=ExecutionKind.SUCCESS,
            result=ResultSummary(output_count=1, total_bytes=len(output)),
            objects=(output_key,),
        )
