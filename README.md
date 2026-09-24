# Agile Flow marketplace

A Git-backed Codex marketplace containing **agile-flow**, a plugin for collaborative software development through small, verifiable increments with durable decisions, evidence, and user review.

## Install from GitHub

Register this marketplace:

```bash
codex plugin marketplace add https://github.com/santiago-migoni/agile-flow.git
```

Open Codex's Plugin Directory, choose the **Agile Flow** marketplace, and install **agile-flow**. Start a new task to use the installed skills. Git and Python 3.10 or later are required for the Git installation and local record CLI respectively. Private repositories require Git access to the repository.

For a local checkout, register the repository root instead:

```bash
codex plugin marketplace add /absolute/path/to/agile-flow
```

The catalog uses repository-relative paths and does not depend on a particular GitHub owner or repository name. See the [official packaging documentation](https://developers.openai.com/plugins/build/plugins) for marketplace distribution.

## Use

See the [plugin guide](plugins/agile-flow/README.md) for the consultative skills: discover, define, design, roadmap, release, sprint, backlog, implement, review, retrospective, status, and close. The initialize, plan and advance entries remain compatible. Product records live in the product's `.agile-flow/` directory, separate from the installed plugin.

The current source uses document schema 4 and the editorial-v2 codec: authored Markdown, release-owned iterations, typed US work records with per-story DoD, portable technical metadata and scoped Git commits. Start with the [documentation map](docs/README.md), [current rendered examples](docs/examples/editorial/README.md) and [compatibility and migration guide](plugins/agile-flow/references/migration.md).

Published versions and their stored formats are listed in that compatibility guide. Older records, including schema-4 clean-markdown-v1 documents, require explicit previewed conversion before using the current writer. Version 0.6.0 ships the editorial-v2 codec. Installing the plugin does not migrate product documents.

## Repository layout

- `.agents/plugins/marketplace.json`: repository marketplace catalog.
- `plugins/agile-flow/`: self-contained plugin source, runtime, references, and tests.
- `docs/`: project design and reference material, outside the installed plugin.

## Validate and package

Run from the repository root:

```bash
cd plugins/agile-flow
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/package_plugin.py
```

The ZIP is optional for GitHub installation. Codex resolves the catalog directly from the Git repository. Update the plugin manifest version for subsequent published releases so installed copies can distinguish versions.

## Release history

[GitHub Releases](https://github.com/santiago-migoni/agile-flow/releases) is the authoritative changelog. Each release describes the changes in its matching version tag.
