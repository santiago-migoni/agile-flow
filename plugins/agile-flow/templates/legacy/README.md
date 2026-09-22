# Legacy template compatibility

These assets support existing record formats and explicit migration. They do not define the current editorial presentation.

| Asset | Consumer | Responsibility |
| --- | --- | --- |
| `documents.json` | `scripts/template_documents.py` | Field grouping for typed Markdown and the legacy clean codec. |
| `clean-markdown-v1/*.md` | `scripts/clean_markdown.py::render_v1` | Historical clean-Markdown titles and section order, retained for compatibility fixtures. |

Current templates live in [../markdown/](../markdown/); see the [presentation contract](../README.md). The legacy directory names describe compatibility, not a new persistent schema or codec. Moving these assets does not migrate any product.
