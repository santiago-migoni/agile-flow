# Session protocol

Resolve and state the actual product checkout before acting. Read applicable repository instructions. Use the installed plugin's `scripts/agile_flow.py --root <absolute-product-root>`; request files in temporary storage are transport only. Never edit the installed cache, or initialize a temporary directory as the user's product.

Run `inspect` to reconstruct the project from authored Markdown and observe relevant product files. It is read-only. Read the relevant authored documents as well, including free notes and files listed in `document_changes`; structured inspect output is not a substitute for the full prose. Existing schema-1, schema-2 or schema-3 records, and schema-4 clean-markdown-v1 records, require explicit migration before using the current writer; consult [compatibility and migration](migration.md). Do not auto-migrate a live project. No product-root AGENTS.md is required.

Before each mutation, obtain the current `revision` and `fingerprint`, then send a JSON request with `operation`, a unique `operation_id`, `purpose`, `expected_revision`, and `expected_fingerprint`. Initialization does not require expected values. Reuse a lost operation ID only with identical content. Failed/conflicting requests have not committed; interrupted transactions require explicit `recover`.

Authored Markdown is the functional authority. Preserve manual prose and validate its structured fields. `document_changes` reports edits since the last transaction. Compare them with the user's intent. Only `backlog/product-backlog.md` and `summary.md` are generated. Reconcile edits there into source documents before `render --force`; force preserves a uniquely named backup under `.internal/local/backups/manual/` but does not interpret the edit or authorize work.

Successful mutations update authored documents and indexes through one recoverable transaction. Inspect the actual readable result, not just the success response. A pending transaction blocks reading partially committed records until recovery. Status never refreshes documents automatically.

Use `effective_verification`, `effective_acceptance`, `active_increment`, and `current_stale_evidence` for current status. Recorded values may be historical. Product-file changes can stale evidence even when record documents have not changed. Preserve exact user quotations; plugin-authored prose is English, conversation follows the user's language.

For clean format and Git operations, read [clean Markdown and Git](clean-markdown-and-git.md). A fingerprint includes the Git checkout anchor. Pending journals cannot replay across a changed branch or HEAD. Local cache is not an authority; read commands reconstruct without writing it.
