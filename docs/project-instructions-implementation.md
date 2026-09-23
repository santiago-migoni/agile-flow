# Project instructions and collaboration continuity

## Result and scope

The plugin now provides a project-root AGENTS.md template and a dedicated preview/apply command. The managed block coordinates roles, intent, deliverables, document ownership, uncertainty, verification and stopping rules. Instructions are in English; conversation follows the user. No live product, installed cache, release version, marketplace entry or publication was changed.

The collaboration contract preserves an unfinished request across clarifications, distinguishes release-definition readiness from planning and implementation readiness, supports grouped assessments, and requires correction of obsolete dependencies in source questions as well as summaries. Operation inclusion does not approve consequential behavior such as data loss. A bureaucracy correction removes inappropriate prerequisites without removing essential verification.

## Implementation map

- `plugins/agile-flow/templates/project-agents.md`: portable managed block, independent of product decisions and cache paths.
- `plugins/agile-flow/scripts/project_instructions.py`: source/template fingerprints, block checksum/version, read-only diff, explicit apply, cooperative locking, backups, atomic replacement and idempotence.
- `plugins/agile-flow/scripts/agile_flow.py`: `instructions` command, default preview and explicit apply.
- `plugins/agile-flow/references/project-instructions.md`: setup/adoption, preservation, recovery and actual Codex discovery.
- Macro workflow, collaboration/session/ownership/readiness references, roles and discover/define/design/plan/advance/status skills: consistent coordination.
- `plugins/agile-flow/tests/test_project_instructions.py`: storage, CLI, conflict and preservation scenarios.
- `plugins/agile-flow/tests/scenarios/project-collaboration.md`: conversational and fresh-discovery acceptance scenarios. Existing workflow scenarios were updated to stop requesting obsolete preparation documents or an automatic first increment.

## Adoption and preservation

New-product setup includes preview and application under the initialization mandate after meaningful product records are created. Existing products use an explicit instruction adoption/update request. Neither installation nor ordinary writes silently apply guidance. Status previews without writing. The record schema stays at 4; existing projects remain readable without AGENTS.md.

Only the managed block is replaceable. Other file bytes and permissions are preserved. Manual changes inside the block, malformed/duplicate delimiters, newer block versions, effective root overrides, symlink targets and stale fingerprints prevent writes. Overrides require explicit reconciliation rather than deletion. Backups preserve the complete prior AGENTS.md and prior existence. Apply has no force option. Git remains governed by the existing policy, with explicit selection of AGENTS.md and no automatic commit or publication.

The checksum detects edits, not semantic compatibility or authorization authenticity. Agents must review repository instructions and the cited user mandate. Cooperative locking cannot eliminate the last race with an unrelated editor that ignores locks; a second fingerprint check detects observed changes before replacement. Coordinate external edits during apply.

## Release outlines without numbering

The existing update-release writer requires a version identity. No schema expansion or invented version was introduced. Complete an unnumbered requested outline in product-design.md, explicitly propose numbering, and move concrete delivery ownership to the versioned release once identity is established. Preserve principal product agreements through references instead of creating competing documents. A draft, scope approval or number does not authorize implementation.

## Validation evidence

Final verification: 176 unittest cases passed (including 11 project-instruction tests); six changed skills passed quick_validate; 89 local reference links resolved; git diff --check passed. Package generation and existing regression checks passed within the suite.

Deterministic tests cover creation and read-only preview, idempotence, original bytes and permissions, backup recovery after interrupted replacement, manual edits, malformed/duplicate blocks, upgrades/downgrade refusal, stale source/template/override fingerprints, concurrent external edits, symlink boundaries, unchanged existing records, no Git initialization, and CLI use from an unrelated working directory. Package checks include the new script, template and reference. Skill frontmatter and referenced paths are validated separately.

An independent agent evaluated three response simulations using the changed instructions: release closure after an edition answer; integral assessment with obsolete CLI prerequisites and unresolved rollback semantics; and a workshop-booking scope closure with a pending cancellation policy. It produced completed outlines, preserved proposals and pending behavior, and did not infer implementation authority. Its review identified an inconsistent readiness sentence, which was corrected, and overly literal scenario wording, which was generalized. These are simulated responses with no product mutation, not end-to-end operation or statistical behavior tests. The third scenario used the same evaluator, so it is cross-domain evidence, not an independent sample.

Fresh automatic discovery was attempted using a generated AGENTS.md in a temporary fixture and an ephemeral read-only Codex run. The sandbox initially prevented startup. The permitted retry reached the service but failed because the installed CLI is too old for its configured model (gpt-5.6-sol). No model/configuration changes were made. Automatic instruction discovery and nested override precedence in a real fresh run therefore remain unverified; repeat the documented fixture after the CLI is compatible. File generation and simulated compliance must not be reported as a successful discovery test.

No migration was performed on app-odoo. Source changes are ready for review; publication and live adoption are separate steps.
