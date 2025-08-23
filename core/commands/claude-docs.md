---
description: Access Claude Code documentation using claude-code-docs
argument-hint: [search-query or topic]
---

# Claude Code Documentation Access

This command uses the `~/.claude-code-docs` installation to access Claude Code documentation.

## Usage
- `/claude-docs` - Show available documentation
- `/claude-docs [topic]` - Search for specific topic
- `/claude-docs what's new` - Show recent updates and changelog

## Execute Documentation Helper

```bash
# Check if claude-code-docs is installed
if [ ! -d "$HOME/.claude-code-docs" ]; then
    echo "❌ claude-code-docs is not installed!"
    echo "Install it from: https://github.com/ericbuess/claude-code-docs"
    exit 1
fi

# Run the documentation helper with any provided arguments
if [ -z "$ARGUMENTS" ]; then
    # No arguments - show main documentation menu
    bash ~/.claude-code-docs/claude-docs-helper.sh
else
    # Pass arguments to the helper script
    bash ~/.claude-code-docs/claude-docs-helper.sh "$ARGUMENTS"
fi
```

## Available Topics

The claude-code-docs system provides comprehensive documentation on:
- **Getting Started**: quickstart, overview, installation
- **Core Features**: memory, hooks, settings, commands
- **Integrations**: mcp, github-actions, ide-integrations
- **Advanced**: amazon-bedrock, google-vertex-ai, corporate-proxy
- **Development**: sdk, troubleshooting, monitoring-usage
- **Reference**: cli-reference, interactive-mode, slash-commands

## Quick Examples

```bash
/claude-docs memory          # Learn about memory management
/claude-docs hooks           # Understand hooks system
/claude-docs what's new      # See recent updates
/claude-docs mcp            # MCP server documentation
```

## Documentation Locations

- **Local Mirror**: `~/.claude-code-docs/docs/`
- **Official Docs**: https://docs.anthropic.com/en/docs/claude-code
- **Community Repo**: https://github.com/ericbuess/claude-code-docs