#!/usr/bin/env python3
"""Telegram incident relay for Papyr operational signals (OP-03).

Consumes the fixed monitor report JSON produced by the backend monitor
(``backend/app/ops/monitor.py`` — status, generated_at, checks, summary) and
pages the operator over Telegram for critical (``fail``) checks only, per the
OP-01 severity mapping (``deploy/monitoring/health-signals.md``:
warn -> warning is review-only, never paged; fail -> critical is the incident
path this relay implements).

Privacy contract (DEC-175, DEC-182): the relay transmits the check name,
status, and the *closed* data fields listed in ``ALLOWED_DETAIL_FIELDS`` only.
Any detail field outside that allowlist, or any non-scalar value, is dropped
before a message is built. No filenames, document content, object keys,
signed URLs, passwords, tokens, payloads, or document metadata can reach a
message; the token and chat id come from the environment
(``TELEGRAM_BOT_TOKEN``, ``TELEGRAM_CHAT_ID``), never from arguments or
committed files.

Alert behaviour:
- Alert on a critical (``fail``) transition.
- Reminder (repeat) after ``--cooldown`` seconds while still critical.
- Deduplicated within the cooldown window; state persisted to ``--state``.
- Recovery message when a previously-critical check leaves critical.
- Transient send failures (network, 5xx, 429) retried up to
  ``--max-attempts`` with ``--retry-delay`` between attempts.
- Permanent send failures (400/401/403/404/410, or a sender script exit 2)
  write a permanent-failure marker file and never retry; a marker present at
  startup fails closed with exit 3 and sends nothing (no paging spam).

Exit codes: 0 success (or dry-run), 1 transient failure after retries,
2 configuration/input error, 3 permanent-failure marker (present or written).
Never sends in ``--dry-run``; ``--sender-script`` is an offline-safe
substitution seam (message on stdin; exit 0 success, 2 permanent, else
transient). Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Mapping, TextIO

__all__ = ["main"]

# ---------------------------------------------------------------------------
# Closed field vocabulary (must match deploy/monitoring/alerts.md allowlist
# block and the OP-01 closed fields). Kept as a single literal for the guard.
# ---------------------------------------------------------------------------
ALLOWED_DETAIL_FIELDS: frozenset[str] = frozenset(
    {
        "status",
        "status_code",
        "error_class",
        "count",
        "pending",
        "oldest_idle_ms",
        "group_exists",
        "worker_probe",
        "age_seconds",
        "reason",
        "region",
        "consecutive_failures",
        "state",
    }
)

ALLOWED_CHECK_STATUSES: frozenset[str] = frozenset({"ok", "warn", "fail"})

# Telegram Bot API treats these as unretryable configuration errors.
PERMANENT_HTTP_CODES: frozenset[int] = frozenset({400, 401, 403, 404, 410})

DEFAULT_COOLDOWN_SECONDS = 3600
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 5.0
DEFAULT_TIMEOUT_SECONDS = 10.0
SENDER_EXIT_PERMANENT = 2

STATE_VERSION = 1
EMPTY_STATE: dict[str, Any] = {"version": STATE_VERSION, "checks": {}}


class SendOutcome(StrEnum):
    SUCCESS = "success"
    TRANSIENT = "transient"
    PERMANENT = "permanent"


class MissingEnvVarError(RuntimeError):
    """A required environment variable is missing or blank (fail closed)."""


def _is_scalar(value: object) -> bool:
    return isinstance(value, (bool, int, float, str))


def allowed_details(details: Mapping[str, object]) -> dict[str, str]:
    """Retain only allowlisted scalar detail fields (privacy filter).

    Anything outside ``ALLOWED_DETAIL_FIELDS`` or that is not a scalar
    (no nested maps, no lists, no bytes) is dropped. This is the single
    data-path filter every message goes through.
    """
    filtered: dict[str, str] = {}
    for name, value in details.items():
        if name not in ALLOWED_DETAIL_FIELDS:
            continue
        if not _is_scalar(value):
            continue
        if isinstance(value, bool):
            filtered[name] = "true" if value else "false"
        else:
            filtered[name] = str(value)
    return filtered


def build_message(
    prefix: str,
    check_name: str,
    status: str,
    details: Mapping[str, object],
    generated_at: str,
    summary: Mapping[str, int],
) -> str:
    """Build the alert text from allowlisted fields only."""
    fields = allowed_details(details)
    lines = ["%s Papyr %s: %s" % (prefix, "critical" if prefix != "RECOVERY" else "cleared", check_name)]
    parts = ["status: %s" % status]
    for name in sorted(fields):
        parts.append("%s: %s" % (name, fields[name]))
    lines.append(" | ".join(parts))
    lines.append("generated_at: %s" % generated_at)
    lines.append(
        "summary: ok=%d warn=%d fail=%d"
        % (summary.get("ok", 0), summary.get("warn", 0), summary.get("fail", 0))
    )
    return "\n".join(lines)


def _send_telegram(token: str, chat_id: str, text: str) -> SendOutcome:
    """POST the message to the Telegram Bot API; classify the outcome."""
    url = "https://api.telegram.org/bot%s/sendMessage" % token
    body = json.dumps(
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    ).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in PERMANENT_HTTP_CODES:
            return SendOutcome.PERMANENT
        return SendOutcome.TRANSIENT
    except OSError:
        return SendOutcome.TRANSIENT
    try:
        payload = json.loads(raw)
    except ValueError:
        return SendOutcome.TRANSIENT
    if payload.get("ok") is True:
        return SendOutcome.SUCCESS
    if isinstance(payload.get("error_code"), int) and payload["error_code"] in PERMANENT_HTTP_CODES:
        return SendOutcome.PERMANENT
    return SendOutcome.TRANSIENT


def _send_via_script(script: str, text: str) -> SendOutcome:
    """Delegate delivery to an external command (offline/test seam).

    The message is the script's stdin. Exit 0 = accepted, exit 2 = permanent
    failure, any other nonzero = transient (retryable). stderr is passed
    through so the operator keeps the failure reason without the relay
    inspecting message bodies.
    """
    try:
        command = [sys.executable, script] if script.lower().endswith(".py") else [script]
        completed = subprocess.run(
            command,
            input=text,
            text=True,
            capture_output=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return SendOutcome.TRANSIENT
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    if completed.returncode == 0:
        return SendOutcome.SUCCESS
    if completed.returncode == SENDER_EXIT_PERMANENT:
        return SendOutcome.PERMANENT
    return SendOutcome.TRANSIENT


def _send_once(args: argparse.Namespace, text: str) -> SendOutcome:
    if args.dry_run:
        sys.stdout.write("[dry-run] %s\n" % text)
        return SendOutcome.SUCCESS
    if args.sender_script:
        return _send_via_script(args.sender_script, text)
    return _send_telegram(args.token, args.chat_id, text)


def deliver(args: argparse.Namespace, text: str) -> SendOutcome:
    """Deliver with retry: transient outcomes retried up to max-attempts."""
    last: SendOutcome = SendOutcome.TRANSIENT
    for attempt in range(1, args.max_attempts + 1):
        last = _send_once(args, text)
        if last != SendOutcome.TRANSIENT:
            return last
        if attempt < args.max_attempts and args.retry_delay > 0:
            time.sleep(args.retry_delay)
    return last


def read_report(path: str) -> dict[str, Any]:
    """Read and minimally validate the monitor report JSON."""
    if path == "-":
        raw = sys.stdin.read()
    else:
        try:
            with open(path, encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as exc:
            raise ValueError("report unreadable: %s" % exc) from exc
    try:
        report = json.loads(raw)
    except ValueError as exc:
        raise ValueError("report is not valid JSON") from exc
    if not isinstance(report, Mapping):
        raise ValueError("report must be a JSON object")
    checks = report.get("checks")
    if not isinstance(checks, list):
        raise ValueError("report must carry a checks list")
    for check in checks:
        if not isinstance(check, Mapping):
            raise ValueError("each check must be a JSON object")
        if not isinstance(check.get("name"), str) or not check["name"]:
            raise ValueError("each check must carry a non-empty string name")
        if check.get("status") not in ALLOWED_CHECK_STATUSES:
            raise ValueError("each check must carry a status in {ok, warn, fail}")
    return report


def load_state(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return dict(EMPTY_STATE)
    try:
        with open(path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        # Corrupt state is treated as absent (fail-open to alert once more)
        # but never crashes the relay.
        return dict(EMPTY_STATE)
    if not isinstance(state, Mapping) or not isinstance(state.get("checks"), Mapping):
        return dict(EMPTY_STATE)
    return {"version": state.get("version", STATE_VERSION), "checks": dict(state["checks"])}


def save_state(path: str, state: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")


def alert_decision(
    prior: Mapping[str, Any], now: datetime, cooldown_seconds: float
) -> str:
    """Decide alert / reminder / dedup for a currently-critical check."""
    if not prior.get("critical"):
        return "alert"
    last_raw = prior.get("last_alert_at")
    if not isinstance(last_raw, str):
        return "alert"
    try:
        last = datetime.fromisoformat(last_raw)
    except ValueError:
        return "alert"
    if (now - last).total_seconds() >= cooldown_seconds:
        return "reminder"
    return "dedup"


def require_env(args: argparse.Namespace) -> None:
    """Fail closed when a live Telegram send cannot be authenticated (never
    in dry-run or sender-script mode: dry-run never sends, and a sender
    script delegates delivery and its own auth policy)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token:
        raise MissingEnvVarError("TELEGRAM_BOT_TOKEN is required (set it out of band)")
    if not chat_id:
        raise MissingEnvVarError("TELEGRAM_CHAT_ID is required (set it out of band)")
    args.token = token
    args.chat_id = chat_id


def _print(message: str, out: TextIO) -> None:
    out.write(message + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="telegram-relay.py",
        description="OP-03 Telegram incident relay (privacy-safe, dedup, retry).",
    )
    parser.add_argument("--report", required=True,
                        help="monitor report JSON path, or - for stdin")
    parser.add_argument("--state", default="telegram-relay-state.json",
                        help="alert state JSON path (dedup/cooldown persistence)")
    parser.add_argument("--marker",
                        help="permanent-failure marker path "
                             "(default: <state>.permanent-failure)")
    parser.add_argument("--cooldown", type=float, default=DEFAULT_COOLDOWN_SECONDS,
                        help="reminder repeat interval while critical (seconds)")
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS,
                        help="transient retry count per message")
    parser.add_argument("--retry-delay", type=float, default=DEFAULT_RETRY_DELAY_SECONDS,
                        help="seconds between transient retry attempts")
    parser.add_argument("--sender-script",
                        help="deliver via external command (stdin = message text; "
                             "exit 0 accepted, 2 permanent, else transient)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print messages, update state, never send or require "
                             "credentials")
    args = parser.parse_args(argv)

    marker_path = args.marker or (args.state + ".permanent-failure")
    args.marker = marker_path

    if os.path.exists(marker_path):
        _print(
            "telegram-relay: permanent-failure marker present (%s); "
            "sending nothing — clear the marker after fixing the channel "
            "credentials or sender" % marker_path,
            sys.stderr,
        )
        return 3

    if not args.dry_run and not args.sender_script:
        try:
            require_env(args)
        except MissingEnvVarError as exc:
            _print("telegram-relay: configuration error — %s" % exc, sys.stderr)
            return 2
    else:
        args.token = ""
        args.chat_id = ""

    try:
        report = read_report(args.report)
    except ValueError as exc:
        _print("telegram-relay: configuration error — %s" % exc, sys.stderr)
        return 2

    state = load_state(args.state)
    checks = state["checks"]
    now = datetime.now(UTC)
    generated_at = report.get("generated_at", now.isoformat(timespec="seconds"))
    if not isinstance(generated_at, str):
        generated_at = now.isoformat(timespec="seconds")
    summary = report.get("summary")
    if not isinstance(summary, Mapping):
        summary = {"ok": 0, "warn": 0, "fail": 0}

    permanent = False
    transient = False
    alerted: list[str] = []
    recovered: list[str] = []
    deduped: list[str] = []
    reminders: list[str] = []

    for check in report["checks"]:
        name = check["name"]
        status = check["status"]
        details = check.get("details")
        prior = checks.get(name, {})
        if not isinstance(details, Mapping):
            details = {}

        if status == "fail":
            decision = alert_decision(prior, now, args.cooldown)
            if decision == "dedup":
                deduped.append(name)
                continue
            if decision == "reminder" and prior.get("alerts_sent"):
                prefix = "REMINDER"
            else:
                prefix = "ALERT"
            text = build_message(
                prefix, name, status, details, generated_at, summary
            )
            outcome = deliver(args, text)
            if outcome == SendOutcome.PERMANENT:
                permanent = True
                with open(marker_path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write("reason: permanent delivery failure for check %s\n" % name)
                _print(
                    "telegram-relay: permanent failure for %s — marker written to %s"
                    % (name, marker_path),
                    sys.stderr,
                )
                break
            if outcome == SendOutcome.TRANSIENT:
                transient = True
                _print(
                    "telegram-relay: transient failure for %s after %d attempt(s)"
                    % (name, args.max_attempts),
                    sys.stderr,
                )
                continue
            checks[name] = {
                "critical": True,
                "last_alert_at": now.isoformat(timespec="seconds"),
                "alerts_sent": int(prior.get("alerts_sent", 0)) + 1,
            }
            if prefix == "REMINDER":
                reminders.append(name)
            else:
                alerted.append(name)
            save_state(args.state, state)
        else:
            if prior.get("critical"):
                text = build_message(
                    "RECOVERY", name, status, details, generated_at, summary
                )
                outcome = deliver(args, text)
                if outcome == SendOutcome.PERMANENT:
                    permanent = True
                    with open(marker_path, "w", encoding="utf-8", newline="\n") as fh:
                        fh.write(
                            "reason: permanent delivery failure for recovery %s\n" % name
                        )
                    _print(
                        "telegram-relay: permanent failure for recovery %s — marker "
                        "written to %s" % (name, marker_path),
                        sys.stderr,
                    )
                    break
                if outcome == SendOutcome.TRANSIENT:
                    transient = True
                    _print(
                        "telegram-relay: transient failure for recovery %s after "
                        "%d attempt(s)" % (name, args.max_attempts),
                        sys.stderr,
                    )
                    continue
                recovered.append(name)
                del checks[name]
                save_state(args.state, state)

    if permanent:
        return 3
    if transient:
        return 1

    parts: list[str] = []
    if alerted:
        parts.append("alerted %s" % ", ".join(sorted(alerted)))
    if reminders:
        parts.append("reminded %s" % ", ".join(sorted(reminders)))
    if recovered:
        parts.append("recovered %s" % ", ".join(sorted(recovered)))
    if deduped:
        parts.append("deduped %s" % ", ".join(sorted(deduped)))
    if not parts:
        _print("telegram-relay: OK — no critical checks", sys.stdout)
    else:
        _print("telegram-relay: %s" % "; ".join(parts), sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())