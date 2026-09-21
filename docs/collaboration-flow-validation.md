# Collaboration flow validation

The plugin now defines reviewable outcomes for understanding, prioritization, preparation, development, and review. All six skills load the same collaboration reference. Product context separates users, sourced confirmed facts, assumptions, and proposals. A non-executable preparation proposal can be recorded before development authorization; normal increment preparation and execution retain their authorization checks.

Generated vision and preparation views expose the product context, planning scope, exclusions, criteria, checks, technical approach, and open decisions. Backlog and increment views now expose their detail. Existing authored documents remain in place, and new generated view names cannot silently overwrite unmanaged files. Existing records remain readable without migration.

Validation:

- Complete automated suite: 51 tests passed, including previous audit regressions, packaging, new collaboration views, correction history, authorization boundaries, and unmanaged-view preservation.
- Four collaboration tests rerun after the final heading-layout adjustment: passed.
- Plugin manifest and all six skills validated; all referenced resource paths resolve; git diff whitespace check passed.
- Independent forward test used the actual CLI in a temporary Odoo PaaS product. Seven initial mutations generated readable views and validated at revision 7. No development increments, implementation authorizations, or acceptance reviews were created. A same-server/no-SSH clarification was preserved in product facts, proposal, and backlog.
- Inspection of the generated output led to two refinements: hierarchical Markdown headings and explicit guidance against treating optional future expansion as a blocking decision. Product success criteria must describe user value rather than completion of planning.

The independent rerun reached revision 9 with generated views, product-outcome success criteria, no blocking question about future multiple environments, hierarchical headings, and still no execution authorization or increment.

This is bounded behavioral evidence, not a guarantee across all conversations. The remote app-odoo project and installed plugin cache were not modified. No commit, release, or installation was performed for this change.
