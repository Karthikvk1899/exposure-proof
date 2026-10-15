from decimal import Decimal

from exposure_proof.attribution import shapley_attribution
from exposure_proof.models import Exposure


def exposure(ead: str, pd: str, lgd: str) -> Exposure:
    return Exposure(
        "1",
        "Counterparty",
        "Sector",
        "US",
        "BBB",
        Decimal(ead),
        Decimal(pd),
        Decimal(lgd),
    )


def test_shapley_effects_reconcile_exactly():
    old = exposure("100", "0.02", "0.4")
    new = exposure("130", "0.03", "0.5")
    effects = shapley_attribution(old, new)
    assert sum(effects.values()) == new.expected_loss - old.expected_loss


def test_single_factor_change_isolated():
    old = exposure("100", "0.02", "0.4")
    new = exposure("100", "0.04", "0.4")
    effects = shapley_attribution(old, new)
    assert effects["ead"] == 0
    assert effects["lgd"] == 0
    assert effects["pd"] == new.expected_loss - old.expected_loss
