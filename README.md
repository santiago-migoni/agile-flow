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

See the [plugin guide](plugins/agile-flow/README.md) for the six skills: initialize, backlog, advance, review, status, and close. Product records live in the product's `.agile-flow/` directory, separate from the installed plugin.

Version 0.5.0 implements document schema 4: clean Markdown, release-owned iterations, typed US work records with per-story DoD, portable technical metadata and scoped Git commits. See [implementation evidence](docs/clean-markdown-git-implementation.md), [rendered examples](docs/clean-markdown-example/README.md) and [editing, Git and migration instructions](plugins/agile-flow/references/clean-markdown-and-git.md).

Existing 0.2.0, 0.3.0 and 0.4.0 projects require explicit previewed migration; installing the plugin does not migrate their documents.

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
