#!/usr/bin/env claude-command
# Project Continuation Package Generator
# Version: 1.1.0
# Created: 2025-08-26
# Updated: 2025-08-26 - Added mandatory git safety checks

## Description
Generates an optimized continuation package for seamless handoff between Claude Code sessions. Engineers minimal context while preserving all critical information needed to continue work.

## Usage
```
/continuation-prompt [mode] [--save] [--prism]
```

## Arguments
- `mode`: `compact` (default) or `full` - Size of continuation package
- `--save`: Save to .continuation/session-{timestamp}.md
- `--prism`: Use PRISM for context optimization

## Examples
- `/continuation-prompt` - Quick compact package
- `/continuation-prompt full` - Detailed handoff
- `/continuation-prompt compact --save` - Save compact version
- `/continuation-prompt --prism` - Optimize with PRISM

## Implementation

Generate a project continuation package with these components:

### 1. Git Safety Check (MANDATORY FIRST)

```bash
# Commit and push all work before handoff
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ $UNCOMMITTED -gt 0 ]; then
  echo "⚠️ Committing $UNCOMMITTED files before handoff..."
  git add -A
  git commit -m "WIP: Session handoff $(date '+%Y-%m-%d %H:%M')"
fi

# Push all commits
UNPUSHED=$(git log @{u}.. --oneline 2>/dev/null | wc -l)
if [ $UNPUSHED -gt 0 ]; then
  echo "📤 Pushing $UNPUSHED commits..."
  git push
fi

echo "✅ Repository safe for handoff"
```

### 2. Capture Current State

```bash
# Parallel execution for efficiency
SESSION_ID=$(date +%s | md5sum | head -c 8)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Git state
BRANCH=$(git rev-parse --abbrev-ref HEAD)
LAST_COMMIT=$(git log --oneline -1)
UNCOMMITTED=$(git status --porcelain | wc -l)
CHANGED_FILES=$(git diff --name-only)

# Recent activity (last 8 hours)
RECENT_FILES=$(find . -type f -mmin -480 -not -path "./.git/*" 2>/dev/null | head -20)

# Current tasks from TodoWrite
# Extract pending and in_progress tasks

# Work markers
ACTIVE_TODOS=$(grep -r "TODO\|FIXME\|WIP" --include="*.js" --include="*.ts" --include="*.py" --include="*.md" . 2>/dev/null | head -10)
```

### 2. Score and Select Critical Files

```python
# File criticality scoring
critical_files = []

# Score 10: Must read
- Files currently being edited
- CLAUDE.md, rules.md, README.md  
- Files with uncommitted changes
- Active configuration files

# Score 7: Important
- Test files for changed code
- Related documentation
- Modified dependencies

# Score 5: Contextual
- Parent modules
- Related configs

# Select top 10-15 by score
```

### 3. Generate Package Structure

```markdown
# 🔄 PROJECT CONTINUATION PACKAGE
Session: ${SESSION_ID}
Generated: ${TIMESTAMP}

## Session Summary
[Auto-generated 2-3 sentence summary]

## Completed Tasks
- [x] Items marked complete in TodoWrite
- [x] Committed changes with refs

## Work in Progress
current_task: "Active work description"
files_editing: ["file1.js:145", "file2.py:23"]
next_action: "Immediate next step"

## Pending Tasks
[From TodoWrite pending items]

## Critical Files (Read First)
1. ./CLAUDE.md - Project instructions
2. ./src/active.js - Current work
3. [Additional scored files]

## Key Decisions
- Decision: Reasoning and impact
- Trade-off: What and why

## Blockers
- Issue: Details and next steps

## Environment
branch: ${BRANCH}
uncommitted: ${UNCOMMITTED}
last_commit: ${LAST_COMMIT}

## Next Steps
1. Immediate: Verification commands
2. Continue: Active work
3. Next: Priority tasks

## Verification
\`\`\`bash
git branch --show-current  # Should be: ${BRANCH}
git status --short | wc -l # Should be: ${UNCOMMITTED}
\`\`\`
```

### 4. Mode Handling

```bash
if [[ "$1" == "full" ]]; then
  # Include all context
  MAX_LINES=9999
  FILE_LIMIT=25
  INCLUDE_SNIPPETS=true
else
  # Compact mode (default)
  MAX_LINES=500
  FILE_LIMIT=10
  INCLUDE_SNIPPETS=false
fi
```

### 5. Save Option

```bash
if [[ "$*" == *"--save"* ]]; then
  mkdir -p .continuation
  FILENAME=".continuation/session-$(date +%Y%m%d-%H%M%S).md"
  # Save generated package to file
  echo "[Package Content]" > "$FILENAME"
  ln -sf "$FILENAME" .continuation/latest.md
  echo "Saved to: $FILENAME"
fi
```

### 6. PRISM Integration

```bash
if [[ "$*" == *"--prism"* ]] && command -v prism &> /dev/null; then
  # Use PRISM for context optimization
  OPTIMIZED_CONTEXT=$(prism get_optimal_context \
    --agent "continuation" \
    --task "session-handoff" \
    --project "$(pwd)")
  # Include optimized context in package
fi
```

### 7. Output Format

The package is displayed in a code block for easy copying:
- Compact: <500 lines, essential context only
- Full: Complete context with code snippets
- Always includes verification steps
- Uses markdown for structure

## Configuration

Full template: `~/claude-automations/reusable-prompts/daily/continuation-prompt.md`

## Features

- **Context Engineering**: Minimal tokens, maximum understanding
- **File Scoring**: Intelligent selection of critical files
- **State Capture**: Complete environment snapshot
- **Verification**: Ensures continuity in new session
- **Task Integration**: Uses TodoWrite for task state
- **Decision History**: Preserves reasoning context
- **Flexible Modes**: Compact or full based on needs

## Related Commands
- `/start-prompt` - Begin new day's work
- `/status` - Quick project status
- `/save-session` - Save detailed session

## Best Practices
- Run before ending long work sessions
- Use `--save` for complex projects
- Include in commit messages for context
- Review previous continuations when starting

## Notes
- Optimized for Claude Code context windows
- Works across all project types
- Preserves work momentum between sessions
- Enables immediate work continuation