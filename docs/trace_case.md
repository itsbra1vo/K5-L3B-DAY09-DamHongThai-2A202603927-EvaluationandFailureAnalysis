# Trace case: the first incorrect decision and its regression test

## Reproduce

From `src/`, run:

```bash
python -m lab9.trace_case --shape seeded_regression --claim C-008 --seed 11
python -m lab9.trace_case --shape fixed --claim C-008 --seed 11
```

## Case

| Field | Evidence |
|---|---|
| Trial | `seeded_regression C-008@11`, run `E-seeded_regression-20261118-2bc9` |
| Symptom | The Lab 8 outcome grader passes and the ledger matches the expected 20,000 VND, but the reply claims 35,000 VND. `ReplyLedgerMatches` fails this trial. |
| First incorrect step | Event 3 (`quote`) proposes 35,000 VND; the expected and recorded refund is 20,000 VND. Events 1–2 hand off and read the order before this incorrect quote. |
| Visible consequence | Event 5 (`reply`) says “Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.” while the ledger contains 20,000 VND. |
| Failure modes | FM-04 (`sum_parts / round_down`) for the incorrect quote and FM-08 (`misreport`) for the reply/ledger mismatch. |
| Fixed control | On the same claim and seed, `fixed` replies with 20,000 VND; `ReplyLedgerMatches` passes. |
| Regression test | `test_seeded_regression_c008_misreport_is_caught` runs both shapes and asserts that the grader fails the regression and passes the fixed control. |
| Limit | The trace shows this deterministic public case only; it does not establish a real-world failure rate. |
