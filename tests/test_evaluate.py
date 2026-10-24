from pathlib import Path
from typing import Literal

from pagelens.application.evaluate import EvaluationScenario, compare_results
from pagelens.domain.models import BoundingBox, SearchResult, Verification


def _result(
    pdf: str,
    page: int,
    status: Literal["confirmed", "rejected", "uncertain"] | None = None,
) -> SearchResult:
    verification = None
    if status is not None:
        verification = Verification(status=status, confidence=0.9)
    return SearchResult(
        region_id=f"{pdf}-{page}",
        source_path=Path(pdf),
        page=page,
        bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
        text="evidence",
        preview_path=Path("preview.jpg"),
        visual_score=0.8,
        verification=verification,
    )


def test_retrieval_evaluation_checks_recall_without_penalizing_candidates() -> None:
    scenario = EvaluationScenario(
        id="water-pump",
        text="water pump",
        relevant=[("manual.pdf", 2)],
        must_not_confirm=[("manual.pdf", 3)],
    )

    outcome = compare_results(
        scenario,
        [_result("manual.pdf", 2), _result("manual.pdf", 3)],
        verified=False,
    )

    assert outcome.passed
    assert not outcome.forbidden


def test_verified_evaluation_reports_missing_and_forbidden_confirmations() -> None:
    scenario = EvaluationScenario(
        id="water-pump",
        text="water pump",
        relevant=[("manual.pdf", 2), ("scan.pdf", 1)],
        must_not_confirm=[("manual.pdf", 3)],
    )

    outcome = compare_results(
        scenario,
        [_result("manual.pdf", 2, "confirmed"), _result("manual.pdf", 3, "confirmed")],
        verified=True,
    )

    assert not outcome.passed
    assert outcome.missing == frozenset({("scan.pdf", 1)})
    assert outcome.forbidden == frozenset({("manual.pdf", 3)})
