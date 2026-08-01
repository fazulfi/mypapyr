"""Provide deterministic test environment defaults before app imports.

The five CI-injected settings variables are seeded into the process
environment *before any application import*. pytest loads this rootdir
conftest before any test-directory conftest or test module, so
``app.main`` — whose module-level ``app = create_app()`` fails fast without
the five required variables—is always imported with a complete
environment. ``setdefault`` keeps values injected by CI authoritative.
"""

from __future__ import annotations

import os

from app.config import REQUIRED_ENV_VARS

# CI parity defaults: five required vars, ALLOWED_ORIGINS at the CI test value.
_ENV_DEFAULTS: dict[str, str] = {name: "test" for name in REQUIRED_ENV_VARS}
_ENV_DEFAULTS["ALLOWED_ORIGINS"] = "http://localhost:3000"

for _name, _value in _ENV_DEFAULTS.items():
    os.environ.setdefault(_name, _value)
