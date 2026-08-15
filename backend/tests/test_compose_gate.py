"""U-COMPOSE deployment contract tests for ``deploy/docker-compose.yml``.

Locks the Phase-5 U-COMPOSE topology contract (BLKR-02 part 2, BLKR-11),
derived from:

* ``audit-outputs/phase-5/plans/phase-5-remediation-plan-v2.md`` (U-COMPOSE
  unit: workers parameterization + scanner service + single-project Redis
  topology fix).
* ``scripts/check-compose.sh`` (the authoritative structural gate this test
  mirrors; it renders the Compose model with PyYAML).
* ``deploy/.env.test`` (the CI-only render fixture).

The production defect these tests encode: the VPS ran two split-brain Compose
projects (``papyr`` api / ``papyr-app`` redis) on two networks, so the API
could not resolve Redis and ``/health/ready`` returned 503, while no worker
or scanner ran at all. The contract is ONE Compose project / ONE internal
network, Redis + clamd resolved by stable in-project service DNS, immutable
digest-form images, truthful health ordering, and a hardened posture.

Design notes mirror ``test_dependencies_worker_pins.py`` and
``test_ci_audit_contract.py``: the file is read as text and asserted with
targeted regular expressions. PyYAML is deliberately NOT imported so the
strict-mypy gate stays satisfied without ``# type: ignore`` or an untyped
dependency; structural rendering belongs to ``scripts/check-compose.sh`` and
the CI ``qa-production-api`` compose-config gate.

RED phase: fails against HEAD (workers ``__SET_ME__`` placeholder, no clamd
service, API standalone with no ``depends_on``, no worker healthcheck, no
explicit network). GREEN once the unified topology lands.
"""

from __future__ import annotations

import re
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
COMPOSE_FILE = BACKEND_DIR.parent / "deploy" / "docker-compose.yml"

# Digest-form image reference: ``registry/path@sha256:<64 hex>``.
_DIGEST_REF = r"[^\s:]+@sha256:[0-9a-f]{64}"
# Required-variable image reference with no mutable default.
_REQUIRED_VAR = r"\$\{PAPYR_[A-Z0-9_]*_IMAGE:\?[^}]+\}"


def _compose_text() -> str:
    assert COMPOSE_FILE.exists(), f"compose file absent: {COMPOSE_FILE}"
    return COMPOSE_FILE.read_text(encoding="utf-8")


def _service_block(text: str, name: str) -> str:
    """Return the YAML block for a top-level ``services.<name>`` entry.

    The block spans from the ``  <name>:`` line (two-space indent) to the next
    two-space-indented sibling key or the end of the services mapping. This is
    a read-only textual slice; structural truth is check-compose.sh's job.
    """
    pattern = re.compile(
        r"^  " + re.escape(name) + r":[^\n]*\n(.*?)(?=^  [A-Za-z0-9_.-]+:|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    # Isolate the services mapping first so a top-level key of the same name
    # (there is none today) cannot shadow a service.
    services_match = re.search(
        r"^services:\n(.*?)(?=^[A-Za-z0-9_.-]+:|\Z)", text, re.MULTILINE | re.DOTALL
    )
    services_body = services_match.group(1) if services_match else text
    match = pattern.search(services_body)
    assert match is not None, f"service block not found: {name}"
    return match.group(0)


def _clamd_service_name(text: str) -> str | None:
    for name in ("clamd", "clamav", "scanner"):
        if re.search(r"^  " + name + r":", text, re.MULTILINE):
            return name
    return None


class TestSingleProjectAndNetwork:
    """One deterministic project name and one explicit internal network."""

    def test_deterministic_project_name(self) -> None:
        text = _compose_text()
        assert re.search(r"^name:\s*papyr-app\s*$", text, re.MULTILINE), (
            "compose must declare the deterministic project name 'papyr-app'"
        )

    def test_single_explicit_network(self) -> None:
        text = _compose_text()
        networks = re.search(
            r"^networks:\n(.*?)(?=^[A-Za-z0-9_.-]+:|\Z)", text, re.MULTILINE | re.DOTALL
        )
        assert networks is not None, "compose must declare an explicit networks: block"
        # Exactly one network key at one level of indentation under networks:.
        keys = re.findall(r"^  ([A-Za-z0-9_.-]+):", networks.group(1), re.MULTILINE)
        assert len(keys) == 1, f"exactly one network expected, found {keys}"

    def test_no_legacy_container_name(self) -> None:
        text = _compose_text()
        assert not re.search(r"^\s+container_name:", text, re.MULTILINE), (
            "no service may use container_name (legacy coupling)"
        )


class TestImmutableImages:
    """api/workers/clamd are required digest-form variables; redis digest-pinned."""

    def test_api_image_required_variable(self) -> None:
        block = _service_block(_compose_text(), "api")
        assert re.search(r"image:\s*\"\$\{PAPYR_API_IMAGE:\?[^}]+\}\"", block), (
            "api image must be the required PAPYR_API_IMAGE variable (immutable-injected)"
        )

    def test_workers_image_required_variable_no_placeholder(self) -> None:
        block = _service_block(_compose_text(), "workers")
        assert "__SET_ME__" not in block, "workers must not carry the __SET_ME__ placeholder"
        assert re.search(r"image:\s*\"\$\{PAPYR_WORKERS_IMAGE:\?[^}]+\}\"", block), (
            "workers image must be the required PAPYR_WORKERS_IMAGE variable"
        )

    def test_redis_image_digest_pinned(self) -> None:
        block = _service_block(_compose_text(), "redis")
        assert re.search(
            r"image:\s*redis:[0-9]+\.[0-9]+\.[0-9]+-alpine@sha256:[0-9a-f]{64}", block
        ), "redis image must be an immutable digest pin"

    def test_clamd_image_digest_form(self) -> None:
        text = _compose_text()
        clamd = _clamd_service_name(text)
        assert clamd is not None, "clamd/clamav/scanner service must exist"
        block = _service_block(text, clamd)
        digest_pin = re.search(r"image:\s*" + _DIGEST_REF, block)
        required_var = re.search(r"image:\s*\"?" + _REQUIRED_VAR + r"\"?", block)
        assert digest_pin or required_var, (
            f"{clamd} image must be a digest pin or a required digest-form variable"
        )
        assert "latest" not in block, f"{clamd} must not use the mutable latest tag"


class TestClamdService:
    """The ClamAV daemon is configured, pinned, healthy, and internal-only."""

    def test_clamd_exists_on_queue_profile(self) -> None:
        text = _compose_text()
        clamd = _clamd_service_name(text)
        assert clamd is not None, "no clamd/clamav/scanner service; U-COMPOSE must add one"
        block = _service_block(text, clamd)
        assert re.search(r"profiles:\s*\[\"queue\"\]", block), (
            f"{clamd} must be on the queue profile"
        )

    def test_clamd_port_internal_only(self) -> None:
        text = _compose_text()
        clamd = _clamd_service_name(text)
        assert clamd is not None
        block = _service_block(text, clamd)
        assert not re.search(r"^\s+ports:", block, re.MULTILINE), (
            f"{clamd} must not publish ports (internal-only)"
        )

    def test_clamd_healthcheck_present(self) -> None:
        text = _compose_text()
        clamd = _clamd_service_name(text)
        assert clamd is not None
        block = _service_block(text, clamd)
        assert re.search(r"^\s+healthcheck:", block, re.MULTILINE), (
            f"{clamd} must declare a healthcheck"
        )


class TestDependencyOrdering:
    """api/workers depend on healthy redis+clamd; no deprecated links."""

    def _depends(self, name: str) -> str:
        block = _service_block(_compose_text(), name)
        match = re.search(r"depends_on:\n(.*?)(?=^\s{2}\S|\Z)", block, re.MULTILINE | re.DOTALL)
        return match.group(1) if match else ""

    def test_api_depends_on_healthy_redis_and_clamd(self) -> None:
        deps = self._depends("api")
        assert re.search(r"redis:\s*\n\s+condition:\s*service_healthy", deps), (
            "api must depend_on redis with condition service_healthy"
        )
        clamd = _clamd_service_name(_compose_text())
        assert clamd and re.search(clamd + r":\s*\n\s+condition:\s*service_healthy", deps), (
            f"api must depend_on {clamd} with condition service_healthy"
        )

    def test_workers_depend_on_healthy_redis_and_clamd(self) -> None:
        deps = self._depends("workers")
        assert re.search(r"redis:\s*\n\s+condition:\s*service_healthy", deps), (
            "workers must depend_on redis with condition service_healthy"
        )
        clamd = _clamd_service_name(_compose_text())
        assert clamd and re.search(clamd + r":\s*\n\s+condition:\s*service_healthy", deps), (
            f"workers must depend_on {clamd} with condition service_healthy"
        )

    def test_no_deprecated_links(self) -> None:
        text = _compose_text()
        assert not re.search(r"^\s+links:", text, re.MULTILINE), (
            "deprecated compose links must not be used"
        )


class TestWorkerHealth:
    """worker health hits the real /health endpoint (worker entrypoint)."""

    def test_worker_healthcheck_hits_real_health(self) -> None:
        block = _service_block(_compose_text(), "workers")
        assert re.search(r"^\s+healthcheck:", block, re.MULTILINE), (
            "workers must declare a healthcheck"
        )
        assert "/health" in block, "worker healthcheck must probe the real /health endpoint"


class TestRedisContract:
    """Redis keeps the R-09 AOF/noeviction/resource/health contract."""

    def test_redis_aof_noeviction_and_bounds(self) -> None:
        block = _service_block(_compose_text(), "redis")
        assert "--appendonly" in block, "redis must enable AOF"
        assert "--maxmemory-policy" in block and "noeviction" in block, (
            "redis must use the noeviction policy"
        )
        assert re.search(r"^\s+mem_limit:", block, re.MULTILINE), "redis must be memory-bounded"
        assert re.search(r"^\s+cpus:", block, re.MULTILINE), "redis must bound cpus"
        assert re.search(r"^\s+healthcheck:", block, re.MULTILINE), (
            "redis must declare a healthcheck"
        )
        assert not re.search(r"^\s+ports:", block, re.MULTILINE), (
            "redis must not publish ports (internal-only)"
        )


class TestEnvFileGateAndNoSecrets:
    """env_file strategy preserved; no secrets; scanner env matches Settings."""

    def test_api_and_workers_env_file_gate(self) -> None:
        for name in ("api", "workers"):
            block = _service_block(_compose_text(), name)
            assert "PAPYR_ENV_FILE" in block, (
                f"{name} env_file must gate on ${{PAPYR_ENV_FILE:?...}}"
            )
            assert "env.production.example" not in block, (
                f"{name} env_file must not reference the committed template"
            )

    def test_no_secret_material(self) -> None:
        lowered = _compose_text().lower()
        for marker in ("r2_secret_access_key=", "password=", "secret_access_key=dummy"):
            assert marker not in lowered, f"compose must not embed secret material: {marker!r}"

    def test_scanner_env_matches_settings_names(self) -> None:
        # backend/app/config.py reads CLAMD_HOST / CLAMD_PORT. The compose
        # scanner wiring must use those exact Settings names so the API and
        # worker resolve clamd by the stable service DNS name.
        text = _compose_text()
        clamd = _clamd_service_name(text)
        assert clamd is not None
        # The API/worker reach clamd via the service name; CLAMD_HOST must be
        # set to that service name in the env wiring (documented contract).
        assert re.search(r"CLAMD_HOST", text), (
            "compose must wire CLAMD_HOST (Settings name) to the clamd service DNS"
        )


class TestHardenedPosture:
    """non-root/read-only/tmpfs/cap-drop/no-new-privileges where feasible."""

    def _assert_hardened(self, name: str) -> None:
        block = _service_block(_compose_text(), name)
        assert re.search(r"^\s+read_only:\s*true", block, re.MULTILINE), (
            f"{name} read_only must be true"
        )
        assert "no-new-privileges:true" in block, f"{name} must set no-new-privileges:true"
        assert re.search(r"cap_drop:\s*\n\s+-\s*ALL", block), f"{name} must drop ALL capabilities"

    def test_api_hardened(self) -> None:
        self._assert_hardened("api")

    def test_workers_hardened(self) -> None:
        self._assert_hardened("workers")

    def test_clamd_hardened(self) -> None:
        clamd = _clamd_service_name(_compose_text())
        assert clamd is not None
        block = _service_block(_compose_text(), clamd)
        assert "no-new-privileges:true" in block, f"{clamd} must set no-new-privileges:true"
        assert re.search(r"cap_drop:\s*\n\s+-\s*ALL", block), f"{clamd} must drop ALL capabilities"


class TestResourceBoundsEffective:
    """Resource limits effective for non-Swarm docker compose (top-level keys)."""

    def test_all_services_bounded(self) -> None:
        text = _compose_text()
        services = re.findall(r"^  ([A-Za-z0-9_.-]+):", _services_body(text), re.MULTILINE)
        assert services, "no services discovered"
        for name in services:
            block = _service_block(text, name)
            assert re.search(r"^\s+cpus:", block, re.MULTILINE), f"{name} missing cpus"
            assert re.search(r"^\s+mem_limit:", block, re.MULTILINE), f"{name} missing mem_limit"
            assert re.search(r"^\s+pids_limit:", block, re.MULTILINE), f"{name} missing pids_limit"


class TestClamdHealthTruthful:
    """clamd healthcheck is a real daemon probe, never a version-only false positive."""

    def test_clamd_healthcheck_rejects_version_only_false_positive(self) -> None:
        clamd = _clamd_service_name(_compose_text())
        assert clamd is not None
        block = _service_block(_compose_text(), clamd)
        assert "clamdscan --version" not in block, (
            f"{clamd} healthcheck must not be the 'clamdscan --version' false positive: "
            "it only checks the client binary is installed and short-circuits the probe, "
            "so a dead clamd would still be marked healthy"
        )
        assert "--version" not in block, (
            f"{clamd} healthcheck must not rely on any --version probe (install-only, "
            "says nothing about whether the daemon is listening/ready)"
        )

    def test_clamd_healthcheck_is_truthful_daemon_probe(self) -> None:
        clamd = _clamd_service_name(_compose_text())
        assert clamd is not None
        block = _service_block(_compose_text(), clamd)
        hc = re.search(r"healthcheck:.*?test:\s*\[(.*?)\]", block, re.DOTALL)
        assert hc is not None, f"{clamd} must declare a healthcheck test"
        test_cmd = hc.group(1)
        assert "3310" in test_cmd, f"{clamd} healthcheck must reach the clamd daemon on port 3310"
        assert "PONG" in test_cmd, (
            f"{clamd} healthcheck must verify the daemon actually answers PONG "
            "(real TCP PING/PONG liveness), so a dead daemon cannot be healthy"
        )


class TestRedisServiceDns:
    """api/workers resolve Redis by Compose service DNS; never localhost, no credentials."""

    def test_api_redis_url_service_dns(self) -> None:
        block = _service_block(_compose_text(), "api")
        assert re.search(r"REDIS_URL=redis://redis:6379/0", block), (
            "api must set REDIS_URL=redis://redis:6379/0 (Compose service DNS 'redis'); "
            "Settings default localhost would not resolve across containers"
        )
        assert "redis://localhost" not in block, "api REDIS_URL must not use localhost"

    def test_workers_redis_url_service_dns(self) -> None:
        block = _service_block(_compose_text(), "workers")
        assert re.search(r"REDIS_URL=redis://redis:6379/0", block), (
            "workers must set REDIS_URL=redis://redis:6379/0 (Compose service DNS 'redis')"
        )
        assert "redis://localhost" not in block, "workers REDIS_URL must not use localhost"

    def test_redis_url_has_no_credentials(self) -> None:
        assert not re.search(r"redis://[^/\s:]+:[^/\s@]+@", _compose_text()), (
            "REDIS_URL must not embed credentials (Redis is internal, no-auth)"
        )


class TestActivationProfiles:
    """--profile app --profile queue activates the full backend stack; edge stays deferred."""

    def test_nginx_excluded_from_app_and_queue(self) -> None:
        block = _service_block(_compose_text(), "nginx")
        assert re.search(r"profiles:\s*\[\"edge\"\]", block), (
            "nginx must be ONLY on the edge profile, excluded from the Phase 5 "
            "app+queue activation command"
        )
        assert '"app"' not in block and '"queue"' not in block, (
            "nginx must not be activatable via app or queue profile"
        )

    def test_no_set_me_in_activated_app_queue_services(self) -> None:
        text = _compose_text()
        clamd = _clamd_service_name(text)
        activated = ["api", "redis", "workers"] + ([clamd] if clamd else [])
        for name in activated:
            block = _service_block(text, name)
            assert "__SET_ME__" not in block, (
                f"{name} is activated by --profile app --profile queue and must not "
                "carry the __SET_ME__ placeholder"
            )

    def test_production_activation_covers_full_stack(self) -> None:
        text = _compose_text()
        clamd = _clamd_service_name(text)
        api = _service_block(text, "api")
        assert re.search(r"profiles:\s*\[\"app\"\]", api), "api must be on the app profile"
        for name in ["redis", "workers"] + ([clamd] if clamd else []):
            block = _service_block(text, name)
            assert re.search(r"profiles:\s*\[\"queue\"\]", block), (
                f"{name} must be on the queue profile so '--profile app --profile queue' "
                "activates the full backend stack"
            )


def _services_body(text: str) -> str:
    match = re.search(r"^services:\n(.*?)(?=^[A-Za-z0-9_.-]+:|\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""
