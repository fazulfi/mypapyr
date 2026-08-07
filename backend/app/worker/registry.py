"""Tool-to-executor dispatch registry (P4-02).

The single mapping from the five canonical tool route ids (the closed
:class:`app.routers.capabilities.ToolId` set) to executor factories. The worker
entrypoint consumes :func:`build_executor` as its only dispatch seam; unknown
route ids fail closed with :class:`UnknownRouteError` (never a silent skip,
never a default executor).

Factories construct executors per the pickle-safety contract of each service
module: only :class:`Settings` (and module-level engine defaults) are captured
at construction time; live clients are built lazily inside ``execute``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from app.config import Settings
from app.routers.capabilities import ToolId
from app.services.compress_service import CompressExecutor, GhostscriptEngine
from app.services.image_to_pdf_service import ImageToPdfExecutor
from app.services.merge_service import MergeExecutor
from app.services.pdf_to_jpg_service import PdfToImageExecutor
from app.services.split_service import SplitExecutor
from app.worker.worker import JobExecutor


class UnknownRouteError(KeyError):
    """No executor is registered for the route id; fail closed."""


ExecutorFactory = Callable[[Settings], JobExecutor]


def _compress_factory(settings: Settings) -> JobExecutor:
    return CompressExecutor(settings=settings, engine=GhostscriptEngine())


def _merge_factory(settings: Settings) -> JobExecutor:
    return MergeExecutor(settings=settings)


def _split_factory(settings: Settings) -> JobExecutor:
    return SplitExecutor(settings=settings)


def _jpg_to_pdf_factory(settings: Settings) -> JobExecutor:
    return ImageToPdfExecutor(settings=settings)


def _pdf_to_jpg_factory(settings: Settings) -> JobExecutor:
    return PdfToImageExecutor(settings=settings)


EXECUTOR_FACTORIES: Mapping[ToolId, ExecutorFactory] = {
    ToolId.COMPRESS_PDF: _compress_factory,
    ToolId.MERGE_PDF: _merge_factory,
    ToolId.SPLIT_PDF: _split_factory,
    ToolId.JPG_TO_PDF: _jpg_to_pdf_factory,
    ToolId.PDF_TO_JPG: _pdf_to_jpg_factory,
}


def build_executor(route: str, settings: Settings) -> JobExecutor:
    """Build the executor registered for *route*; unknown routes fail closed.

    Args:
        route: The canonical tool route id carried by the claimed job entry.
        settings: The process settings forwarded to the executor factory.

    Returns:
        A fresh :class:`JobExecutor` instance for the route.

    Raises:
        UnknownRouteError: When *route* is not one of the five canonical ids.
    """
    try:
        tool = ToolId(route)
    except ValueError:
        raise UnknownRouteError(route) from None
    factory = EXECUTOR_FACTORIES.get(tool)
    if factory is None:
        raise UnknownRouteError(route)
    return factory(settings)
