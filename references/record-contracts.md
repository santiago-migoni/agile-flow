# Record contracts

`.agile-flow/state.json` is the sole canonical plugin record. Generated Markdown under `.agile-flow/views/` is a projection, not an editable authority. The program writes backups, uses a same-directory temporary file followed by atomic replacement, locks cooperating writers, and validates schema, references, operation IDs, revisions, fingerprints, and the single-active-increment rule.

Supported mutations are `initialize`, `update-backlog`, `record-decision`, `prepare`, `start`, `mark-implemented`, `record-evidence`, `record-review`, `record-blocker`, `record-improvement`, `mark-delivery-change`, `pause`, `close`, and `reopen`. `mark-delivery-change` is the explicit internal operation that creates a later delivery revision and preserves prior evidence.

Manual state or generated-view edits stop mutation until reconciled. Explicit recovery requires `recover`, preserving the damaged state file; it never silently restores a backup.
