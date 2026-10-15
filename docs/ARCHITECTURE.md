# Architecture

## Design principles

1. **Fail closed:** invalid records stop analysis rather than being silently dropped.
2. **Deterministic:** the same bytes produce the same evidence ID and analytical result.
3. **Reconciled:** an explanation is incomplete until exposure-level effects equal the portfolio move.
4. **Reviewable:** calculation, validation, rendering, and input/output concerns stay separate.
5. **Local-first:** source data never leaves the machine running the command.

## Components

| Module | Responsibility |
|---|---|
| `io.py` | Schema/range validation, CSV loading, SHA-256 hashing |
| `models.py` | Immutable exposure and attribution records |
| `attribution.py` | Exact Shapley factor attribution and entry/exit treatment |
| `engine.py` | Portfolio aggregation, reconciliation, concentration, migrations |
| `report.py` | JSON, Markdown, and self-contained HTML evidence artifacts |
| `cli.py` | Stable command-line interface and exit behavior |

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Inputs valid and attribution reconciled |
| `1` | Analysis completed but attribution control failed |
| `2` | Input, validation, or filesystem error |

These codes allow CI pipelines to use Exposure Proof as a quality gate.
