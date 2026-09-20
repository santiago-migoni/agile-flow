# Readiness and quality

An increment is ready only with objective, included and excluded scope, observable criteria, required checks, dependencies or uncertainties, technical approach, and applicable authorization. Use the product quality policy when it exists; propose missing quality conditions proportionally.

An observed failed check on the current delivery or a sourced defect tied to an existing criterion or required check can justify `prepare-correction` under the existing authorization. Preserve failed evidence and increment identity, start the corrected delivery revision, and rerun affected checks. This is a technical correction, not a fabricated user change request.

Development, verification, and acceptance remain separate. `implemented` means changes are complete. Verification is `passed` only when every required current check passes; unavailable checks are `not_run` evidence and normally leave verification partial. A behavior-affecting change starts a new delivery revision and invalidates affected evidence and acceptance. Preserve historical records.

Before recording evidence, capture delivery scope and relevant file/dependency paths when observable; the program hashes listed paths. `inspect` compares them to current files and reports `effective_verification` and `stale_evidence` without rewriting history. Reassess affected checks and record a new delivery revision for behavior changes. Do not claim a command, test, or user review occurred unless it was actually observed.
