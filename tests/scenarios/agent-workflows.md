# Agent workflow scenarios

These are manual Codex skill scenarios, intentionally separate from deterministic CLI tests.

1. In a new empty temporary product, explicitly invoke `initialize` with a short need. Confirm it records facts, assumptions, open questions, a proposed first increment, and no code change.
2. In an existing temporary repository containing an instruction file, documentation, code, and a test, invoke `initialize` for a localized change. Confirm it distinguishes observed, documented, and unverified facts without modifying existing documents.
3. Invoke `backlog` with a duplicate need, a priority change during active work, and a documentation-only request. Confirm it preserves identity, asks only for ambiguous replacement/supplement intent, and starts no implementation.
4. Invoke `advance` under existing authorization, then with a new product rule. Confirm it advances the first and requests a decision for the second. Simulate an unavailable credential; confirm blocker and `not_run` evidence rather than a fabricated pass.
5. Invoke `review` with partial acceptance, a requested label correction, and a new feature request. Confirm scoped acceptance, correction linkage, and a separate new need.
6. Start a fresh conversation, invoke `status`, and confirm it reconstructs objective, states, blockers, decisions, and next step from records without inventing history. Confirm status itself does not change canonical revision.
7. Invoke `close` to pause active work, then resume it. Confirm the resumption point is retained and only affected evidence is reassessed after a behavior change.
