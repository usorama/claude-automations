# Claude Automations Project Overview

## Purpose
Comprehensive automation ecosystem built specifically for Claude Code CLI to provide safety nets, workflow automation, and intelligence augmentation.

## Key Components

### Git Intelligence (`git-intelligence/`)
- Smart commit message generation
- Repository state analysis
- Auto-commit and auto-push capabilities
- Pattern detection in development

### PRISM System (`prism/`)
- LLM-driven context optimization for Claude Code agents
- Manifest-based intelligence routing
- Learning from agent usage patterns
- SQLite database for context tracking

### Core Automation (`core/`)
- **Commands**: 101+ slash commands for Claude Code
- **Hooks**: 25+ event-driven automations
- **Agents**: Specialized development agents (BMAD, etc.)
- **Scripts**: Utility and deployment scripts

### Configuration (`config/`)
- Global settings for all subsystems
- Agent-specific configurations
- Hook configurations

## Critical Files
- `CLAUDE.md` - Project instructions and architecture
- `rules.md` - Mandatory AI development guidelines
- `docs/REALITY_CHECK.md` - Current system status
- `docs/DEPLOYMENT_GUIDE.md` - How to deploy features

## Current Status
- Commands: ✅ Working (101 installed)
- Hooks: ⚠️ Installed but not auto-triggering
- PRISM: ✅ Running but needs agent integration
- Git Intelligence: ✅ Working when called manually

## Integration Points
- Slash Commands: `/command` files in `~/.claude/commands/`
- Event Hooks: Python scripts in `~/.claude/hooks/`
- MCP Servers: PRISM available via MCP
- Agent Instructions: Via CLAUDE.md files

## Key Problems Being Solved
1. Never lose work (automatic checkpoints)
2. Quality maintenance (automatic validation)
3. Pattern detection (intelligent analysis)
4. Friction elimination (zero manual steps)
5. Context preservation (Claude-aware operations)