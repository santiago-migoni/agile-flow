# Clean Markdown and Git implementation

> Historical implementation or validation record. Its statements and results apply to the stage documented below; they do not describe every aspect of the current writer. Preserve the original decisions and evidence. See [current documentation](README.md) for maintained contracts and examples.

## Scope

Version 0.5.0 implements the approved clean Markdown and Git design as document schema 4. Publication does not install the plugin, change installed caches or migrate app-odoo.

## Document contract

The release/iteration/BL/US model is preserved. Current authored Markdown contains no private af comments. Executable Markdown templates control section order; JSON field grouping and portable structural schemas retain reliable reading. Tables tolerate spacing changes and additional homogeneous rows. Unknown Notes sections and author-created details blocks survive updates. Duplicate/missing structured headings and unresolved conflict markers stop writes.

All functional product meaning stays in Markdown. Technical identities, field schemas and operation receipts are stored in .internal/registry.json, format identity in manifest.json, and hash baselines in baselines/records.json. Project UUIDs and file hashes no longer clutter the documents. The project root is resolved from the actual checkout. Schema-4 metadata refers to technical records by stable record identity, avoiding evidence reassignment when records are reordered.

The reader reconstructs from current portable files. The local cache, locks, journals and backups are ignored under .internal/local/. Status does not rewrite documents or refresh that cache. Pending journals are bound to branch and HEAD; a changed checkout blocks replay. The historical writers refuse a schema-4 project.

## Git integration

The CLI adds git-status, git-init, git-preview and git-commit. It uses the enclosing repository, including nested product directories. Initialization requires its own sourced authorization. A visible set-git-policy operation records on-request or automatic coherent-outcome commits with the real user source.

Preview returns selected paths, hashes, tracked diffs and untracked text. Commit requires a fresh preview plus an explicit request source or an outcome covered by the policy. All changed portable Agile Flow files must be included together. Unrelated staged changes, ignored selected files, detached HEAD and merge conflicts are refused. Unrelated unstaged files remain outside the commit. Hooks run normally; failure preserves work and the index.

Automatic policy is implemented in the agent workflow at agreed outcomes, not as an implicit commit after every record write. Push, branch creation, tags and releases use normal Git tooling under separate authorization and the project's strategy. The helper does not infer ownership of mixed changes within a file; those require human/agent diff review before whole-file selection. Concurrent Git writers must finish before committing.

Commits do not grant execution, verification or acceptance. A later verification/review can reference an implementation commit; a document does not attempt to store its own commit SHA.

## Migration

Explicit preview/application supports schemas 1, 2 and 3. Earlier release assignments remain required. Conversion from older layouts is prepared in a temporary copy; preview does not mutate the real product. Schema-3 free notes and functional content are preserved while removing technical markers. No global backslash replacement is performed.

Application verifies source fingerprints and original-byte backups before a recoverable transaction. Previous current metadata is retired. Original records remain in ignored local backups. Valid draft planning hashes are translated across the format conversion; already stale plans remain stale. Existing delivery evidence and acceptance survive the conversion. Unresolved legacy mapping and manual-prose reconciliation remain explicit.

## Validation

The complete suite passed 120 tests: 95 retained tests plus 25 clean-format/Git scenarios. New coverage includes the full delivery/evidence/acceptance lifecycle, per-story DoD, all five work types, manual criteria rows and notes, duplicate headings, clone portability, read-only reconstruction, schema-1/2/3 migration, byte-preserving backups, interrupted writes, checkout changes, complete commit snapshots, stale previews, authorization policies, detached HEAD, failed hooks and nested products.

Plugin manifest validation and all six skill validations passed. The existing packaging tests remain part of the full suite. git diff --check is required before delivery.

An independent agent also completed an isolated booking scenario through manual criterion/note editing, plan update, validation and a scoped local commit. It verified no af comments, preservation of the note, 12 selected portable files, exclusion of local recovery data and a clean fixture Git status. The authorization was synthetic; this is behavioral workflow evidence, not acceptance of a real booking product.

See [generated examples](clean-markdown-example/README.md) and the [editing, migration and Git contract](../plugins/agile-flow/references/clean-markdown-and-git.md).

## Practical editing boundary

Free text, list entries and homogeneous table rows are editable directly. Adding new typed fields, renaming structured headings, changing complex snapshot shape or resolving identity collisions requires explicit reconciliation through the record operations and applicable references. A validation conflict preserves the files instead of guessing their meaning.
