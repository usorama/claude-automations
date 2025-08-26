# 📦 DEPLOYMENT GUIDE: Making Claude Automations Actually Work

**Purpose**: Step-by-step guide to deploy claude-automations features to real projects  
**Problem**: Features exist but don't run automatically in your projects

## 🎯 The Core Problem

You have sophisticated automation that doesn't automate because:
1. **Hooks don't trigger** - Claude Code's event system isn't well documented
2. **No project integration** - Features aren't deployed to actual projects
3. **No observability** - Can't see what's running or failing
4. **Systems isolated** - PRISM, git automation, etc. don't work together

## 🚀 Quick Start: Deploy to Any Project

### Step 1: Add Git Hooks to Your Project

```bash
# Navigate to your project (e.g., virtual-tutor)
cd ~/Projects/virtual-tutor

# Create git hooks directory if missing
mkdir -p .git/hooks

# Create post-commit hook for auto-push
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Auto-push after commit
git push origin $(git branch --show-current) 2>/dev/null &
EOF

chmod +x .git/hooks/post-commit

# Create prepare-commit-msg hook for smart commits
cat > .git/hooks/prepare-commit-msg << 'EOF'
#!/bin/bash
# Use claude-automations smart commit
python3 ~/claude-automations/git-intelligence/src/quick_commit.py "$1"
EOF

chmod +x .git/hooks/prepare-commit-msg
```

### Step 2: Add Auto-Commit Cron Job

Since Claude Code hooks aren't triggering, use cron:

```bash
# Add to crontab (runs every 30 minutes)
crontab -e
# Add this line:
*/30 * * * * cd ~/Projects/virtual-tutor && ~/claude-automations/scripts/auto_commit.sh
```

Create the auto-commit script:

```bash
cat > ~/claude-automations/scripts/auto_commit.sh << 'EOF'
#!/bin/bash
# Auto-commit script for projects

PROJECT_DIR="${1:-$(pwd)}"
cd "$PROJECT_DIR" || exit 1

# Check for changes
if [ $(git status --porcelain | wc -l) -gt 0 ]; then
    # Stage all changes
    git add -A
    
    # Generate smart commit message
    COMMIT_MSG=$(python3 ~/claude-automations/git-intelligence/src/quick_commit.py 2>/dev/null || echo "WIP: Auto-commit $(date '+%Y-%m-%d %H:%M')")
    
    # Commit
    git commit -m "$COMMIT_MSG"
    
    # Push
    git push 2>/dev/null
    
    echo "[$(date)] Auto-committed changes in $PROJECT_DIR" >> ~/.claude/auto_commit.log
fi
EOF

chmod +x ~/claude-automations/scripts/auto_commit.sh
```

### Step 3: Enable PRISM for Your Project

```bash
# Navigate to project
cd ~/Projects/virtual-tutor

# Create PRISM manifest
cat > .prism-manifest.json << 'EOF'
{
  "project": "virtual-tutor",
  "description": "AI-powered tutoring application",
  "key_files": [
    "src/components/",
    "src/services/",
    "README.md",
    "package.json"
  ],
  "ignore": [
    "node_modules/",
    ".next/",
    "*.log"
  ]
}
EOF

# Register with PRISM (if database worked)
python3 ~/claude-automations/prism/src/manifest_updater.py .
```

### Step 4: Add Project-Specific CLAUDE.md

```bash
cat > CLAUDE.md << 'EOF'
# Project: Virtual Tutor

## Auto-Commit Rules
- Commit every 30 minutes if changes exist
- Use descriptive commit messages
- Push to remote automatically

## Key Files
- src/components/ - React components
- src/services/ - Backend services
- src/hooks/ - Custom React hooks

## Development Workflow
1. Changes are auto-committed every 30 minutes
2. Smart commit messages via git-intelligence
3. Auto-push to remote after commits
EOF
```

## 🔧 Fix Common Issues

### Issue: Auto-commit not working

**Solution 1**: Use git hooks instead of Claude hooks
```bash
# In your project directory
echo '#!/bin/bash
# Auto-commit on file save
if [ $(git status --porcelain | wc -l) -gt 0 ]; then
    git add -A
    git commit -m "WIP: $(date)"
fi' > .git/hooks/post-checkout

chmod +x .git/hooks/post-checkout
```

**Solution 2**: Use file watchers
```bash
# Install fswatch (macOS)
brew install fswatch

# Watch and auto-commit
fswatch -o . | xargs -n1 -I{} ~/claude-automations/scripts/auto_commit.sh
```

### Issue: PRISM not collecting context

**Solution**: Manually create database
```bash
# Create PRISM database
cd ~/claude-automations/prism/database
sqlite3 prism.db < schema.sql

# Add initial data
sqlite3 prism.db << 'EOF'
INSERT INTO manifests (agent_id, agent_type, file_path, content, metadata)
VALUES ('default', 'general', 'README.md', 'Project context', '{}');
EOF
```

### Issue: Hooks not triggering in Claude Code

**Solution**: Add logging to debug
```bash
# Add to any hook file
echo "[$(date)] Hook triggered: $0" >> ~/.claude/hook_debug.log
```

## 📋 Complete Deployment Checklist

### For Each Project:

- [ ] **Git Hooks**
  ```bash
  ls -la .git/hooks/
  # Should have: post-commit, prepare-commit-msg
  ```

- [ ] **Cron Jobs**
  ```bash
  crontab -l | grep auto_commit
  # Should show scheduled auto-commits
  ```

- [ ] **CLAUDE.md**
  ```bash
  [ -f CLAUDE.md ] && echo "✅ Present" || echo "❌ Missing"
  ```

- [ ] **PRISM Manifest**
  ```bash
  [ -f .prism-manifest.json ] && echo "✅ Present" || echo "❌ Missing"
  ```

- [ ] **Test Auto-Commit**
  ```bash
  echo "test" > test.txt
  ~/claude-automations/scripts/auto_commit.sh .
  git log -1 # Should show auto-commit
  ```

## 🚨 Critical: Making Hooks Actually Work

### The Truth About Claude Code Hooks

Claude Code hooks in `~/.claude/hooks/` need specific triggers:
1. They must be executable (`chmod +x`)
2. They need specific naming conventions
3. They may need manual triggering

### Working Alternative: System Integration

Instead of relying on Claude Code's event system:

1. **Use git hooks** (`.git/hooks/`) - Proven to work
2. **Use cron jobs** - Reliable time-based triggers
3. **Use file watchers** - React to file changes
4. **Use CI/CD** - GitHub Actions, etc.

## 🎯 Minimal Working Setup

For immediate results in any project:

```bash
#!/bin/bash
# quick_deploy.sh - Deploy essentials to a project

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

# 1. Git hook for auto-push
echo '#!/bin/bash
git push &' > .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# 2. Cron for auto-commit (every 30 min)
(crontab -l 2>/dev/null; echo "*/30 * * * * cd $PWD && git add -A && git commit -m 'Auto-commit' && git push") | crontab -

echo "✅ Deployed to $PROJECT_DIR"
echo "   - Auto-push after commits"
echo "   - Auto-commit every 30 minutes"
```

## 📊 Monitoring Your Deployment

### Check If Working:

```bash
# Check recent auto-commits
git log --grep="Auto-commit\|WIP" --oneline -10

# Check cron logs
grep CRON /var/log/syslog | tail -20  # Linux
log show --predicate 'subsystem == "com.apple.cron"' --last 1h  # macOS

# Check hook logs
tail -f ~/.claude/auto_commit.log
```

### Add Observability:

```bash
# Create monitoring script
cat > ~/claude-automations/scripts/monitor.sh << 'EOF'
#!/bin/bash
echo "=== Claude Automations Monitor ==="
echo "Last auto-commit: $(git log --grep='Auto-commit' -1 --format='%ar')"
echo "Uncommitted files: $(git status --porcelain | wc -l)"
echo "PRISM status: $(curl -s localhost:8080/health || echo 'Not running')"
echo "Hooks triggered today: $(grep "$(date +%Y-%m-%d)" ~/.claude/hook_debug.log 2>/dev/null | wc -l)"
EOF

chmod +x ~/claude-automations/scripts/monitor.sh
```

## 🔴 What Still Won't Work

Even after deployment:
1. **PRISM agent integration** - Agents don't use PRISM context
2. **Claude Code event hooks** - Event system unclear
3. **Automatic hook installation** - Must be done per project
4. **Cross-project intelligence** - Each project is isolated

## ✅ What WILL Work

After following this guide:
1. ✅ Auto-commit every 30 minutes
2. ✅ Auto-push after commits
3. ✅ Smart commit messages (if configured)
4. ✅ Project-specific documentation
5. ✅ Basic monitoring and logs

## 🚀 Next Steps

1. **Deploy to virtual-tutor first** - Has 361 uncommitted files
2. **Monitor for 24 hours** - Check if auto-commits work
3. **Add logging** - Debug what's not working
4. **Iterate** - Adjust timing, improve messages
5. **Document findings** - Update REALITY_CHECK.md

---

**Remember**: Perfect automation that doesn't run is worse than simple automation that works. Start with cron + git hooks, then improve from there.