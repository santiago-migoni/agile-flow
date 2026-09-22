# Rendered editorial examples

These fifteen Markdown files demonstrate all eleven document formats, including all five story types. They were produced by the real CleanStore operations in an isolated synthetic Bookly project. They are presentation fixtures, not records of real product acceptance or execution.

Start with the [constitution](constitution.md), [roadmap](roadmap.md), [product backlog](backlog/product-backlog.md), [release](release/v0.1.0/release-0.1.0.md), [planning](release/v0.1.0/ITER-001/sprint-planning.md) and [summary](summary.md). The iteration includes a failed then passed check, a scoped partial review and a retrospective follow-up. Source documents distinguish actual fixture observations from missing information.

The fixture does not populate every optional field. Not recorded is deliberate; it never manufactures an owner, estimate, observed result or permission. Extra domain fields remain in Additional context. Header state is a refresh snapshot; acceptance remains scoped to the underlying sourced review.

Regenerate from the plugin directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tests/render_editorial_examples.py --output /tmp/agile-flow-editorial-examples
```

The generator creates product records only in an isolated temporary directory, then exports Markdown to the selected output directory. It does not export technical records, install a plugin, touch app-odoo or publish anything.
