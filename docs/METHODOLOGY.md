# Methodology

## Objective

Exposure Proof attributes the change in expected loss between two portfolio snapshots. It is designed
for movement explanation and reconciliation, not model estimation or credit decisioning.

## Measure

For exposure `i`:

```text
EL_i = EAD_i × PD_i × LGD_i
```

Portfolio expected loss is the sum of exposure expected losses.

## Matched exposures

For exposures present in both snapshots, three inputs may change simultaneously. Sequentially
substituting inputs creates interaction terms whose allocation depends on substitution order.

The engine removes that ordering choice by evaluating every permutation of `(EAD, PD, LGD)`. For
each permutation, it records the marginal expected-loss change when a factor is replaced by its
current value. A factor's final effect is its average marginal contribution across the six paths.

This is the exact Shapley value for the three-factor multiplicative expected-loss function. The three
effects therefore satisfy efficiency: their sum equals the exposure's expected-loss change.

## Portfolio entry and exit

- An exposure appearing only in the current snapshot contributes its full current expected loss to
  the entry/exit effect.
- An exposure appearing only in the baseline snapshot contributes the negative of its baseline
  expected loss to the entry/exit effect.

This treatment keeps churn visible rather than assigning a new position's expected loss to arbitrary
factor changes.

## Arithmetic and reconciliation

Numeric inputs are parsed as base-10 `Decimal` values. No business-level rounding is applied inside
the engine. If an exact rational Shapley share has a repeating base-10 representation, its Decimal
representation residue is assigned deterministically to the largest factor effect. This closure is
below displayed precision and preserves the Shapley efficiency identity exactly in emitted
arithmetic. Displayed values may be formatted to two decimal places, while the JSON artifact retains
the exact decimal string.

The portfolio control is:

```text
unexplained residual = current EL - baseline EL
                     - EAD effect - PD effect - LGD effect - entry/exit effect
```

The attribution reconciliation passes only when the residual is exactly zero.

## Concentration

Current EAD is aggregated by sector and country. Herfindahl–Hirschman Index is calculated as the sum
of squared group shares. The tool reports the value without interpreting institutional thresholds;
thresholds differ by portfolio, policy, and jurisdiction.

## Limitations

- The input PD and LGD values are accepted after range validation; the engine does not validate the
  models that produced them.
- EAD, PD, and LGD must use compatible units and definitions across snapshots.
- Currency conversion is not implemented in v0.1.0.
- Guarantees, collateral, netting, wrong-way risk, maturity, discounting, and regulatory capital are
  outside the current scope.
- Rating labels are treated as categorical values; the engine does not infer upgrade/downgrade order.
