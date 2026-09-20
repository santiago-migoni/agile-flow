# agile-flow Implementation Audit

**Date:** September 20, 2026.  
**Scope:** Read-only comparison of implementation with the approved vision, functional specification, and plugin design. No spec-flow workflow was used.  
**Verdict:** The package structure is present, but the implementation does not yet satisfy the approved complete development/review/adaptation cycle.

## Evidence and Method

Inspected the six skills, shared references, record program, packaging script, README, manifest, tests, and scenario checklist in `/Users/santiago_migoni/Documents/Projects/agile-flow`.

Executed:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 13 tests passed.
- Local plugin manifest validation: passed.
- Local skill validation: all six passed.
- Seven independent reproduction cases using disposable temporary products: confirmed the failures below.

Tests used temporary products. The package test wrote its ZIP under `/private/tmp`. No project source, installed plugin, marketplace, or live product records were changed. No actual Codex skill execution or installation was performed; the scenario checklist is not execution evidence.

Paths and line numbers below refer to the inspected project. P1 means a core correctness or continuity defect; P2 means an important reliability or usability defect.

## Findings

### A01 — P1: An old delivery review can accept the current delivery

**Location:** `scripts/agile_flow.py:270-275`.

The request payload can override the automatically assigned `delivery_revision` because `**data` is expanded last. The program then updates the increment's current acceptance directly from the decision without checking which delivery was reviewed.

**Reproduction:** Advance `INC-0001` to delivery revision 2, then record an accepted review explicitly targeting revision 1. The operation returns `applied`, the stored review refers to revision 1, and revision 2 becomes `accepted`.

**Impact:** Violates F07 and the requirement that acceptance applies to the evaluated delivery. An obsolete approval can conceal outstanding review of changed behavior.

**Required correction:** Validate reviewed revision and identified scope; preserve historical reviews without applying them to current acceptance. Derive acceptance from reviews covering the current revision and parts. Add rejection/retention tests for stale reviews and partial coverage.

### A02 — P1: Requested adjustments cannot reenter the development lifecycle

**Location:** `scripts/agile_flow.py:252-260,270-275,286-301`.

A review requesting changes leaves development at `implemented`. `mark-delivery-change` resets verification and acceptance but does not reopen development. `reopen` changes administrative fields only. `start` accepts only `ready`; `mark-implemented` also rejects an already implemented increment. No supported mutation updates/reprepares an existing increment.

**Reproduction:** Implement an increment, request changes, record a delivery change, and attempt `start`. It fails with `Only a ready, authorized increment can start.`

**Impact:** F07's correction-on-the-same-increment workflow is unavailable through supported operations. Performing corrections outside the lifecycle also bypasses active-work tracking.

**Required correction:** Add an explicit correction/repreparation transition for the same increment, with delivery revision, authorization, and active-work rules. Test a full implementation → requested changes → correction → reverification → acceptance loop.

### A03 — P1: A technical decision is accepted as authorization for unrelated work

**Location:** `scripts/agile_flow.py:240-255`.

Preparation checks only that a decision ID exists. Decision author, kind, scope, and supersession are not used to determine whether it authorizes this increment. The record program need not authenticate a conversation, but it can and should enforce structured distinctions that are already available.

**Reproduction:** Record an agent-authored technical choice scoped to `unrelated`; reference it when preparing a feature. Both preparation and start return `applied`.

**Impact:** The program does not enforce the approved distinction between a decision and an applicable user authorization. Correct behavior depends entirely on the agent avoiding structurally invalid combinations.

**Required correction:** Model authorization explicitly, reference observed source, and validate covered work and revocation/supersession. Technical decisions must not satisfy authorization checks. Preserve the distinction between structural validation and authentication of source truth.

### A04 — P1: History does not preserve replaced values

**Location:** `scripts/agile_flow.py:175,228-239`.

History stores an operation name, purpose, time, request digest, and result metadata, but not the previous/new values or request content. Updating a backlog item overwrites its former purpose, priority, and provenance. A digest cannot reconstruct that information; the rolling backup retains only one previous state.

**Reproduction:** Create an item with purpose `Original need`, then update it to `Replaced need`. `Original need` no longer appears anywhere in canonical state.

**Impact:** Violates the approved relevant-change history and traceability requirements. Decisions and previous work context cannot be reconstructed after subsequent updates.

**Required correction:** Store structured relevant field changes with before/after values, reason, and provenance in the same transaction. Test multiple updates and recovery without relying on the single backup.

### A05 — P1: Essential record lifecycle operations are missing

**Location:** `scripts/agile_flow.py:224-304`; `initial_state` at lines 186-199.

The mutation interface can append blockers and improvements but cannot update or resolve existing ones. It cannot update project context or `next_step`, complete a backlog item, or cancel an increment/project through the advertised close workflow. Backlog updates explicitly omit its state field. Improvement follow-up cannot update the original action. Canonical manual edits are rejected, so they are not a supported fallback.

**Reproduction:** Record `BLK-0001`, then request a resolution operation: `Unsupported operation: resolve-blocker.` Inspection confirms no alternative branch updates a blocker. Likewise, the initial `next_step` has no update path.

**Impact:** F05, F08, F09, and F10 cannot maintain an accurate durable state through normal use. Resolved blockers remain open; completed needs remain open; the next step remains its initial value.

**Required correction:** Complete lifecycle operations for existing records with stable IDs, history, and validation. Include cancellation, context/next-step updates, blocker resolution, and improvement follow-up. Verify that status after a complete cycle contains no falsely open work.

### A06 — P2: Idempotent replay returns a fingerprint that never matched committed state

**Location:** `scripts/agile_flow.py:164-179,197-198`.

The result fingerprint is computed while history contains `result_fingerprint: pending`, then inserted into the history that participates in the fingerprint itself. The normal response recomputes after that insertion; replay returns the earlier stored value.

**Reproduction:** Apply a decision and replay exactly the same request before any further mutation. Status is correctly `already_applied`, but its fingerprint differs from the initial response and current state. The same construction affects initialization.

**Impact:** Clients using replay metadata for the next optimistic write receive a conflict despite no intervening mutation. The lost-response recovery contract is inconsistent.

**Required correction:** Separate response receipts from fingerprinted content, or define fingerprint exclusions consistently. Test that initial result, replay result, and committed-state metadata agree for the same revision.

### A07 — P1: Recovery accepts a manually altered backup and does not use transaction locking

**Location:** `scripts/agile_flow.py:347-352`.

Recovery validates only the backup's structural schema. It never verifies its stored integrity fingerprint; `write` then generates a new valid fingerprint, effectively accepting unacknowledged changes. Recovery also bypasses the transaction lock and uses a fixed damaged-state filename.

**Reproduction:** Alter `project.name` in the backup without updating its integrity metadata, then run `recover`. It returns `applied` and restores the altered value as valid canonical state.

**Impact:** Recovery can restore an invalid backup as trusted state. The missing lock additionally permits interference with a cooperating mutation. The tampered-backup case was executed; concurrent recovery was identified statically, not stress-tested.

**Required correction:** Validate backup integrity before modifying canonical state, lock recovery, preserve uniquely named damaged snapshots, and test invalid backups and interrupted recovery.

### A08 — P2: Shared skill references do not resolve as written

**Location:** `skills/advance/SKILL.md:8`, with the same pattern in the other skills.

Only the first shared reference includes `../../references/`. Subsequent names such as `authorization.md` and `record-contracts.md` are bare relative paths and do not exist alongside the skill file. They exist under the shared references directory.

**Impact:** An agent resolving relative references against the skill directory encounters missing files or must infer an undocumented base. The package test only checks for the presence of one `../../references/` string and misses the defect.

**Required correction:** Use an explicit correct relative path for every shared reference, or unambiguously declare a shared base. Validate every referenced file from the installed layout and another working directory.

### A09 — P2: Installation instructions overwrite an existing personal marketplace

**Location:** `README.md:24-44`.

The copyable command uses `cat > "$HOME/.agents/plugins/marketplace.json"`, replacing the entire file. The instruction to merge if the file exists appears after the destructive command block and is not implemented by it.

**Impact:** Following the advertised installation sequence can remove existing marketplace entries. No installation commands were executed during this audit.

**Required correction:** Provide an existence-aware merge procedure or the supported creation/update helper, preserve other entries, and remove hard-coded personal source paths from portable instructions.

## Additional Validation Gaps

- Evidence invalidation is explicit and agent-driven; the program never compares recorded product fingerprints to the repository. The skills request comparison, but no executed agent scenario demonstrates that it occurs. Unit tests exercise only a manually requested `mark-delivery-change`, not discovery of a changed file.
- Partial reviews are not aggregated by identified parts. `partial` always becomes `changes_requested`, even if no correction was requested; no test checks part-level coverage.
- `inspect` omits evidence and reviews, while skills instruct the agent to recover those details through inspection. Raw JSON can be read separately, but the documented normal interface does not provide the promised complete view.
- The manual-state conflict message asks for reconciliation, but no supported import/reconciliation operation accepts reviewed edits. Backup restoration is not equivalent to preserving and incorporating intended edits.
- The scenario file lists seven manual scenarios without execution results. There is no evidence here of end-to-end skill selection or a complete live agent journey.

These gaps should be addressed or explicitly tested before claiming complete functional compliance. They are not claims that every related behavior necessarily fails in an actual model session.

## Coverage Assessment

| Capability | Audit assessment |
| --- | --- |
| F01-F02 | Skill guidance and initialization exist; actual agent journeys unverified |
| F03 | Basic creation/update exists; prior values and item completion are incomplete |
| F04 | Basic preparation exists; authorization applicability is not enforced |
| F05 | Start/implementation and blocker creation exist; correction and blocker resolution incomplete |
| F06 | Check-result aggregation exists; real fingerprint reassessment unverified |
| F07 | Review recording exists; stale acceptance and correction lifecycle fail |
| F08 | Improvement creation exists; updating follow-up is missing |
| F09 | Read-only inspection exists; context updates and complete evidence/review retrieval incomplete |
| F10 | Pause/close/reopen partially exist; cancellation and correction resumption incomplete |

## Recommended Completion Order

1. Repair delivery acceptance, correction transitions, and applicable authorization (A01-A03).
2. Complete record lifecycle and preserve change history (A04-A05).
3. Correct transaction replay and recovery (A06-A07).
4. Fix shared references and installation procedure (A08-A09).
5. Execute full new/existing-project agent scenarios, including resumption, partial acceptance, changed-file detection, correction, blocker resolution, and learning follow-up.

Passing the current 13 tests and structure validators establishes a valid starting package, not completion of the approved product behavior.
