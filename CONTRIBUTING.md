# Contributing

Contributions are welcome, especially around real-world edge cases that can be reproduced with
synthetic data.

## Before opening an issue

- Never attach confidential, regulated, or production portfolio data.
- Reduce the case to the smallest synthetic CSV that shows the behavior.
- State the expected reconciliation outcome and why.

## Local checks

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
exposure-proof compare examples/baseline.csv examples/current.csv --out artifacts
```

Changes to financial calculations require tests that prove the result and the reconciliation
invariant. Changes to the input contract require matching documentation updates.
