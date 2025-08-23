# Remaining Items in ~/.claude to Migrate

## 🚀 High Priority (Should Migrate)

### 1. **Automation Directory** (`~/.claude/automation/`)
- Real-time monitoring system
- Smart manifest updater
- Auto-fix scripts
- Start/stop automation controls
- **Why migrate**: Core automation functionality

### 2. **Startup Directory** (`~/.claude/startup/`)
- Auto-activation scripts
- Silent failure prevention
- **Why migrate**: Critical for Claude Code initialization

### 3. **Process Templates** (`~/.claude/process-templates-n-prompts/`)
- Silent failure detection templates
- Process automation prompts
- **Why migrate**: Referenced by hooks

### 4. **Knowledge Base** (`~/.claude/knowledge-base/`)
- Accumulated learning
- Pattern recognition data
- **Why migrate**: Valuable accumulated knowledge

### 5. **MCP Servers** (`~/.claude/mcp-servers/`)
- Model Context Protocol configurations
- Server definitions
- **Why migrate**: MCP integration configs

### 6. **Templates** (`~/.claude/templates/`)
- Project templates
- Boilerplate code
- **Why migrate**: Reusable components

### 7. **Installation Scripts**
- `install-to-project.sh` - Deploy to new projects
- `bmad-knowledge-bridge.sh` - BMAD integration
- `knowledge-migration-script.sh` - Knowledge transfer
- **Why migrate**: Deployment automation

### 8. **MCP Management Scripts**
- `mcp-admin.sh`
- `mcp-validator.sh`
- `mcp-migration-orchestrator.sh`
- `mcp-monitoring-automation.sh`
- `mcp-security-hardening.sh`
- `secure-mcp-setup.sh`
- `validate-mcp-config.sh`
- **Why migrate**: MCP infrastructure management

### 9. **Archon Integration**
- `archon-sync.sh`
- `archon-doc-sync.py`
- `archon-integration.py`
- `setup-archon-cron.sh`
- **Why migrate**: Documentation sync system

### 10. **Status Line Scripts**
- `statusline.sh` (main - already referenced in settings.json)
- `statusline-ultra.sh`
- `statusline-advanced.sh`
- `statusline-ccusage.sh`
- **Why migrate**: UI customization options

## 📊 Medium Priority (Consider Migrating)

### 11. **BMAD Core** (`~/.claude/.bmad-core/`)
- BMAD methodology resources
- **Consider**: If actively using BMAD

### 12. **Manifests** (`~/.claude/manifests/`)
- Project manifests
- **Consider**: Project-specific, may want in git

### 13. **IDE Configs** (`~/.claude/ide/`)
- IDE integration settings
- **Consider**: If using IDE integrations

## ⏸️ Low Priority (Probably Skip)

### 14. **Logs** (`~/.claude/logs/`)
- Runtime logs
- **Skip**: Transient data

### 15. **Todos** (`~/.claude/todos/`)
- Task tracking
- **Skip**: Active working data

### 16. **Shell Snapshots** (`~/.claude/shell-snapshots/`)
- Shell state captures
- **Skip**: Debug/diagnostic data

### 17. **Downloads** (`~/.claude/downloads/`)
- Downloaded files
- **Skip**: Temporary storage

### 18. **Statsig** (`~/.claude/statsig/`)
- Analytics/metrics
- **Skip**: Runtime data

### 19. **Migration Staging** (`~/.claude/migration-staging/`)
- Temporary migration files
- **Skip**: One-time use

## 📝 Files to Consider

### Config Files
- `settings.json` - Main settings (HIGH PRIORITY)
- `settings.local.json` - Local overrides
- `.archon-sync-state.json` - Archon state

### Documentation
- Various .md files - Could be useful reference

## 🎯 Recommended Migration Order

1. **settings.json** - Critical configuration
2. **automation/** - Core automation systems
3. **startup/** - Initialization scripts
4. **process-templates-n-prompts/** - Hook dependencies
5. **knowledge-base/** - Accumulated knowledge
6. **Installation scripts** - Deployment tools
7. **MCP scripts** - If using MCP
8. **Statusline variants** - UI options
9. **templates/** - Reusable components
10. **mcp-servers/** - MCP configs

## 📦 Estimated Additional Items

- **Directories**: 7-10 more directories
- **Scripts**: 20+ executable scripts
- **Config Files**: 3-5 configuration files
- **Total Files**: ~100-150 additional files

## 🔧 Migration Strategy

### Phase 1: Critical Systems
- settings.json
- automation/
- startup/
- process-templates-n-prompts/

### Phase 2: Tools & Scripts
- All installation scripts
- MCP management scripts
- Archon integration
- Statusline variants

### Phase 3: Knowledge & Templates
- knowledge-base/
- templates/
- mcp-servers/
- manifests/

### Phase 4: Cleanup
- Remove migrated items
- Update any hardcoded paths
- Test everything works

## ⚠️ Path Dependencies to Check

Some scripts may have hardcoded paths to `~/.claude/`. After migration, these would need updating to use symlinks or new paths.

---

**Recommendation**: Start with Phase 1 (Critical Systems) as these are most important for daily Claude Code operation.