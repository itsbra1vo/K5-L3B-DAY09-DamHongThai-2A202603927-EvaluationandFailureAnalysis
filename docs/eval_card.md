# Eval card — LogiX-VN refund agent

## Provenance

- **Baseline:** `E-swarm-20261118-2bc9` · eval-set SHA `2bc991f9e760`
- **Variants:** `E-fixed-20261118-2bc9`, `E-seeded_regression-20261118-2bc9`
- **Code:** repository revision `37815f9` plus the M1–M4 working-tree changes present when reports were generated.
- **Metric spec:** v1.0 · eval set v1 (`data/eval/eval_set_v1.jsonl`) · Python 3.11.5 · MockLLM
- **Coverage:** 14 public items × seeds 11/22/33/44/55 = 70 trials per run; all three reports have zero evaluator failures.
- **Reproduce:** from `src/`, run `python -m lab9.eval --shape swarm --spec config/metric_spec.yaml --out reports/baseline_v1.json`, then repeat with `fixed` and `seeded_regression` as the shape and output filename.

## Results

| Shape | Run ID | approval_bypass | secret_leak | db_fact_kept | refund_amount_correct | reply_ledger_match | pass_rate | pass_5 | cost_per_success | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| swarm (baseline) | `E-swarm-20261118-2bc9` | 0 | 0 | 0.9857 | 0.9857 | 1.0000 | 0.9857 | 0.9286 | 49.5670 | Reference |
| fixed | `E-fixed-20261118-2bc9` | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 48.7157 | **Exit 0 — merge** |
| seeded_regression | `E-seeded_regression-20261118-2bc9` | 0 | 0 | 0.9286 | 0.8571 | 0.7857 | 0.7143 | 0.7143 | 81.2020 | **Exit 1 — blocked** |

Paired percentile bootstrap, 95% confidence, 1,000 resamples, RNG seed 2027; differences are variant minus baseline, paired by item:

| Variant | Metric | Δ | 95% CI |
|---|---|---:|---|
| fixed | pass_rate | +0.014 | [+0.000, +0.043] |
| fixed | refund_amount_correct | +0.014 | [+0.000, +0.043] |
| fixed | reply_ledger_match | +0.000 | [+0.000, +0.000] |
| seeded_regression | pass_rate | **−0.271** | **[−0.500, −0.057]** |
| seeded_regression | refund_amount_correct | −0.129 | [−0.315, +0.000] |
| seeded_regression | reply_ledger_match | −0.214 | [−0.429, +0.000] |

The regression gate blocks `refund_amount_correct`, `reply_ledger_match`, and `pass_rate`. In particular, `pass_rate` falls below its 0.85 floor and its paired CI is entirely below zero; the explicit expected regression verdict is exit 1 with `pass_rate` named.

## Judge calibration and trace evidence

- `tone_ok`: κ=0.757, precision=0.857, recall=0.800; it clears the audit floors for conditional tone review only.
- `helpful`: κ=0.375, precision=1.000, recall=0.300; excluded from the release gate because it misses most human-labelled failures.
- FM-08 trace: `seeded_regression C-008@11` reports 35,000 VND while the ledger records 20,000 VND; see [trace_case.md](./trace_case.md) and [judge_audit.md](./judge_audit.md).

## Decision, ownership, and limits

- **Decision:** this is a deterministic offline regression gate, not evidence that the agent is safe for live refunds.
- **Gate owner:** the fork's release/evaluation maintainer investigates a blocked PR; any waiver needs explicit product and evaluation-owner approval recorded in that PR.
- **Limits:** MockLLM and public fixtures only; 14 distinct items give a small paired-bootstrap sample even though there are 70 item-seed trials. The five fixed seeds cannot reliably detect bugs that appear in only one of three seeds. No new held-out human-labelled set or real-user performance has been measured. Cost is a harness estimate, not production spend.
- **Versioning:** adding or changing eval items requires a new eval-set version and a regenerated, committed baseline; changing metric definitions or thresholds requires a metric-spec version bump and documented rationale.

## Advanced/Expert v2

- **Eval set:** v2 contains the 14 v1 items plus 14 adversarial-pack claims (28 items × 5 seeds). Every mechanism in `fm_map.yaml` maps to an FM code; the v2 build/check reports 0 problems.
- **A/A noise:** alternate seeds `66,77,88,99,110` produce Δ = 0.0000 for every numeric metric on the deterministic MockLLM baseline. Real stochastic LLM runs may have a non-zero noise band, so `pass_hat_5` uses a 0.80 floor selected outside that band rather than tuning to individual variants.
- **Flakiness:** `pass_hat_5` is blocking in v2. It blocks `flaky_regression` together with `pass_rate` and prevents a 1/5-seed rounding defect from being averaged away.
- **Slice gates:** `money_movement/pass_rate` and `adversarial/pass_rate` are blocking. `slice_regression` remains 0.9357 overall on `pass_rate` but is blocked by `money_movement`; `adversarial` protects the held-out attack pack.
- **Integrity:** public traps for NaN grader values, dropped failing rows, cherry-picked seeds, and loosened specs are all blocked. The report manifest, `(item_id, seed)` coverage, grader failures, metric values, slice relabelling, and same-version ratchet are checked before normal thresholds run.
- **Limit:** one bug appearing in only 1/3 seeds is not reliably detectable with five fixed seeds; this capping is a sample-size limit, not a reason to lower thresholds. The MockLLM result does not measure live production traffic or human disagreement.
