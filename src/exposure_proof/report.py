from __future__ import annotations

import html
import json
from decimal import Decimal
from pathlib import Path


def _money(value: object) -> str:
    return f"${Decimal(str(value)):,.2f}"


def write_json(result: dict[str, object], path: Path) -> None:
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(result: dict[str, object], path: Path) -> None:
    s = result["summary"]
    c = result["controls"]
    lines = [
        "# Exposure Proof",
        "",
        f"**Evidence ID:** `{result['evidence_id']}`",
        "",
        "## Executive answer",
        "",
        f"Expected loss moved from **{_money(s['baseline_expected_loss'])}** to "
        f"**{_money(s['current_expected_loss'])}**: a net change of "
        f"**{_money(s['expected_loss_delta'])}**.",
        "",
        "| Driver | Effect |",
        "|---|---:|",
        f"| EAD | {_money(s['ead_effect'])} |",
        f"| PD | {_money(s['pd_effect'])} |",
        f"| LGD | {_money(s['lgd_effect'])} |",
        f"| New / removed exposures | {_money(s['entry_exit_effect'])} |",
        f"| **Unexplained residual** | **{_money(s['unexplained_residual'])}** |",
        "",
        "## Control results",
        "",
        f"- Input validation: **{c['input_validation']}**",
        f"- Attribution reconciliation: **{c['attribution_reconciliation']}**",
        f"- Rows reconciled: {c['baseline_rows_reconciled']} baseline / "
        f"{c['current_rows_reconciled']} current",
        "",
        "## Largest exposure-level drivers",
        "",
        "| Exposure | Counterparty | Status | EL change | EAD | PD | LGD | Entry/exit |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["top_drivers"]:
        lines.append(
            f"| {row['exposure_id']} | {row['counterparty']} | {row['status']} | "
            f"{_money(row['delta_el'])} | {_money(row['ead_effect'])} | "
            f"{_money(row['pd_effect'])} | {_money(row['lgd_effect'])} | "
            f"{_money(row['entry_exit_effect'])} |"
        )
    lines.extend([
        "",
        "## Reproducibility",
        "",
        f"- Baseline SHA-256: `{result['inputs']['baseline']['sha256']}`",
        f"- Current SHA-256: `{result['inputs']['current']['sha256']}`",
        "- Monetary calculations use Python `Decimal`; attribution is exact Shapley "
        "decomposition across all six EAD/PD/LGD update orders.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html(result: dict[str, object], path: Path) -> None:
    s = result["summary"]
    effects = [
        ("EAD", Decimal(s["ead_effect"])),
        ("PD", Decimal(s["pd_effect"])),
        ("LGD", Decimal(s["lgd_effect"])),
        ("Entry / exit", Decimal(s["entry_exit_effect"])),
    ]
    maximum = max((abs(value) for _, value in effects), default=Decimal("1")) or Decimal("1")
    bars = "".join(
        f'<div class="bar-row"><span>{html.escape(label)}</span><div class="track">'
        f'<div class="bar {"up" if value >= 0 else "down"}" style="width:{float(abs(value) / maximum * 100):.1f}%"></div>'
        f'</div><strong>{_money(value)}</strong></div>'
        for label, value in effects
    )
    driver_rows = "".join(
        f"<tr><td>{html.escape(row['exposure_id'])}</td><td>{html.escape(row['counterparty'])}</td>"
        f"<td><span class='pill'>{html.escape(row['status'])}</span></td>"
        f"<td class='num'>{_money(row['delta_el'])}</td><td class='num'>{_money(row['pd_effect'])}</td></tr>"
        for row in result["top_drivers"]
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Exposure Proof · {html.escape(result['evidence_id'])}</title>
<style>
:root{{--ink:#172235;--muted:#65728a;--panel:#fff;--line:#dce3ed;--navy:#102a43;--cyan:#12b5cb;--coral:#f46b5f;--bg:#f3f6fa}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,Segoe UI,sans-serif}}
main{{max-width:1120px;margin:auto;padding:48px 24px}} .eyebrow{{letter-spacing:.12em;text-transform:uppercase;color:var(--cyan);font-weight:800}}
h1{{font-size:44px;line-height:1.05;margin:8px 0}} .lede{{color:var(--muted);font-size:18px;max-width:760px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:30px 0}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 8px 30px #102a430b}}
.label{{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.06em}} .metric{{font-size:30px;font-weight:800;margin-top:4px}} .pass{{color:#087f5b}}
.wide{{grid-column:span 2}} h2{{margin:0 0 18px}} .bar-row{{display:grid;grid-template-columns:90px 1fr 120px;align-items:center;gap:14px;margin:13px 0}} .track{{background:#edf1f6;border-radius:99px;height:16px;overflow:hidden}} .bar{{height:100%;border-radius:99px}} .up{{background:var(--coral)}} .down{{background:var(--cyan)}}
table{{border-collapse:collapse;width:100%}} th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left}} th{{color:var(--muted);font-size:12px;text-transform:uppercase}} .num{{text-align:right;font-variant-numeric:tabular-nums}} .pill{{background:#eaf7fa;color:#087487;padding:4px 9px;border-radius:99px;font-size:12px}}
footer{{color:var(--muted);margin-top:24px;font-size:13px;overflow-wrap:anywhere}} @media(max-width:760px){{.grid{{grid-template-columns:1fr}}.wide{{grid-column:auto}}h1{{font-size:34px}}.bar-row{{grid-template-columns:75px 1fr}}.bar-row strong{{grid-column:2}}}}
</style></head><body><main>
<div class="eyebrow">Credit portfolio movement intelligence</div><h1>Exposure Proof</h1>
<p class="lede">A deterministic answer to the question: why did expected loss move, and can every dollar be reconciled?</p>
<section class="grid">
<div class="card"><div class="label">Baseline expected loss</div><div class="metric">{_money(s['baseline_expected_loss'])}</div></div>
<div class="card"><div class="label">Current expected loss</div><div class="metric">{_money(s['current_expected_loss'])}</div></div>
<div class="card"><div class="label">Net movement</div><div class="metric">{_money(s['expected_loss_delta'])}</div></div>
<div class="card wide"><h2>What moved the book</h2>{bars}</div>
<div class="card"><h2>Control proof</h2><div class="label">Input validation</div><div class="metric pass">{result['controls']['input_validation']}</div><div class="label">Attribution reconciliation</div><div class="metric pass">{result['controls']['attribution_reconciliation']}</div><p>Residual: <strong>{_money(s['unexplained_residual'])}</strong></p></div>
</section>
<section class="card"><h2>Largest exposure-level drivers</h2><table><thead><tr><th>Exposure</th><th>Counterparty</th><th>Status</th><th class="num">EL change</th><th class="num">PD effect</th></tr></thead><tbody>{driver_rows}</tbody></table></section>
<footer>Evidence ID: {html.escape(result['evidence_id'])}<br>Baseline SHA-256: {result['inputs']['baseline']['sha256']}<br>Current SHA-256: {result['inputs']['current']['sha256']}</footer>
</main></body></html>"""
    path.write_text(document, encoding="utf-8")
