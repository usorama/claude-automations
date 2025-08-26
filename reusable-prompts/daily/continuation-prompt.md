# 🔄 Project Continuation Handoff Prompt

## Metadata
```yaml
name: continuation-prompt
version: 1.1.0
created_by: Claude Code Assistant
created_date: 2025-08-26
last_modified: 2025-08-26
category: daily-workflow
tags: [context-engineering, session-handoff, continuation, project-management, git-safety]
changelog:
  - v1.1.0 (2025-08-26): Added mandatory git commit/push before handoff
  - v1.0.0 (2025-08-26): Initial implementation with optimized context engineering
```

## Purpose
Generates an optimized continuation package for seamless handoff between Claude Code sessions. Engineers minimal context while preserving all critical information needed to continue work exactly where it left off.

## Usage
```
/continuation-prompt [mode] [options]

Modes:
  compact  - Minimal version for copy-paste (<500 lines)
  full     - Complete context with all details
  
Options:
  --save   - Save to .continuation/session-{timestamp}.md
  --prism  - Use PRISM for context optimization
```

Examples:
- `/continuation-prompt` - Generate compact continuation
- `/continuation-prompt full` - Generate detailed handoff
- `/continuation-prompt compact --save` - Compact version + save to file
- `/continuation-prompt --prism` - Use PRISM optimization

---

# PROMPT BEGINS HERE

## 🎯 Session Continuation Package Generator

I need to create an optimized continuation package that captures the current session's context, progress, and state for seamless handoff to a new Claude Code session.

### User Parameters
- Mode: ${MODE:-compact}
- Save to file: ${SAVE:-false}
- Use PRISM: ${PRISM:-auto-detect}

### Phase 0: Git Safety Check (MANDATORY - Run FIRST)

**CRITICAL**: Ensure all work is committed and pushed before creating handoff:

```bash
# 1. Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ $UNCOMMITTED -gt 0 ]; then
  echo "⚠️ STOP: $UNCOMMITTED uncommitted files detected!"
  echo "Creating safety commit before continuation..."
  
  # Add all changes
  git add -A
  
  # Create descriptive commit
  git commit -m "WIP: Session handoff $(date '+%Y-%m-%d %H:%M') - preparing continuation package"
  echo "✅ Created safety commit"
fi

# 2. Push all commits to remote
UNPUSHED=$(git log @{u}.. --oneline 2>/dev/null | wc -l)
if [ $UNPUSHED -gt 0 ]; then
  echo "📤 Pushing $UNPUSHED commits to remote..."
  git push
  echo "✅ All commits pushed to remote"
else
  echo "✅ Already in sync with remote"
fi

# 3. Verify clean state
if [ $(git status --porcelain | wc -l) -eq 0 ]; then
  echo "✅ Git state is clean and safe for handoff"
else
  echo "⚠️ WARNING: Still have uncommitted changes after safety commit"
fi
```

### Phase 1: Current State Capture

Execute these commands in parallel to capture current state:

```bash
# Git state
git rev-parse --abbrev-ref HEAD        # Current branch
git log --oneline -1                   # Last commit
git status --porcelain                 # Changed files
git diff --stat                        # Change statistics

# Recent activity
find . -type f -mmin -$((60 * 8)) -not -path "./.git/*" 2>/dev/null | head -20  # Files modified in session

# Task state
# Check for .todo files or task lists
find . -name "*.todo" -o -name "TODO.md" 2>/dev/null

# Work markers
grep -r "TODO\|FIXME\|WIP" --include="*.js" --include="*.ts" --include="*.py" --include="*.go" --include="*.md" . 2>/dev/null | grep -E "(added|modified) today" | head -10
```

### Phase 2: Context Analysis

Analyze and score files for criticality:

#### Critical Files (MUST READ) - Score 10
1. Files modified in this session
2. CLAUDE.md, rules.md, README.md
3. Configuration files that changed
4. Files with active TODOs/FIXMEs

#### Important Files - Score 7
1. Test files related to changes
2. Documentation updated
3. Dependencies modified
4. API/Interface definitions

#### Contextual Files - Score 5
1. Parent modules of changed files
2. Related configuration
3. Build/deployment scripts

Select top 10-15 files based on score.

### Phase 3: Generate Continuation Package

Create structured output based on mode:

```markdown
# 🔄 PROJECT CONTINUATION PACKAGE
Session ID: ${SESSION_ID}
Generated: ${TIMESTAMP}
Project: ${PROJECT_NAME}

## 🎯 Quick Start
Copy this entire block and paste at the start of your new Claude Code session.

## 🔒 Git Safety Check
- ✅ All changes committed at: ${LAST_COMMIT_TIME}
- ✅ All commits pushed to remote
- ✅ Repository state is clean and safe

## 📊 Session Summary
[2-3 sentence summary of what was accomplished and current focus]

## ✅ Completed in This Session
- [x] Task 1 with reference (commit: abc123)
- [x] Task 2 with outcome
- [x] Task 3 with any notes

## 🔄 Work in Progress
\`\`\`yaml
current_task: "Description of what you were actively doing"
files_editing: 
  - path/to/file1.js (line 145 - implementing feature X)
  - path/to/file2.py (refactoring function Y)
next_action: "The immediate next step to take"
\`\`\`

## 📋 Pending Tasks
1. [ ] Task from TodoWrite with context
2. [ ] Next priority with reasoning
3. [ ] Future task with dependencies

## 📁 Critical Files to Read
\`\`\`bash
# Read these files first for context (in priority order)
1. ./path/to/critical/file1.md   # Project rules and guidelines
2. ./src/module/active_work.js   # Contains current implementation
3. ./tests/test_suite.py         # Related tests need updating
4. ./config/settings.json        # Changed configuration
5. ./.todo                       # Current task list
\`\`\`

## 🎨 Key Decisions & Context
\`\`\`yaml
decisions:
  - choice: "Used approach X instead of Y"
    reason: "Better performance and maintainability"
    impact: "Affects how we handle Z going forward"
  
  - choice: "Deferred feature B"
    reason: "Waiting for user clarification"
    question: "Should B integrate with existing system or standalone?"

patterns_observed:
  - "User prefers explicit type annotations"
  - "Project uses functional programming style"
  - "Tests should be written before implementation"
\`\`\`

## 🚧 Active Problems/Blockers
\`\`\`yaml
blockers:
  - issue: "Test failing in CI"
    details: "auth.test.js line 45 - timeout issue"
    attempted: "Increased timeout, still fails"
    next_try: "Check for race condition"

  - issue: "Dependency conflict"
    details: "Package X requires Y@2.0, but Z needs Y@1.0"
    proposed: "Upgrade Z or find alternative to X"
\`\`\`

## 🔀 Environment State
\`\`\`bash
# Repository state
branch: feature/continuation-prompts
uncommitted_files: 12
staged_changes: 0
last_commit: "3dce32f - feat: Implement PRISM"

# Key services/processes
database: PostgreSQL (running on port 5432)
api_server: Not running (start with: npm run dev)
background_jobs: None

# Important environment variables
NODE_ENV=development
PRISM_ENABLED=true
\`\`\`

## 🎯 Next Steps (Prioritized)
\`\`\`markdown
1. **Immediate** (< 5 min)
   - [ ] Read critical files listed above
   - [ ] Run \`git status\` to verify state
   - [ ] Check tests with \`npm test\`

2. **Continue Work** (Current session focus)
   - [ ] Complete implementation in active_work.js
   - [ ] Update related tests
   - [ ] Document changes

3. **Next Priority** (After current task)
   - [ ] Address the CI test failure
   - [ ] Resolve dependency conflict
   - [ ] Review and merge pending PR
\`\`\`

## ✅ Verification Checklist
Run these commands to verify environment matches:
\`\`\`bash
# Verify git state
git branch --show-current           # Should show: feature/continuation-prompts
git status --short | wc -l          # Should show: 12 files

# Verify dependencies
npm list --depth=0 2>/dev/null || pip list 2>/dev/null || go list ./...

# Verify tests
npm test -- --listTests 2>/dev/null || pytest --collect-only 2>/dev/null

# Check for running services
lsof -i :5432                       # PostgreSQL
ps aux | grep -E "(node|python|go)" # Running processes
\`\`\`

## 💬 Conversation Context
\`\`\`yaml
user_preferences:
  - "Uses /xall for enhanced thinking"
  - "Prefers concise responses"
  - "Wants automatic test execution"
  
established_patterns:
  - "Always check CLAUDE.md first"
  - "Run tests before committing"
  - "Use TodoWrite for task tracking"

custom_commands_used:
  - /start-prompt
  - /commit
  - /xall

communication_style: "Direct, technical, solution-focused"
\`\`\`

## 🔗 Related Documentation
- Project README: ./README.md
- Development Rules: ./rules.md
- Claude Instructions: ./CLAUDE.md
- Previous Continuations: ./.continuation/

## 📝 Notes for Next Session
\`\`\`
[Any specific notes, reminders, or context that doesn't fit above]
\`\`\`

---
END CONTINUATION PACKAGE - Copy everything above
```

### Phase 4: Compact vs Full Mode

#### Compact Mode (Default)
- Limit to 500 lines maximum
- Include only Score 8+ files
- Summarize decisions briefly
- Show only active blockers
- List top 5 pending tasks

#### Full Mode
- No line limit
- Include all relevant files
- Detailed decision history
- Complete blocker history
- Full task list with context
- Include code snippets from WIP
- Add performance metrics
- Include test results

### Phase 5: Optional Enhancements

#### With --save flag:
```bash
# Create continuation directory
mkdir -p .continuation

# Save with timestamp
filename=".continuation/session-$(date +%Y%m%d-%H%M%S).md"

# Save package
cat > "$filename" << 'EOF'
[Generated package content]
EOF

# Create latest symlink
ln -sf "$filename" .continuation/latest.md
```

#### With --prism flag:
Use PRISM MCP to optimize context:
```python
# Use PRISM for intelligent context selection
context = prism.get_optimal_context(
    agent_type="continuation",
    task_description="session handoff",
    project_path="."
)
```

### Phase 6: Output Format

1. **Display Format**: Show package in code block for easy copying
2. **Save Format**: Write to file if requested
3. **Verification**: Provide command to verify package was saved
4. **Size Check**: Warn if compact mode exceeds 500 lines

### Implementation Notes

The continuation prompt should:
- Be deterministic (same output for same state)
- Handle missing tools gracefully
- Work across all project types
- Preserve work context without file contents
- Optimize for token efficiency
- Include verification steps
- Support incremental continuations

### Quality Metrics

A good continuation package:
- ✅ Under 500 lines in compact mode
- ✅ Contains all active work references
- ✅ Includes clear next actions
- ✅ Preserves decision context
- ✅ Enables work to continue immediately
- ✅ Requires minimal additional discovery

---

*End of Prompt v1.0.0*