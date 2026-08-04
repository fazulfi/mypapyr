"""Structured JSON logging tests (BE-01).

Verify the privacy-safe JSON formatter: every record becomes one JSON line
with a fixed schema; prohibited field names (DEC-175: filenames,
passwords, signed URLs, object keys, contents and previews; plus tokens,
authorization, cookies) are redacted recursively through nested mappings
and sequences, case-insensitively; message args are scrubbed before
interpolation; tracebacks are never rendered; and ``setup_logging`` is
idempotent and wired by the application factory without changing the
health contract.
"""

from __future__ import annotations

import io
import json
import logging
import sys
from datetime import UTC, datetime
from types import TracebackType
from typing import cast

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.utils.logging import (
    REDACTED_VALUE,
    PapyrJsonHandler,
    PrivacyFormatter,
    redact,
    setup_logging,
)


def _record(
    *,
    msg: str = "hello",
    args: tuple[object, ...] | dict[str, object] = (),
    fields: dict[str, object] | None = None,
    exc_info: tuple[type[BaseException], BaseException, TracebackType | None]
    | tuple[None, None, None]
    | None = None,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=exc_info,
    )
    if fields is not None:
        record.fields = fields
    return record


def _format(record: logging.LogRecord) -> dict[str, object]:
    payload = json.loads(PrivacyFormatter().format(record))
    assert isinstance(payload, dict)
    return payload


# --- formatter schema ---


def test_formatter_emits_fixed_json_schema() -> None:
    payload = _format(_record())
    assert set(payload) == {"timestamp", "level", "logger", "message", "fields"}
    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "hello"
    assert payload["fields"] == {}
    parsed = datetime.fromisoformat(str(payload["timestamp"]))
    assert parsed.tzinfo == UTC


def test_fields_slot_emitted_and_scrubbed() -> None:
    record = _record(fields={"filename": "a.pdf", "status": "ok", "request_id": "abc"})
    payload = _format(record)
    assert payload["fields"] == {
        "filename": REDACTED_VALUE,
        "status": "ok",
        "request_id": "abc",
    }


# --- recursive redaction of prohibited fields ---


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("filename", "report.pdf"),
        ("file_name", "scan.pdf"),
        ("password", "hunter2"),
        ("passwords", "hunter2"),
        ("signed_url", "https://r2.example.com/bucket/tmp/2026-08-02/abc?X-Amz-Signature=xyz"),
        ("signedUrl", "https://example.com/download?token=abc"),
        ("presigned_url", "https://example.com/dl"),
        ("object_key", "tmp/2026-08-02/0123456789abcdef.pdf"),
        ("objectKey", "tmp/x.pdf"),
        ("content", "file-bytes-here"),
        ("contents", "file-bytes-here"),
        ("preview", "data:image/png;base64,AAAA"),
        ("previews", "base64-preview"),
        ("token", "abc123"),
        ("access_token", "abc123"),
        ("tokens", "abc123"),
        ("authorization", "Bearer abc123"),
        ("Authorization", "Bearer abc123"),
        ("cookie", "session=abc"),
        ("cookies", "session=abc"),
        ("client_secret", "supersecret"),
        ("api_key", "key-123"),
        ("url", "https://example.com"),
        ("key", "tmp/2026-08-02/abc.pdf"),
    ],
)
def test_prohibited_keys_redacted(key: str, value: str) -> None:
    assert redact({key: value}) == {key: REDACTED_VALUE}


def test_nested_mapping_redaction() -> None:
    payload = redact(
        {
            "task": {
                "task_id": "uuid-1",
                "user": {"password": "hunter2", "locale": "en"},
            },
            "status": "queued",
        }
    )
    assert payload == {
        "task": {
            "task_id": "uuid-1",
            "user": {"password": REDACTED_VALUE, "locale": "en"},
        },
        "status": "queued",
    }


def test_sequence_redaction_nested() -> None:
    payload = redact(
        {
            "files": [
                {"filename": "a.pdf", "size_bytes": 10},
                {"filename": "b.pdf"},
            ],
            "count": 2,
        }
    )
    assert payload == {
        "files": [
            {"filename": REDACTED_VALUE, "size_bytes": 10},
            {"filename": REDACTED_VALUE},
        ],
        "count": 2,
    }


def test_non_sensitive_values_preserved() -> None:
    original = {
        "request_id": "uuid",
        "status": 200,
        "latency_ms": 12.5,
        "ok": True,
        "nothing": None,
    }
    assert redact(original) == original


def test_bytes_never_emitted() -> None:
    assert redact({"payload": b"\x00secret"}) == {"payload": "<bytes>"}


def test_unsupported_types_become_type_placeholder() -> None:
    when = datetime(2026, 8, 2, tzinfo=UTC)
    assert redact({"when": when}) == {"when": "<datetime>"}


def test_redact_does_not_mutate_input() -> None:
    original = {"user": {"password": "hunter2"}, "files": [{"filename": "a.pdf"}]}
    redact(original)
    assert original == {"user": {"password": "hunter2"}, "files": [{"filename": "a.pdf"}]}


# --- message args and tracebacks ---


def test_message_args_are_scrubbed_before_interpolation() -> None:
    record = _record(msg="failed for %(password)s", args=({"password": "hunter2"},))
    payload = _format(record)
    assert "hunter2" not in str(payload["message"])
    assert REDACTED_VALUE in str(payload["message"])


def test_tuple_message_args_scrubbed() -> None:
    record = _record(msg="sensitive %s", args=({"filename": "report.pdf"},))
    payload = _format(record)
    assert "report.pdf" not in str(payload["message"])
    assert REDACTED_VALUE in str(payload["message"])


def test_message_args_kept_when_safe() -> None:
    record = _record(msg="task %s done", args=(42,))
    assert _format(record)["message"] == "task 42 done"


def test_unknown_args_shape_scrubbed_defensively() -> None:
    # Single documented crossing point: typeshed models LogRecord.args as
    # tuple|Mapping, but a bare list can reach the formatter at runtime, so
    # the defensive scrub branch is exercised with an explicit cast.
    args = cast(tuple[object, ...], [{"filename": "report.pdf"}, 2])
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="values %s",
        args=args,
        exc_info=None,
    )
    payload = _format(record)
    assert "report.pdf" not in str(payload["message"])
    assert REDACTED_VALUE in str(payload["message"])


def test_tracebacks_never_rendered() -> None:
    try:
        raise ValueError("secret-value")
    except ValueError:
        record = _record(msg="boom", exc_info=sys.exc_info())
    rendered = PrivacyFormatter().format(record)
    assert "Traceback" not in rendered
    assert "secret-value" not in rendered


# --- setup_logging wiring ---


def test_setup_logging_installs_single_json_handler() -> None:
    setup_logging("INFO")
    setup_logging("INFO")
    root = logging.getLogger()
    json_handlers = [handler for handler in root.handlers if isinstance(handler, PapyrJsonHandler)]
    assert len(json_handlers) == 1


def test_setup_logging_updates_root_level() -> None:
    setup_logging("DEBUG")
    assert logging.getLogger().level == logging.DEBUG
    setup_logging("INFO")
    assert logging.getLogger().level == logging.INFO


def test_setup_logging_invalid_level_raises() -> None:
    with pytest.raises(ValueError):
        setup_logging("bogus")


def test_setup_logging_accepts_int_level() -> None:
    setup_logging(logging.DEBUG)
    assert logging.getLogger().level == logging.DEBUG
    setup_logging("INFO")


class _FailingStream(io.TextIOBase):
    """A stream whose writes always fail, exercising the handler error path."""

    def write(self, text: str) -> int:
        raise OSError("boom")


def test_handler_swallows_write_failures() -> None:
    handler = PapyrJsonHandler(stream=_FailingStream())
    handler.emit(_record())


def test_setup_logging_emits_single_json_line(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging("INFO")
    logging.getLogger("app.be01").info(
        "job queued",
        extra={"fields": {"filename": "report.pdf", "origin": "http://localhost:3000"}},
    )
    captured = capsys.readouterr()
    lines = [line for line in captured.err.splitlines() if line.strip()]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["logger"] == "app.be01"
    assert payload["message"] == "job queued"
    assert payload["fields"] == {
        "filename": REDACTED_VALUE,
        "origin": "http://localhost:3000",
    }


def test_create_app_wires_structured_logging() -> None:
    instance = create_app()
    root = logging.getLogger()
    assert any(isinstance(handler, PapyrJsonHandler) for handler in root.handlers)
    client = TestClient(instance)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
