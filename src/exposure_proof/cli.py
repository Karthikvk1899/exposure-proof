from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import compare_portfolios
from .io import PortfolioValidationError
from .report import write_html, write_json, write_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exposure-proof",
        description=(
            "Explain and reconcile expected-loss movement between two credit portfolio snapshots."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    compare = subparsers.add_parser("compare", help="compare baseline and current CSV snapshots")
    compare.add_argument("baseline", type=Path)
    compare.add_argument("current", type=Path)
    compare.add_argument("--out", type=Path, default=Path("artifacts"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = compare_portfolios(args.baseline, args.current)
    except (OSError, PortfolioValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    write_json(result, args.out / "evidence.json")
    write_markdown(result, args.out / "report.md")
    write_html(result, args.out / "report.html")
    summary = result["summary"]
    print(f"Evidence pack: {args.out.resolve()}")
    print(f"Expected-loss delta: {summary['expected_loss_delta']}")
    print(f"Unexplained residual: {summary['unexplained_residual']}")
    return 0 if result["controls"]["attribution_reconciliation"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
