# 🚀 Universal Project Continuation Prompt

## Metadata
```yaml
name: start-prompt
version: 1.1.0
created_by: Claude Code Assistant
created_date: 2025-08-26
last_modified: 2025-08-26
category: daily-workflow
tags: [project-management, context-recovery, daily-standup, git-safety]
changelog:
  - v1.1.0 (2025-08-26): Added mandatory git commit/push safety checks
  - v1.0.0 (2025-08-26): Initial implementation with comprehensive discovery phase
```

## Purpose
This prompt helps Claude Code understand where a project left off and determine the next steps to take. It performs a systematic discovery of project state, identifies incomplete work, and creates an actionable plan for the current session.

## Usage
```
/start-prompt [optional: specific focus area or instructions]
```

Examples:
- `/start-prompt` - Standard project review and continuation
- `/start-prompt focus on testing and bug fixes`
- `/start-prompt continue implementing the auth feature`
- `/start-prompt prepare for deployment`

---

# PROMPT BEGINS HERE

## 🎯 Project Continuation Protocol - Daily Startup Sequence

I need to understand where this project left off and determine the optimal next steps. I will perform a comprehensive discovery phase to gather context, then provide you with an actionable summary and plan.

### User Focus Area
${USER_INSTRUCTIONS}

### Phase 1: Git Safety Check (MANDATORY - Run FIRST)

**CRITICAL**: Ensure all work is safe before proceeding:

1. **Check for Uncommitted Work**
   ```bash
   # Check if there are uncommitted changes
   UNCOMMITTED=$(git status --porcelain | wc -l)
   if [ $UNCOMMITTED -gt 0 ]; then
     echo "⚠️ WARNING: $UNCOMMITTED uncommitted files detected!"
     echo "Creating safety commit..."
     git add -A
     git commit -m "WIP: Auto-commit at session start $(date '+%Y-%m-%d %H:%M')"
   fi
   ```

2. **Ensure Work is Pushed**
   ```bash
   # Check if local is ahead of remote
   UNPUSHED=$(git log @{u}.. --oneline | wc -l)
   if [ $UNPUSHED -gt 0 ]; then
     echo "📤 Pushing $UNPUSHED commits to remote..."
     git push
   fi
   
   # Pull any remote changes
   git pull --rebase
   ```

### Phase 2: Mandatory Discovery (Run ALL in parallel)

Execute these discovery commands simultaneously for efficiency:

1. **Git State Analysis**
   - `git status` - Current working tree state
   - `git log --oneline -15` - Recent commit history
   - `git diff --cached` - Staged changes awaiting commit
   - `git diff HEAD` - All uncommitted changes
   - `git branch -v` - Current branch and recent commits
   - `git stash list` - Any stashed work
   - `git log @{u}.. --oneline` - Unpushed commits

2. **Documentation Review**
   - Read `CLAUDE.md` (project-specific instructions)
   - Read `rules.md` or `RULES.md` (development guidelines)
   - Read `README.md` (project overview)
   - Read `.claude/CLAUDE.md` (user's global instructions)
   - Check for `TODO.md`, `CHANGELOG.md`, or `ROADMAP.md`

3. **Code State Analysis**
   - Search for `TODO`, `FIXME`, `WIP`, `HACK`, `XXX` comments
   - Check for `.todo` files or task lists
   - Review any `*.log` files from the last 24 hours
   - Identify files modified in the last day: `find . -type f -mtime -1`

4. **Project Type Detection**
   - Identify project type (Node.js, Python, Go, etc.)
   - Check build/test commands (package.json scripts, Makefile, etc.)
   - Review dependency files for recent changes
   - Check CI/CD configuration (.github/workflows, .gitlab-ci.yml, etc.)

5. **Testing & Quality Status**
   - Run test suite if quick (<30s): `npm test`, `pytest`, etc.
   - Check for test failures or skipped tests
   - Review coverage reports if available
   - Check linting status

### Phase 3: Analysis & Synthesis

Based on the discovery phase, analyze:

1. **Work in Progress**
   - What feature/fix was being worked on?
   - What files were most recently modified?
   - Are there uncommitted changes that need attention?
   - Any abandoned branches or stashes?

2. **Blockers & Issues**
   - Failed tests or builds
   - Unresolved merge conflicts
   - Missing dependencies
   - Configuration issues
   - Error patterns in logs

3. **Project Priorities**
   - Next items in roadmap/TODO
   - Critical bugs or security issues
   - User-reported issues
   - Technical debt items

### Phase 4: Output Format

Provide a structured summary:

```markdown
## 📊 Project Status Report

### 🔒 Git Safety Status
- **Uncommitted Work**: ✅ All changes committed
- **Remote Sync**: ✅ All commits pushed
- **Branch Protection**: ✅ Work is safe

### 🏗️ Current State
- **Project**: [Name and brief description]
- **Branch**: [Current branch and its purpose]
- **Last Activity**: [Most recent commit/change]
- **Project Type**: [Technology stack detected]

### 🔄 Work in Progress
- [ ] [Incomplete item 1 with file references]
- [ ] [Incomplete item 2 with context]
- [ ] [Any stashed or uncommitted work]

### 🚧 Blockers/Issues
- ⚠️ [Critical issue if any]
- 🐛 [Bug or test failure]
- 📝 [Documentation gaps]

### 🎯 Today's Recommended Priorities
1. [Most important task with reasoning]
2. [Second priority with context]
3. [Third priority if applicable]

### 💡 Suggested Next Actions
```bash
# Immediate action commands
[Specific command 1]
[Specific command 2]
```

### 📋 Generated Task List
[Create TodoWrite entries for today's work]
```

### Phase 5: Context Integration

Consider:
- User's specific focus area (if provided)
- Time of day and likely work session duration
- Project momentum and recent velocity
- Dependencies and blockers
- Team collaboration needs (PRs, reviews, etc.)

### Phase 6: Proactive Initialization

After analysis, proactively:
1. Create today's todo list using TodoWrite
2. Set up any needed file watchers or monitors
3. Ensure development environment is ready
4. Pull latest changes if working on shared branch
5. Restore any relevant context from previous sessions

---

## Implementation Notes

This prompt should:
- Be language and framework agnostic
- Handle missing files gracefully
- Work with both new and legacy projects
- Provide value even with minimal project structure
- Execute discovery commands in parallel for speed
- Focus on actionable insights over raw data
- Adapt to user's stated priorities while maintaining thoroughness

## Prompt Improvements Tracking

To suggest improvements to this prompt:
1. Note the current version number
2. Describe the improvement clearly
3. Explain the use case it addresses
4. Update version number using semantic versioning
5. Add entry to changelog

---

*End of Prompt v1.0.0*