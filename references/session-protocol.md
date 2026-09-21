# Session protocol

Resolve the product root before acting. Read `.agile-flow/state.json` through the record program when it exists, inspect applicable repository instructions, and compare only relevant repository state.

For every mutation, obtain the current `revision` and `fingerprint` using `inspect`, then submit a JSON request with a unique `operation_id`, `expected_revision`, `expected_fingerprint`, and an English `purpose`. Reuse a lost operation ID only with identical content. Treat `conflict` and `failed` as unsaved; inspect and reconcile before retrying.

The record program is at `../scripts/agile_flow.py` relative to this references directory. Skills must resolve that location from their installed plugin root, not a personal path. Use `--root <product-root>`.

`status` is read-only unless the user explicitly asks to regenerate views. `inspect` returns current and historical evidence, reviews, blockers, and improvement actions. Never overwrite a modified generated view: first report it; `render --force` preserves a uniquely named manual backup. After a mutation, check the returned `views` field: the canonical write can succeed even when view generation fails.

Generated views display the effective current verification and acceptance computed from the same canonical state and file fingerprints as `inspect`. Recorded historical states remain labeled as historical when they differ. After an external file change, do not treat a previous passed check or acceptance as current validity.

`inspect.active_increment` and view headers use the same active-development rule: open project, open increment, `in_progress`, and not suspended. Closed unfinished work retains its development state but is not active. `stale_evidence` includes historical attempts; use `current_stale_evidence` and each attempt's `current_attempt` marker to identify stale evidence still establishing a check.

Record only observed evidence and actual user decisions. User quotes and external material remain verbatim; add a separately labeled English summary when useful.
