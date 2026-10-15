from __future__ import annotations

from itertools import permutations

from .models import Attribution, Exposure

FACTORS = ("ead", "pd", "lgd")


def _value(values: dict[str, object]):
    return values["ead"] * values["pd"] * values["lgd"]


def shapley_attribution(baseline: Exposure, current: Exposure) -> dict[str, object]:
    """Exact, order-independent EAD/PD/LGD attribution over all 3! paths."""
    old = {factor: getattr(baseline, factor) for factor in FACTORS}
    new = {factor: getattr(current, factor) for factor in FACTORS}
    path_totals = {factor: baseline.ead * 0 for factor in FACTORS}

    for order in permutations(FACTORS):
        state = old.copy()
        previous = _value(state)
        for factor in order:
            state[factor] = new[factor]
            changed = _value(state)
            path_totals[factor] += changed - previous
            previous = changed
    effects = {factor: total / 6 for factor, total in path_totals.items()}
    # Rational Shapley values may repeat in base 10. Assign only that Decimal
    # representation residue to the largest effect so efficiency remains exact.
    target_delta = current.expected_loss - baseline.expected_loss
    closure = target_delta - sum(effects.values())
    if closure:
        closure_factor = max(FACTORS, key=lambda factor: abs(effects[factor]))
        effects[closure_factor] += closure
    return effects


def attribute_pair(
    exposure_id: str,
    baseline: Exposure | None,
    current: Exposure | None,
) -> Attribution:
    if baseline is None and current is not None:
        zero = current.ead * 0
        return Attribution(
            exposure_id, current.counterparty, "new", zero, current.expected_loss,
            current.expected_loss, zero, zero, zero, current.expected_loss,
            None, current.rating,
        )
    if current is None and baseline is not None:
        zero = baseline.ead * 0
        return Attribution(
            exposure_id, baseline.counterparty, "removed", baseline.expected_loss, zero,
            -baseline.expected_loss, zero, zero, zero, -baseline.expected_loss,
            baseline.rating, None,
        )
    assert baseline is not None and current is not None
    effects = shapley_attribution(baseline, current)
    zero = baseline.ead * 0
    return Attribution(
        exposure_id, current.counterparty, "matched", baseline.expected_loss,
        current.expected_loss, current.expected_loss - baseline.expected_loss,
        effects["ead"], effects["pd"], effects["lgd"], zero,
        baseline.rating, current.rating,
    )
