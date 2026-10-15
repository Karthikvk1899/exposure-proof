from pathlib import Path

import pytest

from exposure_proof.io import PortfolioValidationError, load_portfolio

ROOT = Path(__file__).parents[1]


def test_duplicate_exposure_ids_fail_closed():
    with pytest.raises(PortfolioValidationError, match="duplicate exposure_id"):
        load_portfolio(ROOT / "examples/invalid_duplicate.csv")
