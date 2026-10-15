from decimal import Decimal
from pathlib import Path

from exposure_proof.engine import compare_portfolios

ROOT = Path(__file__).parents[1]


def test_example_portfolios_reconcile_to_zero_residual():
    result = compare_portfolios(ROOT / "examples/baseline.csv", ROOT / "examples/current.csv")
    assert result["controls"]["input_validation"] == "PASS"
    assert result["controls"]["attribution_reconciliation"] == "PASS"
    assert Decimal(result["summary"]["unexplained_residual"]) == 0


def test_new_and_removed_exposures_are_explicit():
    result = compare_portfolios(ROOT / "examples/baseline.csv", ROOT / "examples/current.csv")
    statuses = {row["exposure_id"]: row["status"] for row in result["attribution"]}
    assert statuses["EXP-008"] == "removed"
    assert statuses["EXP-009"] == "new"


def test_input_hashes_make_evidence_traceable():
    result = compare_portfolios(ROOT / "examples/baseline.csv", ROOT / "examples/current.csv")
    assert len(result["inputs"]["baseline"]["sha256"]) == 64
    assert len(result["evidence_id"]) == 25
