#!/usr/bin/env claude-command
# Universal Project Continuation Command
# Version: 1.1.0
# Created: 2025-08-26
# Updated: 2025-08-26 - Added git safety checks

## Description
Analyzes project state from previous session and creates actionable plan for current work session. Performs comprehensive discovery of git state, documentation, incomplete work, and testing status.

## Usage
```
/start-prompt [optional focus instructions]
```

## Examples
- `/start-prompt` - Standard daily startup
- `/start-prompt focus on testing`
- `/start-prompt continue auth feature`
- `/start-prompt prepare for release`

## Implementation

Execute the Universal Project Continuation Protocol with these steps:

### 1. Git Safety Check (MANDATORY FIRST)

```bash
# Ensure all work is safe
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ $UNCOMMITTED -gt 0 ]; then
  git add -A
  git commit -m "WIP: Auto-commit at session start $(date '+%Y-%m-%d %H:%M')"
fi

# Push to remote
git push 2>/dev/null || echo "Push failed - check credentials"

# Pull latest
git pull --rebase 2>/dev/null || echo "Pull failed - check connection"
```

### 2. Discovery Phase (Parallel Execution)

Run these commands simultaneously:

```bash
# Git state
git status
git log --oneline -15
git diff --cached
git diff HEAD
git branch -v
git stash list

# Find recent changes
find . -type f -mtime -1 -not -path "./.git/*" | head -20

# Search for work markers
grep -r "TODO\|FIXME\|WIP\|HACK\|XXX" --include="*.js" --include="*.ts" --include="*.py" --include="*.go" --include="*.java" --include="*.md" . 2>/dev/null | head -20
```

### 2. Documentation Review

Read in order of priority:
1. `./CLAUDE.md` and `~/CLAUDE.md` and `~/.claude/CLAUDE.md`
2. `./rules.md` or `./RULES.md`
3. `./README.md`
4. `./TODO.md` or `./ROADMAP.md`
5. Any `.todo` files

### 3. Project Analysis

Detect and analyze:
- Project type (package.json, requirements.txt, go.mod, etc.)
- Test framework and status
- Build system
- Recent error logs
- CI/CD status

### 4. Generate Report

Create structured output:

```markdown
## 📊 Project Status: [Project Name]

### Current State
- Branch: [branch-name]
- Last Commit: [commit message]
- Uncommitted: [X files]
- Project Type: [detected stack]

### Work in Progress
- [ ] Item from previous session
- [ ] Uncommitted changes in [files]
- [ ] TODO items found

### Blockers
- ⚠️ [Any critical issues]
- 🐛 [Test failures]

### Today's Priorities
1. [Most important]
2. [Second priority]
3. [Third priority]

### Immediate Actions
\`\`\`bash
# Commands to run
\`\`\`
```

### 5. Create Task List

Use TodoWrite to create today's tasks based on analysis.

### 6. User Focus Integration

If user provides focus area in ${1}, prioritize related tasks and analysis.

## Configuration

The full prompt template is stored at:
`~/claude-automations/reusable-prompts/daily/start-prompt.md`

## Related Commands
- `/status` - Quick project status
- `/plan` - Detailed planning
- `/todo` - Manage tasks

## Notes
- Handles any project type
- Works with incomplete or minimal projects
- Integrates with user's global and project instructions
- Creates actionable next steps
- Runs discovery in parallel for speed