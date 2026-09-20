# Authorization

An authorization is a sourced user decision with `kind: authorization`, structured scope, reason, and date. The scope may cover listed `item_ids`, listed `increment_ids`, or the project explicitly. Technical, product, and priority decisions do not authorize development. Reuse an applicable authorization unless a later decision supersedes or revokes it. The record program validates structure and relationships; it cannot authenticate the source conversation. Do not broaden authorization from one increment to the backlog, from documentation to implementation, or from acceptance to publishing, deployment, installation, or unrelated external action.

When the bound authorization is revoked or superseded, record the actual replacement user authorization and use `rebind-authorization` on the existing increment with a reason and source provenance. The replacement must be sourced, current, and scoped to that increment. Rebinding preserves increment identity and history; it is not a new permission or a way to widen scope.

When a choice changes product behavior, scope, external cost, or commitment, explain the concrete impact and recommend an option before dependent work. Investigate missing technical details without turning the investigation into an unnecessary question.

Acceptance is a delivery-specific user decision. A plan approval is not delivery acceptance. Silence is not either.
