# Claude Automations Migration Plan

## Overview
This document outlines the migration of Claude Code customizations from `~/.claude/` to a git-controlled `~/claude-automations/` repository using symlinks.

## Goal
Separate Claude Code customizations from the core installation to:
- Survive Claude Code reinstalls
- Enable version control with git
- Allow easy deployment across machines
- Maintain all current functionality

## Architecture

### Repository Structure
```
~/claude-automations/
├── core/                    # All customizations
│   ├── agents/             # 90+ custom agents
│   ├── commands/           # 15+ slash commands
│   ├── hooks/              # 20+ automation hooks
│   ├── scripts/            # Utility scripts
│   ├── knowledge-base/     # Accumulated knowledge
│   └── templates/          # Project templates
├── config/                 # Configuration files
│   ├── settings.json       # Main Claude settings
│   └── environment/        # Environment-specific configs
├── deployment/             # Deployment automation
│   ├── deploy.sh          # Main deployment
│   ├── backup.sh          # Backup system
│   ├── restore.sh         # Restore system
│   └── sync.sh            # Git synchronization
└── docs/                  # Documentation
```

### Symlink Mapping
```
~/.claude/agents        → ~/claude-automations/core/agents
~/.claude/commands      → ~/claude-automations/core/commands  
~/.claude/hooks         → ~/claude-automations/core/hooks
~/.claude/scripts       → ~/claude-automations/core/scripts
~/.claude/knowledge-base → ~/claude-automations/core/knowledge-base
~/.claude/templates     → ~/claude-automations/core/templates
~/.claude/settings.json → ~/claude-automations/config/settings.json
```

## Migration Phases

### Phase 1: Test with Hooks (Current)
1. ✅ Create ~/claude-automations directory structure
2. ✅ Document migration plan (this file)
3. Backup ~/.claude/hooks to ~/.claude/hooks.backup
4. Move hooks to ~/claude-automations/core/hooks
5. Create symlink: ~/.claude/hooks → ~/claude-automations/core/hooks
6. Test Claude Code functionality
7. Verify all hooks work correctly

### Phase 2: Migrate Remaining Components
1. Backup all directories (agents, commands, scripts, etc.)
2. Move each to corresponding claude-automations location
3. Create symlinks for each
4. Test extensively
5. Verify Claude Code functionality

### Phase 3: Git Repository Setup
1. Initialize git repository in ~/claude-automations
2. Create .gitignore for sensitive data
3. Initial commit with all customizations
4. Add remote repository
5. Push to remote

### Phase 4: Create Automation Scripts
1. Deploy script for new machine setup
2. Backup script for safety
3. Restore script for rollback
4. Sync script for updates

## Testing Checklist

### Hook Testing
- [ ] notification_alert.py executes on Stop hook
- [ ] global-switch-processor.py processes UserPromptSubmit
- [ ] silent-failure-detector-hook.py runs on code edits
- [ ] statusline.sh displays correctly
- [ ] claude-docs-helper.sh processes Read operations
- [ ] session-lifecycle-manager.py handles sessions
- [ ] auto-checkpoint-hook.py creates checkpoints

### General Testing
- [ ] Claude Code starts without errors
- [ ] Settings are loaded correctly
- [ ] Hooks trigger as expected
- [ ] Agents are accessible
- [ ] Commands work properly
- [ ] Scripts execute correctly

## Rollback Plan

If issues occur at any phase:

1. **Immediate Rollback**:
   ```bash
   # Remove symlink
   rm ~/.claude/hooks
   # Restore backup
   mv ~/.claude/hooks.backup ~/.claude/hooks
   ```

2. **Full Restoration**:
   ```bash
   # Remove all symlinks
   find ~/.claude -type l -delete
   # Restore from backups
   for dir in hooks agents commands scripts; do
     mv ~/.claude/${dir}.backup ~/.claude/${dir}
   done
   ```

## Benefits

1. **Version Control**: Full git history and branching
2. **Portability**: Clone and deploy on any machine
3. **Safety**: Survives Claude Code reinstalls
4. **Collaboration**: Share customizations via git
5. **Rollback**: Easy recovery from any state

## Risk Assessment

**Low Risk (95% confidence)**:
- Symlinks are standard Unix feature
- Claude Code follows symlinks (tested)
- Easy rollback available
- No Claude Code modifications needed

**Potential Issues (5%)**:
- Future Claude versions might change behavior
- Enterprise policies might restrict symlinks
- Some edge cases not yet discovered

## Commands Reference

### Daily Operations
```bash
# Edit hooks (automatically in git repo via symlink)
vim ~/.claude/hooks/my-hook.py

# Commit changes
cd ~/claude-automations
git add .
git commit -m "Updated hook"
git push
```

### New Machine Setup
```bash
# Clone repository
git clone <repo-url> ~/claude-automations

# Run deployment
cd ~/claude-automations/deployment
./deploy.sh
```

### Synchronization
```bash
cd ~/claude-automations
git pull  # Get latest changes
git push  # Push local changes
```

## Success Criteria

Migration is successful when:
1. All hooks execute via symlinks
2. Claude Code operates normally
3. Changes in ~/claude-automations reflect in ~/.claude
4. Git tracks all customizations
5. Deployment works on fresh machine

## Timeline

- **Day 1** (Today): Test with hooks directory
- **Day 2-3**: If successful, migrate remaining components
- **Day 4**: Setup git repository and push
- **Day 5**: Create automation scripts
- **Day 6**: Test on secondary machine
- **Week 2**: Full production use

## Notes

- Keep backups for at least 30 days
- Document any issues discovered
- Update this plan as migration progresses
- Consider automating backup before Claude Code updates

---

**Last Updated**: August 23, 2025
**Status**: Phase 1 - Testing Hooks Migration
**Confidence**: 95% success probability