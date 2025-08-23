# Automation Activation Checklist

## ❌ What We Built But Never Activated:

### 1. Auto-Checkpoint System
**Built:** `auto-checkpoint-hook.py`
**Status:** EXISTS but NEVER RUNNING
**Should have:** 
- Started daemon on system startup
- Added to `.bashrc` or `.zshrc`
- Created systemd/launchd service
**Result:** 528 uncommitted changes accumulated

### 2. Manifest Generation
**Built:** `pre-agent-context.py`, `generate-manifests.ts`
**Status:** Only runs on manual trigger
**Should have:**
- File watcher triggering updates
- Git hooks auto-running
- Scheduled cron job
**Result:** Manifests went stale

### 3. GitHub Actions Integration
**Built:** Workflows, templates
**Status:** Never installed in projects
**Should have:**
- Auto-installed in every project
- `/install-github-app` run automatically
- Verification that `@claude` works
**Result:** No automation in virtual-tutor

### 4. Git Hooks
**Built:** Multiple hooks in `.claude/hooks/`
**Status:** Not symlinked to actual git hooks
**Should have:**
- Automatic installation script
- Symlinks created on project init
- Verification hooks are active
**Result:** Hooks never triggered

## ✅ What SHOULD Be Done Automatically:

### On First Claude Code Use in Project:
```bash
#!/bin/bash
# This should run automatically when claude enters a project

PROJECT_DIR=$(pwd)

# 1. Check if automation is set up
if [[ ! -f "$PROJECT_DIR/.claude/automation-active" ]]; then
    echo "🚀 Setting up automation for this project..."
    
    # 2. Install GitHub App
    claude /install-github-app
    
    # 3. Create CLAUDE.md with automation rules
    cat > CLAUDE.md << 'EOF'
# Project Automation Rules

## Auto-Commit Strategy
- Commit every 30 minutes if changes exist
- Commit after 50 file changes
- Create PR after 10 commits

## Manifest Updates
- Update on every file change
- Preserve manual additions
- Track version history
EOF
    
    # 4. Install git hooks
    for hook in ~/.claude/hooks/*.py; do
        hook_name=$(basename "$hook" .py)
        ln -sf "$hook" ".git/hooks/$hook_name"
    done
    
    # 5. Start checkpoint daemon
    nohup python3 ~/.claude/hooks/auto-checkpoint-hook.py --daemon &
    
    # 6. Start file watcher for manifests
    nohup python3 ~/.claude/automation/manifest-watcher.py &
    
    # 7. Mark as active
    echo "$(date)" > "$PROJECT_DIR/.claude/automation-active"
    
    echo "✅ Automation activated!"
fi

# Always verify automation is running
if ! pgrep -f "auto-checkpoint-hook.py" > /dev/null; then
    echo "⚠️ Checkpoint daemon not running - starting..."
    nohup python3 ~/.claude/hooks/auto-checkpoint-hook.py --daemon &
fi
```

## 🔍 The Health Check We Never Built:

```bash
#!/bin/bash
# Should run on every Claude Code startup

echo "🏥 Claude Code Health Check"

# Check checkpoint daemon
if pgrep -f "auto-checkpoint-hook.py" > /dev/null; then
    echo "✅ Checkpoint daemon running"
else
    echo "❌ Checkpoint daemon NOT running"
    echo "   Fix: python3 ~/.claude/hooks/auto-checkpoint-hook.py --daemon"
fi

# Check GitHub Actions
if [[ -f ".github/workflows/claude.yml" ]]; then
    echo "✅ GitHub Actions configured"
else
    echo "❌ GitHub Actions NOT configured"
    echo "   Fix: claude /install-github-app"
fi

# Check uncommitted changes
CHANGES=$(git status --porcelain 2>/dev/null | wc -l)
if [[ $CHANGES -gt 50 ]]; then
    echo "⚠️ WARNING: $CHANGES uncommitted changes!"
    echo "   Fix: claude /commit"
fi

# Check manifest freshness
for manifest in .claude/manifests/*.json; do
    if [[ -f "$manifest" ]]; then
        AGE=$(( ($(date +%s) - $(stat -f %m "$manifest")) / 86400 ))
        if [[ $AGE -gt 7 ]]; then
            echo "⚠️ Manifest stale: $(basename $manifest) ($AGE days old)"
        fi
    fi
done
```

## 🎯 The Root Cause:

**We built tools but no activation system.** Like building a car but never turning on the engine.

## 🔧 The Permanent Fix:

Create a master activation script that:
1. **Auto-runs on Claude Code startup**
2. **Checks all automation is active**
3. **Alerts when things aren't working**
4. **Self-heals when possible**
5. **NEVER allows silent failures**