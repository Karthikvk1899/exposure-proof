from __future__ import annotations

import csv
import hashlib
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Exposure

REQUIRED_COLUMNS = {
    "exposure_id",
    "counterparty",
    "sector",
    "country",
    "rating",
    "ead",
    "pd",
    "lgd",
}


class PortfolioValidationError(ValueError):
    """Raised when a portfolio cannot safely be analyzed."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_portfolio(path: Path) -> dict[str, Exposure]:
    errors: list[str] = []
    records: dict[str, Exposure] = {}

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            raise PortfolioValidationError(
                f"{path}: missing required columns: {', '.join(missing)}"
            )

        for row_number, row in enumerate(reader, start=2):
            exposure_id = (row.get("exposure_id") or "").strip()
            if not exposure_id:
                errors.append(f"row {row_number}: exposure_id is blank")
                continue
            if exposure_id in records:
                errors.append(f"row {row_number}: duplicate exposure_id '{exposure_id}'")
                continue

            try:
                ead = Decimal((row.get("ead") or "").strip())
                pd = Decimal((row.get("pd") or "").strip())
                lgd = Decimal((row.get("lgd") or "").strip())
            except InvalidOperation:
                errors.append(f"row {row_number}: ead, pd, and lgd must be numeric")
                continue

            if ead < 0:
                errors.append(f"row {row_number}: ead must be >= 0")
            if not Decimal("0") <= pd <= Decimal("1"):
                errors.append(f"row {row_number}: pd must be between 0 and 1")
            if not Decimal("0") <= lgd <= Decimal("1"):
                errors.append(f"row {row_number}: lgd must be between 0 and 1")

            dimensions = {}
            for column in ("counterparty", "sector", "country", "rating"):
                value = (row.get(column) or "").strip()
                if not value:
                    errors.append(f"row {row_number}: {column} is blank")
                dimensions[column] = value

            records[exposure_id] = Exposure(
                exposure_id=exposure_id,
                ead=ead,
                pd=pd,
                lgd=lgd,
                **dimensions,
            )

    if errors:
        detail = "\n  - ".join(errors[:25])
        suffix = f"\n  - ... and {len(errors) - 25} more" if len(errors) > 25 else ""
        raise PortfolioValidationError(f"{path}: validation failed:\n  - {detail}{suffix}")
    if not records:
        raise PortfolioValidationError(f"{path}: portfolio contains no data rows")
    return records
