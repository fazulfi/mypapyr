"""Phase 3 dependency-foundation contract tests.

Locks the exact pins in ``requirements.txt`` / ``requirements-dev.txt``, the
installed-version parity, and the import/API surfaces that Phase 3 consumes:

* BE-03 (R2 client) -> ``boto3`` (runtime)
* BE-04 / BE-05 / BE-10 (Redis store, queue, fair-use) -> ``redis`` (runtime)
* SEC-02 (PDF sanitizer) -> ``pikepdf`` (runtime: production worker
  sanitization; sanitize helpers require pikepdf >= 10.9)
* R2 fixture testing -> ``moto`` S3 (dev; safe assertions per
  r2-pikepdf-reference-audit.md section E.1)
* BE-04 / BE-10 unit tests -> ``fakeredis`` (dev)

Design notes:

* No static third-party imports: boto3 and moto do not ship ``py.typed``, so
  the CI strict-mypy gate (``mypy app tests --strict --no-incremental``)
  would fail on missing stubs. Runtime importability is verified through
  ``importlib`` instead, which is the actual contract under test: the
  packages are importable or they are not.
* ``pikepdf`` is a runtime dependency: SEC-02 sanitizes in production, and
  the Dockerfile contract installs engine deps in the builder stage only —
  ``requirements.txt`` IS the builder install, so pinning pikepdf there is
  the sanctioned path (cp313 manylinux wheels, so no apt packages). moto
  and fakeredis stay dev-only: test fixtures, never shipped.
* Every pin must be exact (``name==version``) because CI runs
  ``pip-audit ... --disable-pip --no-deps`` (ci.yml) and the Dockerfile
  builder installs the runtime pins into a deterministic venv.
* The moto smoke-test client uses ``region_name="us-east-1"``: moto does
  not implement R2's region-auto aliasing (audit gap list item 10), so
  ``"auto"`` fails CreateBucket under moto. The production R2 client
  (BE-03) keeps ``region_name="auto"``.
"""

from __future__ import annotations

import importlib
import importlib.metadata
from pathlib import Path
from typing import Any, cast

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
RUNTIME_REQUIREMENTS = BACKEND_DIR / "requirements.txt"
DEV_REQUIREMENTS = BACKEND_DIR / "requirements-dev.txt"

RUNTIME_PACKAGES: dict[str, tuple[str, ...]] = {
    "redis": ("Redis",),
    "boto3": ("client",),
    "pikepdf": ("sanitize", "PasswordError", "PdfError"),
}
DEV_PACKAGES: dict[str, tuple[str, ...]] = {
    "moto": ("mock_aws",),
    "fakeredis": ("FakeRedis", "FakeServer"),
}
PIKEPDF_SANITIZE_HELPERS: tuple[str, ...] = (
    "remove_javascript",
    "remove_attachments",
    "remove_external_access",
    "remove_thumbnails",
    "remove_private_app_data",
    "remove_collection",
)
REDIS_CLIENT_METHODS: tuple[str, ...] = (
    "xautoclaim",
    "xreadgroup",
    "xack",
    "xgroup_create",
    "register_script",
    "pipeline",
    "transaction",
)

_FIXTURE_KEY = "tmp/2026-08-02/0123456789abcdef0123456789abcdef.pdf"
_FIXTURE_BUCKET = "fixture-bucket"


def _parse_pins(path: Path) -> dict[str, str]:
    """Parse exact ``name==version`` pins from a requirements file."""
    pins: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-r", "-e", "--")):
            continue
        name, separator, version = line.partition("==")
        assert separator, f"non-exact pin in {path.name}: {raw!r}"
        assert version and version == version.strip()
        assert " " not in version and "," not in version
        assert all(op not in version for op in ("<", ">", "~", "!"))
        pins[name] = version
    assert pins, f"no pins parsed from {path.name}"
    return pins


def _installed_version(package: str) -> str:
    return importlib.metadata.version(package.split("[", 1)[0])


def _module_attr(module_name: str, attribute: str) -> Any:
    """Runtime-imported attribute access; the single cast crossing point."""
    return getattr(cast(Any, importlib.import_module(module_name)), attribute)


def _import_surface(package: str, attributes: tuple[str, ...]) -> None:
    module = importlib.import_module(package)
    missing = [name for name in attributes if getattr(module, name, None) is None]
    assert not missing, f"{package} missing required surface: {missing}"


def _s3_client() -> object:
    client = _module_attr("boto3", "client")
    config_cls = _module_attr("botocore.config", "Config")
    return client(
        "s3",
        endpoint_url="https://account-id.r2.cloudflarestorage.com",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
        config=config_cls(signature_version="s3v4"),
    )


def test_runtime_pins_are_exact() -> None:
    pins = _parse_pins(RUNTIME_REQUIREMENTS)
    assert pins == {
        "fastapi": "0.141.1",
        "starlette": "1.3.1",
        "uvicorn[standard]": "0.39.0",
        "redis": "8.1.0",
        "boto3": "1.43.62",
        "pikepdf": "10.11.0",
        "img2pdf": "0.6.3",
        "Pillow": "12.3.0",
        "pypdfium2": "5.12.1",
        "python-multipart": "0.0.20",
    }


def test_dev_pins_are_exact() -> None:
    pins = _parse_pins(DEV_REQUIREMENTS)
    assert pins == {
        "pytest": "9.1.1",
        "pytest-cov": "6.2.1",
        "httpx": "0.28.1",
        "mypy": "2.3.0",
        "ruff": "0.14.4",
        "moto": "5.2.2",
        "fakeredis": "2.37.0",
    }


def test_pikepdf_is_runtime_pinned() -> None:
    """pikepdf powers production sanitization: runtime pin, builder-installed."""
    runtime = RUNTIME_REQUIREMENTS.read_text(encoding="utf-8")
    assert "pikepdf==10.11.0" in runtime


def test_fixture_packages_are_dev_only() -> None:
    """moto and fakeredis are test fixtures: never shipped in the image."""
    runtime = RUNTIME_REQUIREMENTS.read_text(encoding="utf-8")
    dev = DEV_REQUIREMENTS.read_text(encoding="utf-8")
    for package in ("moto", "fakeredis"):
        assert package not in runtime
        assert package in dev


def test_installed_versions_match_pinned_versions() -> None:
    pinned = _parse_pins(RUNTIME_REQUIREMENTS) | _parse_pins(DEV_REQUIREMENTS)
    for package, version in pinned.items():
        assert _installed_version(package) == version, package


def test_runtime_import_surfaces() -> None:
    for package, attributes in RUNTIME_PACKAGES.items():
        _import_surface(package, attributes)
    redis_client = _module_attr("redis", "Redis")
    missing = [name for name in REDIS_CLIENT_METHODS if getattr(redis_client, name, None) is None]
    assert not missing, f"redis.Redis missing methods: {missing}"


def test_dev_import_surfaces() -> None:
    for package, attributes in DEV_PACKAGES.items():
        _import_surface(package, attributes)


def test_pikepdf_sanitize_helpers_exist() -> None:
    sanitize = _module_attr("pikepdf", "sanitize")
    missing = [name for name in PIKEPDF_SANITIZE_HELPERS if getattr(sanitize, name, None) is None]
    assert not missing, f"pikepdf.sanitize missing helpers: {missing}"


def test_moto_s3_metadata_round_trip_and_presigned_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MOTO_S3_CUSTOM_ENDPOINTS", "https://account-id.r2.cloudflarestorage.com")
    mock_aws = _module_attr("moto", "mock_aws")
    client_error = _module_attr("botocore.exceptions", "ClientError")
    # Build the boto3 client *inside* ``mock_aws()`` so moto's
    # ``botocore.endpoint.make_request`` patch is in force when the endpoint
    # handler chain is constructed. Building it before the patch activates
    # leaves the endpoint creator bound to the real R2 host; when this test
    # runs after another suite that already built a boto3 client (e.g.
    # ``test_download`` via ``R2Client(make_settings())``) the in-process
    # call escapes the moto backend and reaches
    # ``account-id.r2.cloudflarestorage.com`` over TLS, surfacing as
    # ``SSLV3_ALERT_HANDSHAKE_FAILURE``. ``region_name="us-east-1"`` matches
    # moto's supported S3 regions (moto does not implement R2's ``"auto"``
    # alias). The contract under test is the moto S3 round-trip +
    # signed-URL surface, not the production R2 endpoint URL.
    with mock_aws():
        s3 = _s3_client()
        s3.create_bucket(Bucket=_FIXTURE_BUCKET)  # type: ignore[attr-defined]
        s3.put_object(  # type: ignore[attr-defined]
            Bucket=_FIXTURE_BUCKET,
            Key=_FIXTURE_KEY,
            Body=b"fixture",
            Metadata={"expires-at": "2026-08-02T12:00:00Z"},
        )
        head = s3.head_object(Bucket=_FIXTURE_BUCKET, Key=_FIXTURE_KEY)  # type: ignore[attr-defined]
        assert head["Metadata"]["expires-at"] == "2026-08-02T12:00:00Z"
        url = s3.generate_presigned_url(  # type: ignore[attr-defined]
            "get_object",
            Params={"Bucket": _FIXTURE_BUCKET, "Key": _FIXTURE_KEY},
            ExpiresIn=300,
        )
        assert "X-Amz-Expires=300" in url
        assert "X-Amz-Algorithm=AWS4-HMAC-SHA256" in url
        s3.delete_object(Bucket=_FIXTURE_BUCKET, Key=_FIXTURE_KEY)  # type: ignore[attr-defined]
        with pytest.raises(client_error):
            s3.head_object(Bucket=_FIXTURE_BUCKET, Key=_FIXTURE_KEY)  # type: ignore[attr-defined]
