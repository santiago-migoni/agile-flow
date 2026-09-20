# Review and learning

Present the delivery objective, scope, change summary, checks with scope and limitations, and exactly what needs user review. Record acceptance, requested changes, deferral, or identified partial acceptance against the delivery revision and criterion parts. A review of an older revision remains historical. Partial acceptance records `accepted_parts`; it does not accept unidentified parts. Requested corrections use `prepare-correction` on the same increment, followed by `start`, implementation, and fresh checks.

A later user decision may explicitly withdraw a prior change request or accept its identified parts. Use `supersedes` entries naming the earlier review ID and exactly which criterion parts are withdrawn; the earlier review remains in history. A later acceptance without such supersession does not silently clear an outstanding change request on another part. A technical failure or documented defect can also reopen the same increment without fabricating a user review.

Keep corrections required by existing criteria on the increment. Record a new need separately and explain its impact before treating it as authorized scope. When a concrete observation supports it, record an improvement with an adjustment, target cycle, and observable effect. If no learning is identifiable, say so; do not fabricate a retrospective action.
