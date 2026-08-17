"""Active-content sanitization contract tests (SEC-02).

Locks ``app.security.sanitize`` (execution-matrix.md SEC-02 row; plan:
680-689; arch 17; DEC-199, R-28; consumes the SEC-01 interface contract in
``app.security.classification``):

* ``PdfSanitizer`` implements the SEC-01 runtime-checkable
  :class:`app.security.classification.Sanitizer` protocol exactly — the
  only status/category vocabulary is the SEC-01 ``SanitizerStatus`` /
  ``SanitizationCategory`` / ``SanitizationVerdict`` set, never a competing
  type.
* Each active-content category (JavaScript, embedded attachments, launch
  actions, external actions) is removed or neutralized, reported without
  payload details, and verified absent in the re-opened in-memory output
  (DEC-090, DEC-091).
* Attachments are removed and never offered as downloads; the
  FileAttachment annotation itself is retained so page geometry is
  unchanged.
* Fail-closed inputs: password-required/encrypted PDFs, malformed bytes,
  and active content that cannot be fully sanitized (a ``/Launch`` action
  beyond pikepdf's 50-node ``/Next`` chain cap) all yield ``REFUSED`` with
  no output bytes — never a raise and never a partially-sanitized
  document.
* Ordinary page content is preserved; a clean input is returned byte-for-
  byte unchanged (no rewrite beyond what sanitation requires).
* Sanitization limitations are documented in the module code comments
  (matrix test contract).
"""

from __future__ import annotations

import io
import logging
from pathlib import Path

import pikepdf
import pytest
from pikepdf import Array, Dictionary, Name, String

import app.security.sanitize as sanitize_module
from app.errors import ErrorCategory
from app.security.classification import (
    SanitizationCategory,
    SanitizationVerdict,
    Sanitizer,
    SanitizerStatus,
)
from app.security.sanitize import PdfSanitizer, SanitizerRefusal

# Hostile marker strings used inside fixtures; none may ever surface in a
# verdict, its repr, or any category/status string (DEC-175, DEC-169).
_PAYLOAD_MARKERS: tuple[str, ...] = (
    "app.alert(1)",
    "evil.exe",
    "https://evil.example/x",
    "secret payload",
    "note.txt",
)

_EXTERNAL_SUBTYPES: frozenset[str] = frozenset(
    {"/URI", "/GoToR", "/GoToE", "/SubmitForm", "/ImportData"}
)


# --- fixture builders (pikepdf-engine-constructed PDFs, in-memory bytes) ---
#
# Note: ``Dictionary`` construction here uses string keys with explicit
# ``Name`` values because pikepdf 10.11.0's ``Dictionary`` constructor
# rejects ``Name`` enum members as keys ("bad cast"); string values alone
# would be converted to ``String`` objects and silently evade pikepdf's
# action detection. This is a documented engine quirk, not a contract.


def _blank_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _js_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    js = Dictionary({"/S": Name("/JavaScript"), "/JS": "app.alert(1)"})
    pdf.Root[Name.Names] = Dictionary({"/JavaScript": Dictionary({"/Names": Array(["named", js])})})
    pdf.Root[Name.OpenAction] = js
    pdf.pages[0].obj[Name.AA] = Dictionary({"/O": js})
    annot = Dictionary(
        {
            "/Type": Name("/Annot"),
            "/Subtype": Name("/Link"),
            "/Rect": Array([0, 0, 10, 10]),
            "/A": js,
        }
    )
    pdf.pages[0].obj[Name.Annots] = Array([annot])
    outline = pdf.make_indirect(Dictionary({"/Type": Name("/Outlines")}))
    item = pdf.make_indirect(Dictionary({"/Title": "t", "/Parent": outline, "/A": js}))
    outline[Name.First] = item
    outline[Name.Last] = item
    pdf.Root[Name.Outlines] = outline
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _launch_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    launch = Dictionary({"/S": Name("/Launch"), "/F": "evil.exe"})
    pdf.Root[Name.OpenAction] = launch
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _external_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.Root[Name.OpenAction] = Dictionary({"/S": Name("/URI"), "/URI": "https://evil.example/x"})
    goto_r = Dictionary({"/S": Name("/GoToR"), "/F": "remote.pdf", "/D": Array([0, Name("/Fit")])})
    pdf.pages[0].obj[Name.AA] = Dictionary({"/C": goto_r})
    submit = Dictionary({"/S": Name("/SubmitForm"), "/F": "https://evil.example/x"})
    outline = pdf.make_indirect(Dictionary({"/Type": Name("/Outlines")}))
    item = pdf.make_indirect(Dictionary({"/Title": "t", "/Parent": outline, "/A": submit}))
    outline[Name.First] = item
    outline[Name.Last] = item
    pdf.Root[Name.Outlines] = outline
    import_data = Dictionary({"/S": Name("/ImportData"), "/F": "data.fdf"})
    annot = Dictionary(
        {
            "/Type": Name("/Annot"),
            "/Subtype": Name("/Link"),
            "/Rect": Array([0, 0, 10, 10]),
            "/A": import_data,
        }
    )
    pdf.pages[0].obj[Name.Annots] = Array([annot])
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _attachment_pdf_bytes(tmp_path: Path) -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    note = tmp_path / "note.txt"
    note.write_bytes(b"secret payload")
    pdf.attachments["note.txt"] = pikepdf.AttachedFileSpec.from_filepath(pdf, str(note))
    stream = pdf.make_stream(b"payload")
    spec = Dictionary(
        {"/Type": Name("/Filespec"), "/F": "f.txt", "/EF": Dictionary({"/F": stream})}
    )
    pdf.Root[Name.AF] = Array([spec])
    annot = Dictionary(
        {
            "/Type": Name("/Annot"),
            "/Subtype": Name("/FileAttachment"),
            "/Rect": Array([0, 0, 10, 10]),
            "/FS": spec,
        }
    )
    pdf.pages[0].obj[Name.Annots] = Array([annot])
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _kitchen_sink_pdf_bytes(tmp_path: Path) -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    js = Dictionary({"/S": Name("/JavaScript"), "/JS": "app.alert(1)"})
    pdf.Root[Name.Names] = Dictionary({"/JavaScript": Dictionary({"/Names": Array(["named", js])})})
    pdf.Root[Name.OpenAction] = js
    note = tmp_path / "note.txt"
    note.write_bytes(b"secret payload")
    pdf.attachments["note.txt"] = pikepdf.AttachedFileSpec.from_filepath(pdf, str(note))
    stream = pdf.make_stream(b"payload")
    spec = Dictionary(
        {"/Type": Name("/Filespec"), "/F": "f.txt", "/EF": Dictionary({"/F": stream})}
    )
    pdf.Root[Name.AF] = Array([spec])
    launch = Dictionary({"/S": Name("/Launch"), "/F": "evil.exe"})
    outline = pdf.make_indirect(Dictionary({"/Type": Name("/Outlines")}))
    item = pdf.make_indirect(Dictionary({"/Title": "t", "/Parent": outline, "/A": launch}))
    outline[Name.First] = item
    outline[Name.Last] = item
    pdf.Root[Name.Outlines] = outline
    uri = Dictionary({"/S": Name("/URI"), "/URI": "https://evil.example/x"})
    annot = Dictionary(
        {
            "/Type": Name("/Annot"),
            "/Subtype": Name("/Link"),
            "/Rect": Array([0, 0, 10, 10]),
            "/A": uri,
        }
    )
    pdf.pages[0].obj[Name.Annots] = Array([annot])
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _deep_launch_pdf_bytes() -> bytes:
    """A /Launch action 61 hops down a /Next chain (beyond pikepdf's cap)."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    head = Dictionary({"/S": Name("/GoTo"), "/D": Array([0, Name("/Fit")])})
    current = head
    for _ in range(60):
        nxt = Dictionary({"/S": Name("/GoTo"), "/D": Array([0, Name("/Fit")])})
        current[Name.Next] = nxt
        current = nxt
    current[Name.Next] = Dictionary({"/S": Name("/Launch"), "/F": "evil.exe"})
    pdf.Root[Name.OpenAction] = head
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _destination_open_action_pdf_bytes() -> bytes:
    """A catalog open action that is a plain destination array (no actions)."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.Root[Name.OpenAction] = Array([0, Name("/Fit")])
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _non_action_chain_slot_pdf_bytes() -> bytes:
    """An action slot whose /Next points at a dictionary without an /S name."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    goto = Dictionary({"/S": Name("/GoTo"), "/D": Array([0, Name("/Fit")])})
    goto[Name.Next] = Dictionary({"/Type": Name("/Junk")})
    pdf.Root[Name.OpenAction] = goto
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _next_cycle_pdf_bytes() -> bytes:
    """A self-referential /Next chain built from an indirect action object."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    js = pdf.make_indirect(Dictionary({"/S": Name("/JavaScript"), "/JS": "x"}))
    js[Name.Next] = js
    pdf.Root[Name.OpenAction] = js
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _next_array_pdf_bytes() -> bytes:
    """A JavaScript action chaining into an array of URI actions."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    js = Dictionary({"/S": Name("/JavaScript"), "/JS": "x"})
    js[Name.Next] = Array(
        [
            Dictionary({"/S": Name("/URI"), "/URI": "https://evil.example/x"}),
            Dictionary({"/S": Name("/URI"), "/URI": "https://evil.example/y"}),
        ]
    )
    pdf.Root[Name.OpenAction] = js
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _outline_tree_pdf_bytes() -> bytes:
    """A two-level outline tree with /Next siblings and nested /First children."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    outlines = pdf.make_indirect(Dictionary({"/Type": Name("/Outlines")}))
    item1 = pdf.make_indirect(
        Dictionary(
            {
                "/Title": "a",
                "/Parent": outlines,
                "/A": Dictionary({"/S": Name("/Launch"), "/F": "evil.exe"}),
            }
        )
    )
    item2 = pdf.make_indirect(
        Dictionary(
            {
                "/Title": "b",
                "/Parent": outlines,
                "/A": Dictionary({"/S": Name("/URI"), "/URI": "https://evil.example/x"}),
            }
        )
    )
    child = pdf.make_indirect(
        Dictionary(
            {
                "/Title": "c",
                "/Parent": item2,
                "/A": Dictionary(
                    {"/S": Name("/GoToR"), "/F": "r.pdf", "/D": Array([0, Name("/Fit")])}
                ),
            }
        )
    )
    item1[Name.Next] = item2
    item2[Name.First] = child
    outlines[Name.First] = item1
    outlines[Name.Last] = item2
    pdf.Root[Name.Outlines] = outlines
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _outline_cycle_pdf_bytes() -> bytes:
    """Two outline items whose /Next links form an indirect-object cycle."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    outlines = pdf.make_indirect(Dictionary({"/Type": Name("/Outlines")}))
    item1 = pdf.make_indirect(Dictionary({"/Title": "a", "/Parent": outlines}))
    item2 = pdf.make_indirect(
        Dictionary(
            {
                "/Title": "b",
                "/Parent": outlines,
                "/A": Dictionary({"/S": Name("/Launch"), "/F": "evil.exe"}),
            }
        )
    )
    item1[Name.Next] = item2
    item2[Name.Next] = item1
    outlines[Name.First] = item1
    pdf.Root[Name.Outlines] = outlines
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _form_field_js_pdf_bytes() -> bytes:
    """A form field whose /AA additional-actions dictionary runs JavaScript."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    widget = pdf.make_indirect(
        Dictionary(
            {
                "/Type": Name("/Annot"),
                "/Subtype": Name("/Widget"),
                "/FT": Name("/Btn"),
                "/T": "btn",
                "/Rect": Array([0, 0, 10, 10]),
                "/AA": Dictionary({"/F": Dictionary({"/S": Name("/JavaScript"), "/JS": "x"})}),
            }
        )
    )
    pdf.Root[Name.AcroForm] = Dictionary({"/Fields": Array([widget])})
    pdf.pages[0].obj[Name.Annots] = Array([widget])
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _af_only_pdf_bytes() -> bytes:
    """An associated-files reference without an EmbeddedFiles name tree."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    stream = pdf.make_stream(b"payload")
    spec = Dictionary(
        {"/Type": Name("/Filespec"), "/F": "f.txt", "/EF": Dictionary({"/F": stream})}
    )
    pdf.Root[Name.AF] = Array([spec])
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _fileattachment_only_pdf_bytes() -> bytes:
    """A FileAttachment annotation without an EmbeddedFiles name tree."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    stream = pdf.make_stream(b"payload")
    spec = Dictionary(
        {"/Type": Name("/Filespec"), "/F": "f.txt", "/EF": Dictionary({"/F": stream})}
    )
    annot = Dictionary(
        {
            "/Type": Name("/Annot"),
            "/Subtype": Name("/FileAttachment"),
            "/Rect": Array([0, 0, 10, 10]),
            "/FS": spec,
        }
    )
    pdf.pages[0].obj[Name.Annots] = Array([annot])
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _malformed_attachment_tree_pdf_bytes() -> bytes:
    """An EmbeddedFiles name-tree key whose value is not a tree at all."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.Root[Name.Names] = Dictionary({"/EmbeddedFiles": "junk"})
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _content_preserving_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.pages[0].obj[Name.Contents] = pdf.make_stream(b"BT /F1 12 Tf 72 720 Td (Hello Papyr) Tj ET")
    pdf.Root[Name.OpenAction] = Dictionary({"/S": Name("/JavaScript"), "/JS": "app.alert(1)"})
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _password_protected_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.Root[Name.OpenAction] = Dictionary({"/S": Name("/JavaScript"), "/JS": "app.alert(1)"})
    buf = io.BytesIO()
    pdf.save(buf, encryption=pikepdf.Encryption(owner="ownerpw", user="userpw"))
    return buf.getvalue()


def _empty_user_password_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.Root[Name.OpenAction] = Dictionary({"/S": Name("/JavaScript"), "/JS": "app.alert(1)"})
    buf = io.BytesIO()
    pdf.save(buf, encryption=pikepdf.Encryption(owner="ownerpw", user=""))
    return buf.getvalue()


def _clean_password_protected_pdf_bytes() -> bytes:
    """Encrypted, active content free — opens only with the user password."""
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    buf = io.BytesIO()
    pdf.save(buf, encryption=pikepdf.Encryption(owner="ownerpw", user="userpw"))
    return buf.getvalue()


def _hostile_acroform_pdf_bytes() -> bytes:
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    field = pdf.make_indirect(Dictionary({"/FT": Name("/Btn"), "/T": "f", "/Kids": Array([])}))
    field[Name.Kids].append(field)  # self-referential indirect cycle
    pdf.Root[Name.AcroForm] = Dictionary({"/Fields": Array([field])})
    pdf.pages[0].obj[Name.Annots] = Array([Dictionary({"/Type": Name("/Annot")}), String("junk")])
    pdf.Root[Name.Outlines] = Dictionary({"/First": String("junk"), "/Type": Name("/Outlines")})
    buf = io.BytesIO()
    pdf.save(buf)
    return buf.getvalue()


def _truncated_pdf_bytes() -> bytes:
    data = _js_pdf_bytes()
    return data[: len(data) // 2]


def _assert_no_prohibited_content(pdf: pikepdf.Pdf) -> None:
    """Assert every SEC-01 prohibited category is absent from *pdf*."""
    names = pdf.Root.get(Name.Names)
    assert not (isinstance(names, Dictionary) and Name.JavaScript in names)
    assert not (isinstance(names, Dictionary) and Name.EmbeddedFiles in names)
    assert Name.OpenAction not in pdf.Root
    assert len(pdf.attachments) == 0
    assert not any(
        isinstance(obj, (Dictionary, pikepdf.Stream))
        and (af := obj.get(Name.AF)) is not None
        and any(
            isinstance(spec, Dictionary) and Name.EF in spec
            for spec in (af if isinstance(af, Array) else [af])
        )
        for obj in pdf.objects
    )
    for page in pdf.pages:
        annots = page.obj.get(Name.Annots)
        if isinstance(annots, Array):
            for annot in annots:
                if not isinstance(annot, Dictionary):
                    continue
                action = annot.get(Name.A)
                assert (
                    Name.A not in annot
                    or not isinstance(action, Dictionary)
                    or not isinstance(action.get(Name.S), Name)
                )
                assert not (annot.get(Name.Subtype) == Name.FileAttachment and Name.FS in annot)
        assert Name.AA not in page.obj
    outlines = pdf.Root.get(Name.Outlines)
    if isinstance(outlines, Dictionary):
        first = outlines.get(Name.First)
        if isinstance(first, Dictionary):
            action = first.get(Name.A)
            assert (
                Name.A not in first
                or not isinstance(action, Dictionary)
                or not isinstance(action.get(Name.S), Name)
            )


# --- protocol contract ---


def test_implements_security_sanitizer_protocol() -> None:
    sanitizer = PdfSanitizer()
    assert isinstance(sanitizer, Sanitizer)
    verdict = sanitizer.sanitize(_blank_pdf_bytes())
    assert isinstance(verdict, SanitizationVerdict)
    assert isinstance(verdict.status, SanitizerStatus)
    assert all(isinstance(cat, SanitizationCategory) for cat in verdict.categories)


def test_verdict_statuses_and_categories_are_closed_vocabulary() -> None:
    sanitizer = PdfSanitizer()
    for data in (_blank_pdf_bytes(), _js_pdf_bytes(), _launch_pdf_bytes()):
        verdict = sanitizer.sanitize(data)
        assert isinstance(verdict.status, SanitizerStatus)
        assert isinstance(verdict.categories, tuple)
        assert all(isinstance(cat, SanitizationCategory) for cat in verdict.categories)


# --- clean input ---


def test_clean_pdf_reports_clean_and_returns_unchanged_bytes() -> None:
    sanitizer = PdfSanitizer()
    data = _blank_pdf_bytes()
    verdict = sanitizer.sanitize(data)
    assert verdict.status is SanitizerStatus.CLEAN
    assert verdict.categories == ()
    assert sanitizer.output_bytes == data


def test_clean_output_is_never_rewritten() -> None:
    sanitizer = PdfSanitizer()
    data = _blank_pdf_bytes()
    sanitizer.sanitize(data)
    assert sanitizer.output_bytes == data


# --- category removal + accurate reporting ---


def test_javascript_sanitized_with_category_report() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_js_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.JAVASCRIPT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_launch_actions_sanitized_with_category_report() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_launch_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.LAUNCH_ACTION,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_external_actions_sanitized_with_category_report() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_external_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.EXTERNAL_ACTION,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_attachments_removed_and_never_offered_as_downloads(tmp_path: Path) -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_attachment_pdf_bytes(tmp_path))
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.EMBEDDED_ATTACHMENT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        assert len(out.attachments) == 0
        names = out.Root.get(Name.Names)
        assert not (isinstance(names, Dictionary) and Name.EmbeddedFiles in names)
        assert not any(isinstance(obj, Dictionary) and Name.AF in obj for obj in out.objects)
        annots = out.pages[0].obj.get(Name.Annots)
        assert isinstance(annots, Array)
        # The FileAttachment annotation is retained (geometry unchanged) but
        # defanged: its /FS file specification is gone.
        assert annots[0].get(Name.Subtype) == Name.FileAttachment
        assert Name.FS not in annots[0]
        assert len(out.pages) == 1


def test_all_categories_reported_together_in_closed_order(tmp_path: Path) -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_kitchen_sink_pdf_bytes(tmp_path))
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (
        SanitizationCategory.JAVASCRIPT,
        SanitizationCategory.EMBEDDED_ATTACHMENT,
        SanitizationCategory.LAUNCH_ACTION,
        SanitizationCategory.EXTERNAL_ACTION,
    )
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_second_pass_is_clean_and_idempotent(tmp_path: Path) -> None:
    sanitizer = PdfSanitizer()
    first = sanitizer.sanitize(_kitchen_sink_pdf_bytes(tmp_path))
    assert first.status is SanitizerStatus.SANITIZED
    first_output = sanitizer.output_bytes
    assert first_output is not None
    second = sanitizer.sanitize(first_output)
    assert second.status is SanitizerStatus.CLEAN
    assert second.categories == ()
    assert sanitizer.output_bytes == first_output


# --- fail-closed: unsafely sanitizable, encrypted, malformed ---


def test_unsafely_sanitizable_input_refused() -> None:
    # The /Launch action sits beyond pikepdf's 50-node /Next chain cap, so
    # removal cannot reach it; the post-sanitize verification must refuse.
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_deep_launch_pdf_bytes())
    assert verdict.status is SanitizerStatus.REFUSED
    assert verdict.categories == ()
    assert sanitizer.output_bytes is None


def test_password_required_pdf_refused() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_password_protected_pdf_bytes())
    assert verdict.status is SanitizerStatus.REFUSED
    assert verdict.categories == ()
    assert sanitizer.output_bytes is None
    assert sanitizer.refusal_reason is SanitizerRefusal.PASSWORD


def test_empty_user_password_pdf_sanitized_and_output_unencrypted() -> None:
    # An empty user password is not password-required (everyone has it), so
    # the document is sanitized and the fresh output is saved unencrypted.
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_empty_user_password_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.JAVASCRIPT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        assert not out.is_encrypted
        _assert_no_prohibited_content(out)


def test_password_protected_pdf_decrypts_with_correct_password() -> None:
    # A correct password unlocks the document; the fresh output is always
    # saved unencrypted (the password is consumed at open time only).
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_password_protected_pdf_bytes(), password="userpw")
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.JAVASCRIPT,)
    assert sanitizer.refusal_reason is None
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        assert not out.is_encrypted
        _assert_no_prohibited_content(out)


def test_password_protected_clean_pdf_decrypts_to_unencrypted_rewrite() -> None:
    # An encrypted document with no active content must still be rewritten
    # unencrypted: the original bytes (still encrypted) are never uploaded.
    data = _clean_password_protected_pdf_bytes()
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(data, password="userpw")
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == ()
    assert sanitizer.refusal_reason is None
    output = sanitizer.output_bytes
    assert output is not None
    assert output != data
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        assert not out.is_encrypted


def test_password_protected_pdf_wrong_password_refused() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_password_protected_pdf_bytes(), password="not-the-password")
    assert verdict.status is SanitizerStatus.REFUSED
    assert verdict.categories == ()
    assert sanitizer.output_bytes is None
    assert sanitizer.refusal_reason is SanitizerRefusal.PASSWORD


def test_password_protected_pdf_default_password_still_refused() -> None:
    # The default password stays empty so the other four tool routers are
    # unchanged: a supplied password is required to open a locked document.
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_clean_password_protected_pdf_bytes())
    assert verdict.status is SanitizerStatus.REFUSED
    assert sanitizer.output_bytes is None
    assert sanitizer.refusal_reason is SanitizerRefusal.PASSWORD


@pytest.mark.parametrize(
    "data",
    [b"", b"not a pdf at all", _truncated_pdf_bytes()],
    ids=["empty", "garbage", "truncated"],
)
def test_malformed_inputs_refused(data: bytes) -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(data)
    assert verdict.status is SanitizerStatus.REFUSED
    assert verdict.categories == ()
    assert sanitizer.output_bytes is None
    assert sanitizer.refusal_reason is SanitizerRefusal.CORRUPT


def test_hostile_acroform_fails_closed() -> None:
    # A self-referential form field must never raise out of the sanitizer;
    # the document has no active-content categories and is left untouched.
    sanitizer = PdfSanitizer()
    data = _hostile_acroform_pdf_bytes()
    verdict = sanitizer.sanitize(data)
    assert verdict.status is SanitizerStatus.CLEAN
    assert sanitizer.output_bytes == data


def test_destination_open_action_is_not_active_content() -> None:
    sanitizer = PdfSanitizer()
    data = _destination_open_action_pdf_bytes()
    verdict = sanitizer.sanitize(data)
    assert verdict.status is SanitizerStatus.CLEAN
    assert verdict.categories == ()
    assert sanitizer.output_bytes == data


def test_non_action_chain_values_are_ignored() -> None:
    # A /Next hop that is not an action dictionary is not active content and
    # must not derail the walk or the document.
    sanitizer = PdfSanitizer()
    data = _non_action_chain_slot_pdf_bytes()
    verdict = sanitizer.sanitize(data)
    assert verdict.status is SanitizerStatus.CLEAN
    assert verdict.categories == ()
    assert sanitizer.output_bytes == data


def test_next_cycle_terminates_and_sanitizes() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_next_cycle_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.JAVASCRIPT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_next_array_chain_sanitized() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_next_array_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (
        SanitizationCategory.JAVASCRIPT,
        SanitizationCategory.EXTERNAL_ACTION,
    )
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_outline_tree_actions_sanitized() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_outline_tree_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (
        SanitizationCategory.LAUNCH_ACTION,
        SanitizationCategory.EXTERNAL_ACTION,
    )
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_outline_cycle_terminates_and_sanitizes() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_outline_cycle_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.LAUNCH_ACTION,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_form_field_actions_sanitized() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_form_field_js_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.JAVASCRIPT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        _assert_no_prohibited_content(out)


def test_af_reference_without_name_tree_sanitized() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_af_only_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.EMBEDDED_ATTACHMENT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        assert len(out.attachments) == 0
        assert not any(isinstance(obj, Dictionary) and Name.AF in obj for obj in out.objects)


def test_fileattachment_without_name_tree_sanitized() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_fileattachment_only_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.EMBEDDED_ATTACHMENT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        annots = out.pages[0].obj.get(Name.Annots)
        assert isinstance(annots, Array)
        assert Name.FS not in annots[0]


def test_malformed_attachment_tree_sanitized() -> None:
    # The name-tree key alone marks the document; the key is dropped even
    # though the mapping itself cannot enumerate anything.
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_malformed_attachment_tree_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.EMBEDDED_ATTACHMENT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        names = out.Root.get(Name.Names)
        assert not (isinstance(names, Dictionary) and Name.EmbeddedFiles in names)


def test_unexpected_engine_failure_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(pdf: pikepdf.Pdf) -> tuple[SanitizationCategory, ...]:
        raise RuntimeError("engine blew up")

    monkeypatch.setattr(sanitize_module, "_detect_categories", boom)
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_js_pdf_bytes())
    assert verdict.status is SanitizerStatus.REFUSED
    assert verdict.categories == ()
    assert sanitizer.output_bytes is None


def test_verification_reopen_failure_refuses_without_residual_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # F-2 regression: a verification re-open exception returned REFUSED while
    # leaving the partial 998-byte document on output_bytes (SEC-02: REFUSED
    # always has output_bytes None).
    real_open = pikepdf.Pdf.open
    calls = 0

    def flaky_open(
        source: str | Path | io.BytesIO,
        password: str = "",
        attempt_recovery: bool = False,
    ) -> pikepdf.Pdf:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise pikepdf.PdfError("verification reopen failed")
        return real_open(source, password=password, attempt_recovery=attempt_recovery)

    monkeypatch.setattr(pikepdf.Pdf, "open", staticmethod(flaky_open))
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_js_pdf_bytes())
    assert verdict.status is SanitizerStatus.REFUSED
    assert verdict.categories == ()
    assert sanitizer.output_bytes is None


def test_verification_detection_failure_refuses_without_residual_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # F-2 invariant, other verification leg: detection on the re-opened
    # output fails after the sanitized bytes were produced.
    real_detect = sanitize_module._detect_categories
    calls = 0

    def flaky_detect(pdf: pikepdf.Pdf) -> tuple[SanitizationCategory, ...]:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("verification detection blew up")
        return real_detect(pdf)

    monkeypatch.setattr(sanitize_module, "_detect_categories", flaky_detect)
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_js_pdf_bytes())
    assert verdict.status is SanitizerStatus.REFUSED
    assert verdict.categories == ()
    assert sanitizer.output_bytes is None


def test_unexpected_failure_emits_privacy_safe_structured_telemetry(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # The broad defensive catch must not swallow failures silently (F-2),
    # and its telemetry carries only closed category + exception class.
    def boom(pdf: pikepdf.Pdf) -> tuple[SanitizationCategory, ...]:
        raise RuntimeError("app.alert(1) at https://evil.example/x with secret payload")

    monkeypatch.setattr(sanitize_module, "_detect_categories", boom)
    sanitizer = PdfSanitizer()
    with caplog.at_level(logging.ERROR, logger="app.security.sanitize"):
        verdict = sanitizer.sanitize(_js_pdf_bytes())
    assert verdict.status is SanitizerStatus.REFUSED
    assert sanitizer.output_bytes is None
    records = [record for record in caplog.records if record.name == "app.security.sanitize"]
    assert len(records) == 1
    fields = records[0].__dict__.get("fields")
    assert isinstance(fields, dict)
    assert set(fields) == {"category", "error"}
    assert fields["category"] == ErrorCategory.ENGINE
    assert fields["error"] == "RuntimeError"
    emitted = records[0].getMessage() + repr(fields)
    for marker in _PAYLOAD_MARKERS:
        assert marker not in emitted


# --- preservation and freshness ---


def test_ordinary_page_content_preserved() -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_content_preserving_pdf_bytes())
    assert verdict.status is SanitizerStatus.SANITIZED
    assert verdict.categories == (SanitizationCategory.JAVASCRIPT,)
    output = sanitizer.output_bytes
    assert output is not None
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        assert len(out.pages) == 1
        contents = out.pages[0].obj.get(Name.Contents)
        assert contents is not None
        assert contents.read_bytes() == b"BT /F1 12 Tf 72 720 Td (Hello Papyr) Tj ET"
        _assert_no_prohibited_content(out)


def test_sanitized_output_is_fresh_in_memory_document(tmp_path: Path) -> None:
    sanitizer = PdfSanitizer()
    data = _kitchen_sink_pdf_bytes(tmp_path)
    verdict = sanitizer.sanitize(data)
    assert verdict.status is SanitizerStatus.SANITIZED
    output = sanitizer.output_bytes
    assert output is not None
    assert output != data
    with pikepdf.Pdf.open(io.BytesIO(output)) as out:
        assert len(out.pages) == 1


def test_sanitizer_reusable_across_calls(tmp_path: Path) -> None:
    sanitizer = PdfSanitizer()
    clean = sanitizer.sanitize(_blank_pdf_bytes())
    assert clean.status is SanitizerStatus.CLEAN
    js = sanitizer.sanitize(_js_pdf_bytes())
    assert js.status is SanitizerStatus.SANITIZED
    assert js.categories == (SanitizationCategory.JAVASCRIPT,)
    again = sanitizer.sanitize(_blank_pdf_bytes())
    assert again.status is SanitizerStatus.CLEAN
    assert sanitizer.output_bytes == _blank_pdf_bytes()


def test_refusal_clears_previous_output() -> None:
    sanitizer = PdfSanitizer()
    first = sanitizer.sanitize(_js_pdf_bytes())
    assert first.status is SanitizerStatus.SANITIZED
    assert sanitizer.output_bytes is not None
    refused = sanitizer.sanitize(_password_protected_pdf_bytes())
    assert refused.status is SanitizerStatus.REFUSED
    assert sanitizer.output_bytes is None


# --- payload privacy (DEC-175, DEC-169) ---


def test_payload_details_never_reported(tmp_path: Path) -> None:
    sanitizer = PdfSanitizer()
    verdict = sanitizer.sanitize(_kitchen_sink_pdf_bytes(tmp_path))
    strings = (
        str(verdict),
        repr(verdict),
        repr(verdict.status),
        repr(verdict.categories),
        str(verdict.status),
    )
    for marker in _PAYLOAD_MARKERS:
        assert marker not in "".join(strings)
