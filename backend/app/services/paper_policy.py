from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum

_ISO_ALPHA2_LENGTH = 2


class PaperStandard(StrEnum):
    LETTER = "LETTER"
    A4 = "A4"


def is_valid_iso_alpha2(value: str) -> bool:
    return (
        len(value) == _ISO_ALPHA2_LENGTH
        and value.isascii()
        and value.isalpha()
        and value.upper() not in {"XX", "T1"}
    )


def select_paper(
    edge_country: str | None, *, valid_alpha2: Callable[[str], bool] = is_valid_iso_alpha2
) -> PaperStandard:
    country = (edge_country or "").strip().upper()
    if country in {"US", "CA"}:
        return PaperStandard.LETTER
    if country and valid_alpha2(country):
        return PaperStandard.A4
    return PaperStandard.A4
