# Implementation deviations in the released study

The frozen preregistration and its five companion documents remain unchanged in [preregistration/](../preregistration/). This record describes the executed confirmatory study; it does not amend the plan, alter original observations, change primary estimands, or discard runs.

## Evidence feedback: at most five completed ticks

An implementation check on 2026-10-29 established that `src/v2/conditions.py` sets `EVIDENCE_WINDOW = 8`, but `src/v2/simulate.py::_history_for` passes only `HISTORY_K = 4` completed feature–return pairs. The audit appends the just-completed tick. The evidence builder therefore receives `min(t + 1, 5)` observations; applying its eight-tick cap cannot enlarge that input. No eight-observation table was delivered, and every table generated in the primary window (ticks 20–39) used five observations.

The offline reconstruction verifies all **8,721** persisted evidence-feedback instances against the recorded prompt text. In the primary window, the realized five-observation tables crossed regime changes in **294/718 DeepSeek audits (40.95%)** and **150/344 audits in each replication (43.60%)**. A nominal eight-tick recipe on the same audit coordinates would cross in **507/718 (70.61%)** and **249/344 (72.38%)**, respectively. This nominal comparison is counterfactual; it does not describe delivered feedback.

Primary prompts actually exposed to a mixed-regime table numbered **996/2,400 for DeepSeek (41.50%)** and **549/1,200 in each replication (45.75%)**. Table generation and prompt exposure have different denominators: feedback arrives after the audited action, and a final-tick audit has no later decision prompt.

The evidence-package estimates describe implemented feedback based on at most five ticks. They do not estimate the registered eight-tick intervention. Raw data, registered outcomes and confirmatory contrasts are retained. Full reconstruction, exposure counts and fixed-path price-impact diagnostics are in [the exploratory report](../data/v2/analysis/exploratory/report.md) and [analysis source](../src/v2/exploratory_analyses.py).

## Identical-prompt null re-asks: coordinate mask and invalid bases

The registered recipe samples a full 40 × 6 Bernoulli(0.20) null mask from `default_rng(seed * 1000 + 29)` and intersects it with the independent feature-probe mask. The implementation instead advances that RNG with a scalar draw only at feature-probe-selected coordinates, after the base response and regardless of its validity. The seed and nominal probability are the same, but RNG consumption produces a different realized coordinate mask. Across models, monitoring covered approximately 18.5–18.6% of probed decisions.

The implemented draw schedule is paired across packages and independent of response outcomes. The feature-probe mask and raw primary outcome definitions are unaffected. It nevertheless departs from the exact registered sampling recipe and affects protocol fidelity and the null diagnostic.

A selected invalid base also receives an identical-prompt null call and logs an undefined flip; Amendment 1 specified no null call for invalid bases. One selected invalid Haiku evidence base is recorded and excluded from the valid null denominator. Missing nulls never exclude otherwise eligible raw primary observations.

These null deviations were disclosed in [confirmatory results, Collection implementation deviations](confirmatory_results.md#deviations-and-incidents). The exploratory script reconstructs the implemented schedule from each seed and verifies its agreement with the stored masks. Original runs, the freeze marker and the six frozen documents are preserved; no collection was repeated to repair these deviations.
