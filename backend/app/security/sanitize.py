"""Active-content sanitization for PDF payloads (SEC-02).

Implements the SEC-01 :class:`app.security.classification.Sanitizer`
interface contract with the approved pikepdf engine (DEC-199, R-28; A3
brief): JavaScript, embedded attachments, launch actions, and external
actions are removed or neutralized on a fresh in-memory copy of the
document, the SEC-01 :class:`SanitizationCategory` names are reported
without payload details (DEC-090, DEC-091), and the output is re-opened
and verified free of every prohibited category before a ``SANITIZED``
verdict is returned.

Fail-closed posture (DEC-088, DEC-065, DEC-171): password-required,
malformed, and unsafely-sanitizable documents return ``REFUSED`` with no
output bytes; unexpected engine behaviour never raises out of
:meth:`PdfSanitizer.sanitize`. Input is materialized as bytes and opened
from :class:`io.BytesIO` (never a live network stream), and
``attempt_recovery=False`` means a document that needs parsing recovery is
refused instead of being reconstructed from hostile structure.

Encrypted inputs (FR-SHARED-09): :meth:`PdfSanitizer.sanitize` accepts an
optional ``password`` that is threaded into the pikepdf open and consumed
at that point only — the fresh output is always saved unencrypted, the
password is never persisted or logged, and the default value keeps every
other caller refusing locked documents unchanged. A refusal whose cause is
``pikepdf.PasswordError`` is reported on :attr:`refusal_reason` so
admission routers can render a distinct wrong-password error instead of
the generic corruption category.

Sanitization limitations (documented per the execution-matrix SEC-02 test
contract): the engine removes active content reachable through the
documented action slots (catalog open/additional actions, page and
annotation actions, form-field additional actions, outline actions) plus
the embedded-files name tree, ``/AF`` references, and FileAttachment
``/FS`` specifications. Content-stream-level script, XFA, and multimedia
are out of scope by engine design and are not claimed removed. Detection
walks deeper than pikepdf's 50-node ``/Next`` chain cap, so anything the
engine cannot reach is caught by the post-sanitize verification and
refused — active content is never silently downgraded into an output.
"""

from __future__ import annotations

import io
import logging
from collections.abc import Iterator
from enum import StrEnum
from typing import Final

import pikepdf
from pikepdf import Array, Dictionary, Name, Object, Pdf, Stream
from pikepdf.sanitize import Sanitizer as PikepdfSanitizer

from app.errors import ErrorCategory
from app.security.classification import (
    SanitizationCategory,
    SanitizationVerdict,
    Sanitizer,
    SanitizerStatus,
)

__all__ = ["PdfSanitizer", "SanitizerRefusal"]

logger = logging.getLogger(__name__)


class SanitizerRefusal(StrEnum):
    """Closed cause vocabulary for a ``REFUSED`` verdict.

    Lets admission routers distinguish a locked document (wrong or missing
    password, FR-SHARED-09) from a corrupt or otherwise unsupported one
    without exposing payload details; the value is never rendered to users.
    """

    PASSWORD = "password"
    CORRUPT = "corrupt"
    OTHER = "other"


# External-access subtypes, split out from the engine's combined set so the
# launch category is reported separately from the other external actions.
_EXTERNAL_ACTION_SUBTYPES: Final[frozenset[Name]] = frozenset(
    {Name.URI, Name.GoToR, Name.GoToE, Name.SubmitForm, Name.ImportData}
)

# Detection walks deeper than pikepdf's 50-node /Next chain cap: any action
# found beyond the removal reach fails the post-sanitize verification and
# refuses the document (fail closed) instead of downgrading it.
_MAX_CHAIN_DEPTH: Final[int] = 10_000


def _is_action_dict(obj: Object | None) -> bool:
    """True if *obj* looks like a PDF action dictionary (an ``/S`` Name)."""
    if not isinstance(obj, (Dictionary, Stream)):
        return False
    return isinstance(obj.get(Name.S), Name)


def _walk_action_chain(head: Object | None) -> Iterator[Object]:
    """Yield *head* and every action in its ``/Next`` chain, cycle-safe.

    Mirrors the engine's action-slot reachability (single action or
    ``/Next`` array, with object-generation cycle protection) but with a
    larger depth cap, so the detection is a superset of what the engine can
    remove; the difference is what the verification step refuses.
    """
    seen: set[tuple[int, int]] = set()
    stack: list[Object] = [] if head is None else [head]
    visited = 0
    while stack and visited < _MAX_CHAIN_DEPTH:
        action = stack.pop()
        if not _is_action_dict(action):
            continue
        if action.is_indirect:
            objgen = action.objgen
            if objgen in seen:
                continue
            seen.add(objgen)
        visited += 1
        yield action
        nxt = action.get(Name.Next)
        if isinstance(nxt, Array):
            stack.extend(list(nxt))
        elif nxt is not None:
            stack.append(nxt)


def _iter_aa_actions(holder: Object) -> Iterator[Object]:
    """Yield every action in *holder*'s ``/AA`` additional-actions dictionary."""
    aa = holder.get(Name.AA)
    if not isinstance(aa, Dictionary):
        return
    for event_key in list(aa.keys()):
        yield from _walk_action_chain(aa.get(event_key))


def _iter_outline_actions(root: Object) -> Iterator[Object]:
    """Yield the ``/A`` action of every document-outline item, cycle-safe."""
    outlines = root.get(Name.Outlines)
    if not isinstance(outlines, Dictionary):
        return
    visited: set[tuple[int, int]] = set()
    first_item = outlines.get(Name.First)
    stack: list[Object] = [first_item] if first_item is not None else []
    while stack:
        item = stack.pop()
        if not isinstance(item, (Dictionary, Stream)):
            continue
        if item.is_indirect:
            objgen = item.objgen
            if objgen in visited:
                continue
            visited.add(objgen)
        yield from _walk_action_chain(item.get(Name.A))
        nxt = item.get(Name.Next)
        if nxt is not None:
            stack.append(nxt)
        first = item.get(Name.First)
        if first is not None:
            stack.append(first)


def _iter_reachable_actions(pdf: Pdf) -> Iterator[Object]:
    """Yield every action the sanitization engine can reach in *pdf*."""
    root = pdf.Root
    yield from _walk_action_chain(root.get(Name.OpenAction))
    yield from _iter_aa_actions(root)
    for page in pdf.pages:
        yield from _iter_aa_actions(page.obj)
        annots = page.obj.get(Name.Annots)
        if isinstance(annots, Array):
            for annot in annots:
                if not isinstance(annot, Dictionary):
                    continue
                yield from _walk_action_chain(annot.get(Name.A))
                yield from _iter_aa_actions(annot)
    if pdf.acroform.exists:
        for field in pdf.acroform.fields:
            yield from _iter_aa_actions(field.obj)
    yield from _iter_outline_actions(root)


def _named_javascript_present(pdf: Pdf) -> bool:
    """True if the catalog carries the ``/Names/JavaScript`` name tree."""
    names = pdf.Root.get(Name.Names)
    return isinstance(names, Dictionary) and Name.JavaScript in names


def _af_holds_embedded_file(af: Object | None) -> bool:
    """True if an ``/AF`` value points to an embedded-file specification.

    Mirrors the engine's guard: only references with an ``/EF`` entry are
    treated as embedded files, so unrelated keys that happen to be named
    ``/AF`` are not misreported.
    """
    candidates: list[Object] = list(af) if isinstance(af, Array) else [] if af is None else [af]
    return any(isinstance(spec, (Dictionary, Stream)) and Name.EF in spec for spec in candidates)


def _attachment_present(pdf: Pdf) -> bool:
    """True if *pdf* carries embedded files through any supported mechanism."""
    names = pdf.Root.get(Name.Names)
    if isinstance(names, Dictionary) and Name.EmbeddedFiles in names:
        return True
    if pdf.attachments:
        return True
    for obj in pdf.objects:
        if isinstance(obj, (Dictionary, Stream)) and _af_holds_embedded_file(obj.get(Name.AF)):
            return True
    for page in pdf.pages:
        annots = page.obj.get(Name.Annots)
        if isinstance(annots, Array):
            for annot in annots:
                if not isinstance(annot, Dictionary):
                    continue
                if annot.get(Name.Subtype) == Name.FileAttachment and Name.FS in annot:
                    return True
    return False


def _detect_categories(pdf: Pdf) -> tuple[SanitizationCategory, ...]:
    """The SEC-01 categories present in *pdf*, in closed definition order."""
    found: set[SanitizationCategory] = set()
    if _named_javascript_present(pdf):
        found.add(SanitizationCategory.JAVASCRIPT)
    if _attachment_present(pdf):
        found.add(SanitizationCategory.EMBEDDED_ATTACHMENT)
    for action in _iter_reachable_actions(pdf):
        subtype = action.get(Name.S)
        if not isinstance(subtype, Name):
            continue
        if subtype == Name.JavaScript:
            found.add(SanitizationCategory.JAVASCRIPT)
        elif subtype == Name.Launch:
            found.add(SanitizationCategory.LAUNCH_ACTION)
        elif subtype in _EXTERNAL_ACTION_SUBTYPES:
            found.add(SanitizationCategory.EXTERNAL_ACTION)
    return tuple(cat for cat in SanitizationCategory if cat in found)


class PdfSanitizer(Sanitizer):
    """SEC-02 concrete sanitizer implementing the SEC-01 ``Sanitizer`` protocol.

    One instance may be reused across many documents: each
    :meth:`sanitize` call starts from a fresh in-memory document and
    replaces :attr:`output_bytes`. ``CLEAN`` documents are returned
    byte-for-byte unchanged; ``SANITIZED`` documents are a freshly saved,
    unencrypted in-memory rewrite; ``REFUSED`` produces no output bytes.
    """

    output_bytes: bytes | None
    refusal_reason: SanitizerRefusal | None

    def __init__(self) -> None:
        self.output_bytes = None
        self.refusal_reason = None

    def sanitize(self, data: bytes, *, password: str = "") -> SanitizationVerdict:
        """Sanitize *data* in memory and return the SEC-01 verdict.

        The sanitized document (for ``CLEAN``/``SANITIZED`` outcomes) is
        available on :attr:`output_bytes`; it is always ``None`` after a
        refusal, with :attr:`refusal_reason` describing the closed cause.
        ``password`` decrypts an encrypted input at open time only (the
        output is never re-encrypted) and is never logged or persisted;
        the default keeps locked documents refused for callers that do not
        supply one. Never raises with payload details.
        """
        self.output_bytes = None
        self.refusal_reason = None
        try:
            return self._sanitize(data, password=password)
        except pikepdf.PasswordError:
            # Password-required input: wrong, missing, or no supplied
            # password; the document is refused.
            self.refusal_reason = SanitizerRefusal.PASSWORD
            return SanitizationVerdict(status=SanitizerStatus.REFUSED)
        except pikepdf.PdfError:
            # Malformed or structurally unsupported input fails closed; a
            # damaged document is never reconstructed into an output.
            self.refusal_reason = SanitizerRefusal.CORRUPT
            return SanitizationVerdict(status=SanitizerStatus.REFUSED)
        except Exception as exc:
            # Any unexpected engine behaviour fails closed rather than
            # raising with payload details or leaking a partial document;
            # telemetry carries only the closed category and the exception
            # class name (DEC-175, DEC-169).
            self.output_bytes = None
            self.refusal_reason = SanitizerRefusal.OTHER
            logger.error(
                "pdf sanitizer refusal",
                extra={
                    "fields": {
                        "category": ErrorCategory.ENGINE,
                        "error": type(exc).__name__,
                    }
                },
            )
            return SanitizationVerdict(status=SanitizerStatus.REFUSED)

    def _sanitize(self, data: bytes, *, password: str) -> SanitizationVerdict:
        source = io.BytesIO(data)
        with pikepdf.Pdf.open(source, password=password, attempt_recovery=False) as pdf:
            categories = _detect_categories(pdf)
            if not categories and not pdf.is_encrypted:
                self.output_bytes = data
                return SanitizationVerdict(status=SanitizerStatus.CLEAN)
            scrubber = (
                PikepdfSanitizer().remove_javascript().remove_external_access().remove_attachments()
            )
            scrubber.apply(pdf)
            out = io.BytesIO()
            pdf.save(out)
        output = out.getvalue()
        with pikepdf.Pdf.open(io.BytesIO(output), password="", attempt_recovery=False) as check:
            remaining = _detect_categories(check)
        if remaining:
            # A prohibited category survived the pass: the document cannot
            # be claimed sanitized, so it is refused, never downgraded.
            self.refusal_reason = SanitizerRefusal.OTHER
            return SanitizationVerdict(status=SanitizerStatus.REFUSED)
        # Only a verified, active-content-free rewrite is published; a
        # failure in the verification above must never leave output_bytes set.
        self.output_bytes = output
        return SanitizationVerdict(status=SanitizerStatus.SANITIZED, categories=categories)
