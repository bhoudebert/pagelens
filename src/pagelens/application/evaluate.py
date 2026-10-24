from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from pagelens.domain.models import EvidenceMode, SearchResult

PageKey = tuple[str, int]


class EvaluationScenario(BaseModel):
    id: str
    text: str
    evidence: EvidenceMode = EvidenceMode.VISUAL
    relevant: list[PageKey]
    must_not_confirm: list[PageKey] = Field(default_factory=list)


class GroundTruth(BaseModel):
    schema_version: int
    queries: list[EvaluationScenario]


@dataclass(frozen=True, slots=True)
class ScenarioOutcome:
    scenario: EvaluationScenario
    matched: frozenset[PageKey]
    missing: frozenset[PageKey]
    forbidden: frozenset[PageKey]

    @property
    def passed(self) -> bool:
        return not self.missing and not self.forbidden


def load_ground_truth(path: Path) -> GroundTruth:
    try:
        return GroundTruth.model_validate_json(path.read_text())
    except (OSError, ValueError) as error:
        raise ValueError(f"invalid ground truth {path}: {error}") from error


def compare_results(
    scenario: EvaluationScenario,
    results: list[SearchResult],
    *,
    verified: bool,
) -> ScenarioOutcome:
    if verified:
        selected = {
            (result.source_path.name, result.page)
            for result in results
            if result.verification is not None and result.verification.status == "confirmed"
        }
    else:
        selected = {(result.source_path.name, result.page) for result in results}

    relevant = set(scenario.relevant)
    forbidden = set(scenario.must_not_confirm) & selected if verified else set()
    return ScenarioOutcome(
        scenario=scenario,
        matched=frozenset(relevant & selected),
        missing=frozenset(relevant - selected),
        forbidden=frozenset(forbidden),
    )
