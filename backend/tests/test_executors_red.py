"""Executor registry contract tests (U-EXEC GREEN).

Date: 2026-08-07
Commit baseline: 9859516 (after U-ROUTER complete)

Verifies the five-tool dispatch registry maps every canonical ToolId to a
concrete executor factory, builds executors, and fails closed on unknown
routes.
"""

from __future__ import annotations

import pytest

import app.worker.registry
from app.config import Settings
from app.routers.capabilities import ToolId
from app.services.compress_service import CompressExecutor
from app.services.image_to_pdf_service import ImageToPdfExecutor
from app.services.merge_service import MergeExecutor
from app.services.pdf_to_jpg_service import PdfToImageExecutor
from app.services.split_service import SplitExecutor
from app.worker.registry import EXECUTOR_FACTORIES, UnknownRouteError, build_executor


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


def test_executor_registry_module_exists() -> None:
    assert app.worker.registry is not None


def test_build_executor_factory_exists() -> None:
    assert callable(build_executor)


def test_executor_factories_mapping_exists() -> None:
    assert isinstance(EXECUTOR_FACTORIES, dict)


def test_all_five_tools_have_registered_executors() -> None:
    expected_tools = {
        ToolId.COMPRESS_PDF,
        ToolId.MERGE_PDF,
        ToolId.SPLIT_PDF,
        ToolId.JPG_TO_PDF,
        ToolId.PDF_TO_JPG,
    }
    assert set(EXECUTOR_FACTORIES.keys()) == expected_tools


def test_build_executor_raises_for_unknown_route() -> None:
    with pytest.raises(UnknownRouteError):
        build_executor("unknown-tool", _settings())


def test_compress_executor_buildable_via_registry() -> None:
    executor = build_executor("compress-pdf", _settings())
    assert isinstance(executor, CompressExecutor)


def test_merge_executor_buildable_via_registry() -> None:
    executor = build_executor("merge-pdf", _settings())
    assert isinstance(executor, MergeExecutor)


def test_split_executor_buildable_via_registry() -> None:
    executor = build_executor("split-pdf", _settings())
    assert isinstance(executor, SplitExecutor)


def test_image_to_pdf_executor_buildable_via_registry() -> None:
    executor = build_executor("jpg-to-pdf", _settings())
    assert isinstance(executor, ImageToPdfExecutor)


def test_pdf_to_jpg_executor_buildable_via_registry() -> None:
    executor = build_executor("pdf-to-jpg", _settings())
    assert isinstance(executor, PdfToImageExecutor)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
