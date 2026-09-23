# Executive-reading example

These are complete synthetic documents generated through real source-runtime transactions. No live product information is included. The fixture retains 21 settled design decisions, 14 proposed states and two additional architecture proposals. The summary is approximately 2 KB; detailed source documents remain available.

Start with [summary.md](summary.md), then follow its links to [constitution.md](constitution.md), [product-design.md](product-design.md), [architecture.md](architecture.md) and [the backlog need](backlog/BL-0001.md). Historical alternatives and operations use expandable sections. Agreement pointers keep the principal wording in the source decision.

The numbered configuration agreements intentionally create volume for readability evaluation; they are synthetic records, not a product proposal. No release, iteration or implementation authority is created.

Regenerate into an isolated output directory from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/examples/executive/generate.py --plugin plugins/agile-flow --output /tmp/agile-flow-executive-example
```

The script creates a temporary product, performs actual transactions and copies only Markdown into the requested output. Timestamps reflect generation time. These examples illustrate current source behavior, not the previously published plugin.
