"""Application factory tests.

Verify that ``create_app()`` returns isolated
FastAPI instances with ``/health`` registered, accepts injected settings
without touching the module-level ``app`` export, wires the BE-04 task
store onto ``app.state.task_store``, and runs a minimal lifespan that
closes the store's Redis connection on shutdown.
"""

from __future__ import annotations

import asyncio
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import REQUIRED_ENV_VARS, Settings, load
from app.main import app, create_app
from app.queue.store import RedisLike, TaskStore


def _settings(**overrides: str) -> Settings:
    env = {name: "test" for name in REQUIRED_ENV_VARS}
    env.update(overrides)
    return Settings.from_env(env)


class _ClosingProbe:
    """Redis client recording whether the store closed it on shutdown."""

    closed = False

    def ping(self) -> bool:
        return True

    def close(self) -> None:
        type(self).closed = True


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


# --- BE-04 task-store lifecycle wiring --------------------------------------


def test_factory_wires_task_store_from_injected_settings() -> None:
    settings = _settings(REDIS_URL="redis://cache.internal:6379/2")
    instance = create_app(settings=settings)
    assert isinstance(instance.state.task_store, TaskStore)


def test_lifespan_closes_task_store_on_shutdown() -> None:
    """The factory's lifespan closes the wired store's Redis client.

    Starlette 1.x always installs a lifespan context; the behavioral
    contract is that entering it succeeds (startup side-effect-free), the
    store stays usable while the app is up, and the store's client is
    closed when the context exits (safe shutdown).
    """
    instance = create_app(settings=_settings())
    probe = _ClosingProbe()
    instance.state.task_store = TaskStore(_settings(), client=cast(RedisLike, probe))
    lifespan_context = instance.router.lifespan_context
    assert lifespan_context is not None

    _ClosingProbe.closed = False

    async def probe_lifespan() -> None:
        async with lifespan_context(instance) as state:
            assert state is None
            instance.state.task_store.ping()
            assert _ClosingProbe.closed is False

    asyncio.run(probe_lifespan())
    assert _ClosingProbe.closed is True


def test_testclient_context_manager_works() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
