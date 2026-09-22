# Clean Markdown and Git contract

Version 0.5.0 uses document schema 4. Version 0.4.0 uses schema 3. Installing the plugin does not automatically migrate product records.

## Document authority

Constitution, roadmap, BL needs, releases and iteration US records keep the existing release layout. Each US owns criteria and DoD. Readable Markdown owns all product meaning and decisions. No af comments are emitted. Read the documents themselves, including additional notes, before deciding what work is authorized.

Templates in templates/markdown/ drive titles and section order. The JSON layout describes field grouping. Portable registry schemas describe field keys, heading paths and types. They do not contain a duplicate editable product. Technical baseline hashes and identity metadata live in .internal/baselines/records.json. Do not hand-edit schemas to invent evidence or acceptance.

Existing text, list entries and homogeneous table rows may be edited directly. Table spacing is flexible; maintain headers and condition IDs. Extra Notes headings and prose survive updates. New field types or complex record entries use the operation API. Missing, duplicated or renamed structured headings cause a conflict. Nested snapshots use readable field/value tables; structural edits there require reconciliation. Escaped source content is not automatically rewritten.

Only summary.md and backlog/product-backlog.md are generated. Preserve and reconcile edits before render --force, which saves originals under .internal/local/backups/manual/.

## Portable and local control

Version the Markdown, .internal/manifest.json, .internal/registry.json and .internal/baselines/. Ignore .internal/local/: its state cache, locks, journals and backups are recovery facilities, not functional authority. Initialization writes a scoped .agile-flow/.gitignore. An existing repository ignore rule that hides .agile-flow must be reconciled explicitly before versioning; do not force-add ignored files.

Read operations reconstruct the current checkout without updating the local cache. Branch/HEAD changes invalidate mutation fingerprints. A pending transaction is bound to its original checkout and cannot replay after a branch or commit change. Restore that checkout with user changes preserved, or deliberately reconcile the journal; never discard records or reset the repository to make recovery pass.

Duplicate identities and merge conflicts require resolution before new writes. Do not automatically renumber competing records: preserve both intentions and update their references deliberately. Git history preserves committed snapshots; local journals recover uncommitted interrupted writes.

## Git policy and operations

Use the enclosing project repository, including when the product lives in a subdirectory. No nested repository is created. Before modifying records inspect git-status and applicable project guidance. There is no mandatory branching strategy.

Record a sourced policy using mutate operation set-git-policy, with policy.commits=on-request or automatic, policy.outcomes listing authorized outcome names for automatic commits, and source containing the actual user instruction. The policy remains visible in the constitution. Commit authorization never grants branch creation, push, tags, release, deployment or destructive Git permission. Use normal Git tools for those actions only when separately authorized.

At a coherent outcome (agreed planning, verified implementation, recorded review or migration), validate the records and relevant code, inspect the diff and call:

- git-status: read-only repository, branch, HEAD, pending changes and conflicts.
- git-preview: request paths as explicit product-relative files. Returns hashes, tracked diff and untracked text. Review binary evidence separately. Include all changed portable Agile Flow files in one snapshot.
- git-commit: same paths, expected_fingerprint from preview, message, and either authorization_source from an explicit request or outcome covered by the recorded automatic policy.
- git-init: authorization_source required; initialize only if no enclosing repository exists.

Pass JSON through --request or stdin, using the same scripts/agile_flow.py --root entrypoint. Git commands do not require record operation_id/revision. They return separate Git outcomes and do not alter acceptance or create a reference to their own SHA.

Commit coherent results, not every field mutation. Automatic mode means the agent performs preview and commit at the agreed outcome; individual record writes never create commits implicitly. Include only authorized files. If a selected file mixes unrelated changes, separate them after review or ask for clarification; whole-file selection is not semantic proof of ownership. Unrelated staged changes block the helper and remain untouched. Concurrent Git writers must finish before commit. Hooks execute normally; failure preserves files and the index for inspection. Inspect Git before retrying an uncertain result.

Reference an implementation commit in later verification/review documentation when useful. A commit is not verification, passing tests are not user acceptance, and a tag is not deployment. Push and release remain distinct user-authorized operations.

## Migration

Use migrate --dry-run with the current source. Schema-1/2 conversions are prepared in an isolated temporary copy; the real product remains unchanged during preview. Existing iteration/release mapping requirements still apply. Schema-3 documents are converted directly, preserving structured content and free notes. No blanket removal of backslashes is performed.

Review the returned changes, source fingerprint, mappings and unresolved items. Apply with expected_source_fingerprint only under migration authorization. Verified original-byte backups are saved under .internal/local/backups/migration-*. The recoverable journal retires previous current metadata and writes the new registry. Valid draft hashes are translated across the format-only change; already stale plans remain stale. Historical acceptance and evidence retain their meaning.

Validate, review the actual documents and compare before/after meaning. If Git is enabled, prepare a dedicated migration commit according to the agreed policy, without unrelated development. Keep the original backups until reconciliation and acceptance are complete.
