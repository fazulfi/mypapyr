from app.services.paper_policy import PaperStandard, select_paper

def test_policy() -> None:
    assert select_paper("US") is PaperStandard.LETTER
    assert select_paper("CA") is PaperStandard.LETTER
    assert select_paper("DE") is PaperStandard.A4
    assert select_paper(None) is PaperStandard.A4
