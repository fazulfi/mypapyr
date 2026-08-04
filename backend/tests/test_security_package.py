"""Security-package promotion contract tests (Phase 3 prerequisite).

Locks the module-to-package promotion of ``app.security``:

* ``app.security`` must be a *package* (it carries ``__path__``), because
  Phase 3 adds sibling modules (``validation``, ``classification``,
  ``sanitize``, ``fair_use``) under the package namespace — a plain module
  would shadow them.
* The moved implementation lives in ``app.security.middleware``.
* ``app.security`` re-exports the exact public surface the existing
  consumers import (``app.main`` and ``tests/test_headers.py``), and the
  re-exports are the *same objects* as the implementation — no duplicate
  definitions, no drift.
* The legacy ``app/security.py`` module file must be gone; while both the
  module and the package exist, the module wins import resolution and the
  package layout is unusable.

The public import contract (``from app.security import add_security_middleware``,
the exact statement ``app/main.py`` uses) is exercised verbatim below and
throughout the factory tests in ``tests/test_headers.py``.
"""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

from app.security import add_security_middleware

PUBLIC_SURFACE: tuple[str, ...] = (
    "CORS_ALLOW_HEADERS",
    "CORS_ALLOW_METHODS",
    "SECURITY_HEADERS",
    "SecurityHeadersMiddleware",
    "WildcardOriginError",
    "add_security_middleware",
    "build_cors_config",
)

BACKEND_DIR = Path(__file__).resolve().parent.parent


def test_security_is_a_package() -> None:
    spec = importlib.util.find_spec("app.security")
    assert spec is not None
    # Packages expose submodule search locations; plain modules do not.
    assert spec.submodule_search_locations is not None
    assert spec.submodule_search_locations[0].endswith(Path("security").as_posix())


def test_implementation_lives_in_security_middleware_module() -> None:
    middleware = importlib.import_module("app.security.middleware")
    assert middleware.__name__ == "app.security.middleware"
    for name in PUBLIC_SURFACE:
        assert getattr(middleware, name, None) is not None, name


def test_reexports_are_the_implementation_objects() -> None:
    package = importlib.import_module("app.security")
    middleware = importlib.import_module("app.security.middleware")
    for name in PUBLIC_SURFACE:
        assert getattr(package, name) is getattr(middleware, name), name


def test_public_import_contract_line_is_valid() -> None:
    assert (
        add_security_middleware
        is importlib.import_module("app.security.middleware").add_security_middleware
    )
    assert callable(add_security_middleware)


def test_legacy_security_module_file_is_removed() -> None:
    legacy_module = BACKEND_DIR / "app" / "security.py"
    assert not legacy_module.exists(), (
        "app/security.py must be removed; while present it shadows the package "
        "(module wins over package in import resolution)"
    )
