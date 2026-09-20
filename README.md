# agile-flow

`agile-flow` is a local Codex skills plugin for delivering small, verifiable software increments while preserving decisions, evidence, and review across sessions.

It stores product records in `<product-root>/.agile-flow/`; it never stores product state in the plugin installation, creates commits, publishes, deploys, or installs itself.

## Use

Invoke one of the six skills in a Codex conversation:

- `initialize`: start a managed product or adopt an existing repository.
- `backlog`: capture, refine, deduplicate, or reprioritize needs.
- `advance`: prepare, implement, verify, or continue an authorized increment.
- `review`: record delivery-specific user feedback, acceptance, and learning.
- `status`: inspect records and repository differences without writing by default.
- `close`: pause, cancel, close, or reopen an increment or project.

The skills call `scripts/agile_flow.py` with JSON requests. The CLI is an internal interface, but can be inspected with `python3 scripts/agile_flow.py --help`.

## Local installation

Do not copy product records into the plugin. Codex installs local plugins from a marketplace. The following commands create a personal local copy and marketplace entry; run them yourself only when you want to install it:

```bash
mkdir -p "$HOME/plugins" "$HOME/.agents/plugins"
python3 /Users/santiago_migoni/Documents/Projects/agile-flow/scripts/package_plugin.py --output /private/tmp/agile-flow.zip
unzip -q /private/tmp/agile-flow.zip -d "$HOME/plugins/agile-flow"
cat > "$HOME/.agents/plugins/marketplace.json" <<'EOF'
{
  "name": "personal",
  "interface": {"displayName": "Personal"},
  "plugins": [
    {
      "name": "agile-flow",
      "source": {"source": "local", "path": "./plugins/agile-flow"},
      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
      "category": "Productivity"
    }
  ]
}
EOF
```

Restart Codex Desktop, open the Plugin Directory, select **Personal**, and install **agile-flow**. If `~/.agents/plugins/marketplace.json` already exists, merge the `agile-flow` entry instead of replacing its existing contents. Installation is intentionally not performed by this repository.

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 /Users/santiago_migoni/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 /Users/santiago_migoni/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/initialize
```

`scripts/package_plugin.py` creates a ZIP from the current directory and explicitly excludes `docs/agile-lledo.pdf`, product record folders, caches, and temporary files.
