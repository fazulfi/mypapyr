"""Concrete ClamAV threat scanner client (U-SEC; BLKR-01, SEC-03/R-10).

Implements the SEC-01 ``ThreatScanner`` protocol with a production clamd
client speaking INSTREAM over plain TCP (standard library ``socket`` only —
no new dependency; ``backend/requirements.txt`` stays U-PINS-owned and
untouched). Construction performs NO network I/O; the daemon is reached only
inside :meth:`ClamdScanner.scan`, so import-time and app-startup stay
side-effect free. All connect/send/recv operations are bounded by
``Settings.scanner_timeout_seconds`` and the response read window is capped
at :data:`_MAX_RESPONSE_BYTES` so a hostile or broken daemon can never hang
the admission path.

Fail-closed verdict mapping (DEC-171; never raises with payload details):

- ``stream: OK`` .................. -> ``CLEAN``
- ``stream: <name> FOUND`` ........ -> ``MALICIOUS``
- ``stream: ... ERROR`` or any
  ambiguous/malformed reply ....... -> ``INDETERMINATE``
- connect refused/reset, timeout,
  disabled scanner ................ -> ``UNAVAILABLE``

Telemetry carries exception class names only (DEC-175): host, port,
signature names, and payload bytes never reach logs or verdicts.
"""

from __future__ import annotations

import logging
import socket
import struct
from typing import Final

from app.config import Settings
from app.security.classification import ScannerStatus, ScannerVerdict

logger = logging.getLogger(__name__)

# INSTREAM framing constants (clamd protocol).
_INSTREAM_COMMAND: Final[bytes] = b"zINSTREAM\x00"
_CHUNK_LENGTH_PREFIX: Final[str] = ">I"  # 4-byte big-endian unsigned length
_STREAM_TERMINATOR: Final[bytes] = struct.pack(">I", 0)  # 4-byte zero-length chunk (spec)
_SEND_CHUNK_SIZE: Final[int] = 64 * 1024

# Bounded response window: clamd replies are short one-line results; anything
# beyond this cap is treated as ambiguous instead of read forever.
_MAX_RESPONSE_BYTES: Final[int] = 4 * 1024


class ClamdScanner:
    """Production ``ThreatScanner`` implemented over the clamd INSTREAM protocol."""

    def __init__(self, settings: Settings) -> None:
        self._enabled = settings.scanner_enabled
        self._host = settings.clamd_host
        self._port = settings.clamd_port
        self._timeout = float(settings.scanner_timeout_seconds)

    def scan(self, data: bytes) -> ScannerVerdict:
        """Scan *data*; returns a closed ``ScannerVerdict``; never raises."""
        if not self._enabled:
            # Disabled scanner never touches the network and still fails closed.
            logger.error("scanner disabled", extra={"fields": {"error": "ScannerDisabled"}})
            return ScannerVerdict(status=ScannerStatus.UNAVAILABLE)
        try:
            response = self._exchange(data)
        except OSError as exc:
            # Connect refused/reset, DNS failure, or timeout: the daemon is
            # unreachable. Class name only in telemetry (DEC-175).
            logger.error(
                "scanner unavailable",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ScannerVerdict(status=ScannerStatus.UNAVAILABLE)
        except (ValueError, struct.error) as exc:
            # Framing/decoding problems are ambiguous outcomes, not daemon loss.
            logger.error(
                "scanner indeterminate",
                extra={"fields": {"error": type(exc).__name__}},
            )
            return ScannerVerdict(status=ScannerStatus.INDETERMINATE)
        return self._classify(response)

    def _exchange(self, data: bytes) -> bytes:
        """One bounded INSTREAM exchange; returns the raw response bytes."""
        with socket.create_connection((self._host, self._port), timeout=self._timeout) as sock:
            sock.settimeout(self._timeout)
            sock.sendall(_INSTREAM_COMMAND)
            for offset in range(0, len(data), _SEND_CHUNK_SIZE):
                chunk = data[offset : offset + _SEND_CHUNK_SIZE]
                sock.sendall(struct.pack(_CHUNK_LENGTH_PREFIX, len(chunk)) + chunk)
            sock.sendall(_STREAM_TERMINATOR)
            return self._read_response(sock)

    @staticmethod
    def _read_response(sock: socket.socket) -> bytes:
        """Read at most ``_MAX_RESPONSE_BYTES``; stops early on a NUL terminator."""
        response = bytearray()
        while len(response) < _MAX_RESPONSE_BYTES:
            chunk = sock.recv(min(1024, _MAX_RESPONSE_BYTES - len(response)))
            if not chunk:
                break
            response.extend(chunk)
            if b"\x00" in chunk:
                break
        return bytes(response)

    @staticmethod
    def _classify(response: bytes) -> ScannerVerdict:
        """Map a daemon reply to a closed verdict; ambiguity fails closed."""
        text = response.split(b"\x00", 1)[0].decode("latin-1", errors="replace").strip()
        if not text.startswith("stream:"):
            return ScannerVerdict(status=ScannerStatus.INDETERMINATE)
        outcome = text.split(":", 1)[1].strip()
        if outcome == "OK":
            return ScannerVerdict(status=ScannerStatus.CLEAN)
        if outcome.endswith("FOUND"):
            return ScannerVerdict(status=ScannerStatus.MALICIOUS)
        # ERROR replies (e.g. "INSTREAM size limit exceeded ERROR") and any
        # unrecognized text are ambiguous: never silently accept.
        return ScannerVerdict(status=ScannerStatus.INDETERMINATE)
