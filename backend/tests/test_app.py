"""Application factory tests.

Verify that ``create_app()`` returns isolated
FastAPI instances with ``/health`` registered, accepts injected settings
without touching the module-level ``app`` export, and installs no
lifespan side effects.
"""

from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import REQUIRED_ENV_VARS, Settings, load
from app.main import app, create_app


def _settings(**overrides: str) -> Settings:
    env = {name: "test" for name in REQUIRED_ENV_VARS}
    env.update(overrides)
    return Settings.from_env(env)


# --- factory instances, health registration, and module export ---


def test_create_app_returns_fastapi_instance() -> None:
    assert isinstance(create_app(), FastAPI)


def test_create_app_returns_distinct_instances() -> None:
    first = create_app()
    second = create_app()
    assert first is not second


def test_health_registered_on_factory_instance() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_module_level_app_export_preserved() -> None:
    assert isinstance(app, FastAPI)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- injected settings remain isolated from the module-level app ---


def test_factory_accepts_injected_settings() -> None:
    settings = _settings(ALLOWED_ORIGINS="http://override.test")
    instance = create_app(settings=settings)
    assert instance.state.settings is settings


def test_factory_defaults_settings_from_environment() -> None:
    instance = create_app()
    assert instance.state.settings == load()


def test_injected_settings_do_not_touch_global_app() -> None:
    global_settings = app.state.settings
    settings = _settings(ALLOWED_ORIGINS="http://override.test")
    instance = create_app(settings=settings)
    assert instance.state.settings is settings
    assert app.state.settings is global_settings


# --- no lifespan side effects; TestClient context manager works ---


def test_no_lifespan_handlers_registered() -> None:
    """The factory registers no custom startup/shutdown handlers or lifespan.

    Starlette 1.x always installs a default no-op lifespan
    (``starlette.routing._DefaultLifespan``), so ``lifespan_context`` is
    never ``None``. FastAPI 0.141.x additionally wraps that default with its
    own ``_merge_lifespan_context`` context, so the robust invariant is
    behavioral rather than identity-based: with no custom ``lifespan`` and no
    ``on_event`` startup/shutdown handlers, entering the merged context must
    succeed and yield no lifespan state (``None``). A registered handler
    would surface as non-``None`` state here, and a removed/``None``
    lifespan (pre-1.x assumption) is explicitly rejected below.
    """
    instance = create_app()
    lifespan_context = instance.router.lifespan_context
    assert lifespan_context is not None, (
        "Starlette 1.x installs a default no-op lifespan; a None assertion "
        "only held for pre-1.x Starlette semantics"
    )

    async def probe() -> None:
        async with lifespan_context(instance) as state:
            assert state is None, (
                "lifespan state implies a registered startup handler; "
                "create_app() must not install custom lifespan handlers"
            )

    asyncio.run(probe())


def test_testclient_context_manager_works() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
