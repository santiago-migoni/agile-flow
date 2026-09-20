# Session protocol

Resolve the product root before acting. Read `.agile-flow/state.json` through the record program when it exists, inspect applicable repository instructions, and compare only relevant repository state.

For every mutation, obtain the current `revision` and `fingerprint` using `inspect`, then submit a JSON request with a unique `operation_id`, `expected_revision`, `expected_fingerprint`, and an English `purpose`. Reuse a lost operation ID only with identical content. Treat `conflict` and `failed` as unsaved; inspect and reconcile before retrying.

The record program is at `../scripts/agile_flow.py` relative to this references directory. Skills must resolve that location from their installed plugin root, not a personal path. Use `--root <product-root>`.

`status` is read-only unless the user explicitly asks to regenerate views. Never overwrite a modified generated view: first report it; `render --force` preserves a `.manual-backup` copy.

Record only observed evidence and actual user decisions. User quotes and external material remain verbatim; add a separately labeled English summary when useful.
