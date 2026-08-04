"""Privacy-safe structured JSON logging (BE-01).

Every emitted record is a single JSON line with the fixed schema
``{timestamp, level, logger, message, fields}``. Prohibited field names
(DEC-175: filenames, passwords, signed URLs, object keys, contents and
previews; plus tokens, authorization, cookies) are redacted recursively —
through nested mappings and sequences, case-insensitively — so document
data never reaches logs. Message ``args`` are scrubbed before
interpolation and tracebacks are never rendered, keeping both fail-closed.
Non-serializable values become ``<type>`` placeholders; bytes are never
decoded.

Free-form message strings themselves cannot be inspected: callers must
pass structured data via ``extra={"fields": {...}}`` rather than embedding
sensitive values into message text.
"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from io import TextIOBase
from typing import cast

REDACTED_VALUE = "[REDACTED]"

# Normalized (lowercase, separators stripped) key stems that mark a field
# as prohibited. Substring matching after normalization is intentionally
# aggressive: it catches compound keys (``original_filename``,
# ``presigned_url``, ``access_token``) and case variants, and any
# false-positive redaction fails closed (DEC-175).
_SENSITIVE_KEY_STEMS: tuple[str, ...] = (
    "authorization",
    "cookie",
    "password",
    "passwd",
    "secret",
    "token",
    "filename",
    "objectkey",
    "content",
    "preview",
    "signedurl",
    "accesskey",
    "url",
    "key",
)

_INSTALLED_HANDLER: PapyrJsonHandler | None = None


def _normalize_key(key: str) -> str:
    lowered = key.lower()
    for separator in ("_", "-", " "):
        lowered = lowered.replace(separator, "")
    return lowered


def _is_sensitive_key(key: str) -> bool:
    normalized = _normalize_key(key)
    return any(stem in normalized for stem in _SENSITIVE_KEY_STEMS)


def redact(value: object) -> object:
    """Return a deep copy of *value* with prohibited fields redacted.

    Mapping keys are matched case-insensitively by normalized substring
    against the prohibited stems; the key itself is kept and only the
    value is replaced with :data:`REDACTED_VALUE`. Bytes and unsupported
    objects become ``<type>`` placeholders.
    """
    if isinstance(value, Mapping):
        return {
            str(key): REDACTED_VALUE if _is_sensitive_key(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, bytes):
        return "<bytes>"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return f"<{type(value).__name__}>"


def _timestamp(created: float) -> str:
    return datetime.fromtimestamp(created, tz=UTC).isoformat(timespec="milliseconds")


def _scrub_args(record: logging.LogRecord) -> None:
    """Replace *record* args with a scrubbed copy before interpolation."""
    if not record.args:
        return
    if isinstance(record.args, Mapping):
        record.args = {
            str(key): REDACTED_VALUE if _is_sensitive_key(str(key)) else redact(item)
            for key, item in record.args.items()
        }
    elif isinstance(record.args, tuple):
        record.args = tuple(redact(item) for item in record.args)
    else:
        record.args = (redact(record.args),)


class PrivacyFormatter(logging.Formatter):
    """Format :class:`logging.LogRecord` as one redacted JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        _scrub_args(record)
        fields = getattr(record, "fields", None)
        payload = {
            "timestamp": _timestamp(record.created),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "fields": redact(fields) if isinstance(fields, Mapping) else {},
        }
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


class PapyrJsonHandler(logging.Handler):
    """Emit each record as one redacted JSON line.

    The stream resolves at emit time so pytest's capsys capture observes
    output written through the shared handler.
    """

    def __init__(self, stream: TextIOBase | None = None) -> None:
        super().__init__()
        self._stream = stream
        self.setFormatter(PrivacyFormatter())

    def _target(self) -> TextIOBase:
        if self._stream is not None:
            return self._stream
        # Documented crossing point: sys.stderr is typed TextIO | Any in the
        # installed mypy typeshed, though at runtime it is always TextIOBase.
        return cast(TextIOBase, sys.stderr)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._target().write(self.format(record) + "\n")
            self.flush()
        except Exception:
            self.handleError(record)

    def flush(self) -> None:
        self._target().flush()


def _resolve_level(level: str | int) -> int:
    if isinstance(level, int):
        return level
    name = level.strip().upper()
    try:
        return logging.getLevelNamesMapping()[name]
    except KeyError as exc:
        raise ValueError(f"Unknown log level {level!r}") from exc


def setup_logging(level: str | int = "INFO") -> None:
    """Install the JSON handler on the root logger; idempotent per process.

    Repeated calls update the root level without stacking handlers, so the
    application factory can call this on every ``create_app()`` safely.
    """
    root = logging.getLogger()
    handler = _INSTALLED_HANDLER
    if handler is None or handler not in root.handlers:
        handler = PapyrJsonHandler()
        root.addHandler(handler)
        globals()["_INSTALLED_HANDLER"] = handler
    root.setLevel(_resolve_level(level))
