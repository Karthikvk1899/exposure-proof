from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class Exposure:
    exposure_id: str
    counterparty: str
    sector: str
    country: str
    rating: str
    ead: Decimal
    pd: Decimal
    lgd: Decimal

    @property
    def expected_loss(self) -> Decimal:
        return self.ead * self.pd * self.lgd


@dataclass(frozen=True)
class Attribution:
    exposure_id: str
    counterparty: str
    status: str
    baseline_el: Decimal
    current_el: Decimal
    delta_el: Decimal
    ead_effect: Decimal
    pd_effect: Decimal
    lgd_effect: Decimal
    entry_exit_effect: Decimal
    baseline_rating: str | None
    current_rating: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            key: str(value) if isinstance(value, Decimal) else value
            for key, value in asdict(self).items()
        }
