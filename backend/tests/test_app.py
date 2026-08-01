"""Application factory tests.

Verify that ``create_app()`` returns isolated
FastAPI instances with ``/health`` registered, accepts injected settings
without touching the module-level ``app`` export, and installs no
lifespan side effects.
"""

from __future__ import annotations

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
    instance = create_app()
    assert instance.router.on_startup == []
    assert instance.router.on_shutdown == []


def test_testclient_context_manager_works() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
