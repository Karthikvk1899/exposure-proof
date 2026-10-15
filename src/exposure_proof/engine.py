from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal
from pathlib import Path

from .attribution import attribute_pair
from .io import file_sha256, load_portfolio
from .models import Exposure


def _sum(values: Iterable[Decimal]) -> Decimal:
    return sum(values, Decimal("0"))


def _concentration(portfolio: dict[str, Exposure], dimension: str) -> list[dict[str, str]]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    portfolio_ead = _sum(item.ead for item in portfolio.values())
    for item in portfolio.values():
        totals[getattr(item, dimension)] += item.ead
    rows = []
    for name, ead in sorted(totals.items(), key=lambda pair: pair[1], reverse=True):
        share = ead / portfolio_ead if portfolio_ead else Decimal("0")
        rows.append({"name": name, "ead": str(ead), "share": str(share)})
    return rows


def _hhi(rows: list[dict[str, str]]) -> Decimal:
    return _sum(Decimal(row["share"]) ** 2 for row in rows)


def compare_portfolios(baseline_path: Path, current_path: Path) -> dict[str, object]:
    baseline = load_portfolio(baseline_path)
    current = load_portfolio(current_path)
    ids = sorted(set(baseline) | set(current))
    details = [attribute_pair(key, baseline.get(key), current.get(key)) for key in ids]

    baseline_el = _sum(item.expected_loss for item in baseline.values())
    current_el = _sum(item.expected_loss for item in current.values())
    ead_effect = _sum(item.ead_effect for item in details)
    pd_effect = _sum(item.pd_effect for item in details)
    lgd_effect = _sum(item.lgd_effect for item in details)
    entry_exit = _sum(item.entry_exit_effect for item in details)
    explained = ead_effect + pd_effect + lgd_effect + entry_exit
    delta = current_el - baseline_el

    sector_rows = _concentration(current, "sector")
    country_rows = _concentration(current, "country")
    migration: dict[str, int] = defaultdict(int)
    for item in details:
        if item.status == "matched" and item.baseline_rating != item.current_rating:
            migration[f"{item.baseline_rating} -> {item.current_rating}"] += 1

    evidence_id = file_sha256(baseline_path)[:12] + "-" + file_sha256(current_path)[:12]
    return {
        "schema_version": "1.0",
        "evidence_id": evidence_id,
        "inputs": {
            "baseline": {"path": baseline_path.name, "sha256": file_sha256(baseline_path)},
            "current": {"path": current_path.name, "sha256": file_sha256(current_path)},
        },
        "summary": {
            "baseline_exposures": len(baseline),
            "current_exposures": len(current),
            "baseline_ead": str(_sum(item.ead for item in baseline.values())),
            "current_ead": str(_sum(item.ead for item in current.values())),
            "baseline_expected_loss": str(baseline_el),
            "current_expected_loss": str(current_el),
            "expected_loss_delta": str(delta),
            "ead_effect": str(ead_effect),
            "pd_effect": str(pd_effect),
            "lgd_effect": str(lgd_effect),
            "entry_exit_effect": str(entry_exit),
            "unexplained_residual": str(delta - explained),
        },
        "controls": {
            "input_validation": "PASS",
            "attribution_reconciliation": "PASS" if delta == explained else "FAIL",
            "baseline_rows_reconciled": len(baseline),
            "current_rows_reconciled": len(current),
        },
        "concentration": {
            "sector_hhi": str(_hhi(sector_rows)),
            "country_hhi": str(_hhi(country_rows)),
            "by_sector": sector_rows,
            "by_country": country_rows,
        },
        "rating_migrations": dict(sorted(migration.items())),
        "top_drivers": [
            item.as_dict()
            for item in sorted(details, key=lambda row: abs(row.delta_el), reverse=True)[:10]
        ],
        "attribution": [item.as_dict() for item in details],
    }
