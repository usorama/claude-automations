# 🚨 CLAUDE CODE - CRITICAL INSTRUCTIONS 🚨

**READ THIS FIRST BEFORE ANY WORK IN CLAUDE-AUTOMATIONS**

Last Updated: August 23, 2025

## 🏗️ ARCHITECTURE - HOW THIS WORKS

### The Golden Rule
**NEVER PUT FILES DIRECTLY IN ~/.claude/**

### Correct Structure:
```
~/claude-automations/           # ← ALL FILES GO HERE (Git controlled)
├── core/
│   ├── commands/              # ← Slash commands (/commit, /plan, etc.)
│   ├── hooks/                 # ← Event hooks (auto-commit, etc.)
│   ├── agents/                # ← Specialist agents
│   └── scripts/               # ← Utility scripts
├── git-intelligence/          # ← Git automation subsystem
├── config/                    # ← Configuration files
└── docs/                      # ← Documentation

~/.claude/                     # ← ONLY SYMLINKS HERE
├── commands → ~/claude-automations/core/commands
├── hooks → ~/claude-automations/core/hooks
├── agents → ~/claude-automations/core/agents
└── scripts → ~/claude-automations/core/scripts
```

### Why This Architecture:
1. **Survives Claude reinstalls** - Customizations are separate
2. **Git controlled** - Everything versioned in claude-automations
3. **Portable** - Clone repo + create symlinks = instant setup
4. **Organized** - Clear separation of concerns

## 🎯 PURPOSE OF CLAUDE-AUTOMATIONS

This is NOT just about git. This is a comprehensive automation ecosystem for:

### 1. **Safety Nets** (Automatic, no interaction)
- Auto-commit every 30 minutes
- Auto-backup before risky operations
- Auto-checkpoint on file changes
- Auto-push to preserve work remotely

### 2. **Workflow Automation**
- Auto-branch creation for features
- Auto-PR generation
- Auto-documentation updates
- Auto-test execution

### 3. **Intelligence Augmentation**
- Smart commit messages from code analysis
- Pattern detection in development
- Context-aware suggestions
- Learning from repository history

### 4. **Developer Experience**
- Zero-friction tools (work automatically)
- Natural language commands (/commit, /plan)
- Proactive assistance (not reactive)
- Silent operation (no interruptions)

## ⚠️ CRITICAL REMINDERS FROM TODAY'S SESSION

### 1. **Automation-First Philosophy**
```
❌ WRONG: "Here's a tool, remember to use it"
✅ RIGHT: "It's already working in the background"
```

**Example:**
- ❌ `scg commit` (manual CLI command)
- ✅ `/commit` (Claude Code slash command)
- ✅ Auto-commit hook (runs automatically)

### 2. **The Airbag Principle**
> "Like airbags in a car - always there, works automatically, saves you when needed"

You don't "use" these automations - they're just there, protecting your work.

### 3. **Zero Manual Intervention**
If the user has to:
- Remember to run something
- Choose between options
- Confirm actions
- Wait for prompts

**Then we've failed.** Automation means AUTOMATIC.

### 4. **Commands vs CLI Tools**
- **Slash Commands** (`/commit`): Inside Claude Code, contextual
- **CLI Tools** (`scg commit`): External, manual, AVOID
- **Hooks**: Background, automatic, PREFERRED

## 📁 WHERE THINGS GO

### For Git Intelligence Features:
```
~/claude-automations/git-intelligence/
├── src/                       # Core logic (analyzers, generators)
├── tests/                     # Test suites
├── config/                    # Configuration
└── docs/                      # Documentation

~/claude-automations/core/commands/
└── commit.md                  # /commit slash command

~/claude-automations/core/hooks/
└── smart-auto-commit.py       # Auto-commit hook
```

### For New Features:
1. **Core logic** → `git-intelligence/src/` or new subsystem
2. **Slash commands** → `core/commands/`
3. **Hooks** → `core/hooks/`
4. **Agents** → `core/agents/`
5. **Config** → `config/` or subsystem config

## 🚫 WHAT NOT TO DO

### 1. **Don't Create Standalone CLIs**
- No separate Python packages requiring pip install
- No external tools requiring manual execution
- Everything should integrate with Claude Code

### 2. **Don't Put Files in ~/.claude/**
- That's for symlinks only
- Actual files go in ~/claude-automations/

### 3. **Don't Ask for User Confirmation**
- Make intelligent decisions
- Provide undo/rollback instead
- Use --interactive only as optional override

### 4. **Don't Forget Context**
- Claude Code knows what you're working on
- Use that context in automations
- Don't make tools that work in isolation

## ✅ CORRECT WORKFLOW FOR NEW FEATURES

1. **Identify the need** (e.g., "never lose work")
2. **Design for automation** (not manual use)
3. **Implement in claude-automations/**
4. **Create slash command** in `core/commands/`
5. **Add background hook** in `core/hooks/`
6. **Test inside Claude Code** (not standalone)
7. **Ensure zero friction** (works automatically)

## 🔧 CURRENT SUBSYSTEMS

### 1. Git Intelligence (`git-intelligence/`)
- **Purpose**: Smart git operations
- **Components**: 
  - GitStateAnalyzer (Day 2)
  - CommitMessageGenerator (Day 3)
  - Auto-commit hooks (Day 4)
- **Status**: Active, being enhanced

### 2. BMAD Agents (`core/agents/bmad-*.md`)
- **Purpose**: Specialized development agents
- **Count**: 20+ agents
- **Usage**: Via Task tool

### 3. Custom Commands (`core/commands/`)
- **Purpose**: Slash commands for Claude Code
- **Count**: 92+ commands
- **Categories**: Planning, development, testing, deployment

### 4. Event Hooks (`core/hooks/`)
- **Purpose**: Automatic triggers
- **Count**: 20+ hooks
- **Types**: Pre-commit, post-edit, session lifecycle

## 🎯 THE MISSION

**Build an ecosystem where:**
1. Work is never lost (automatic checkpoints)
2. Quality is maintained (automatic validation)
3. Patterns are detected (intelligent analysis)
4. Friction is eliminated (zero manual steps)
5. Context is preserved (Claude-aware)

## 🚀 QUICK REFERENCE

### Testing a New Feature:
```bash
# 1. Implement in claude-automations
cd ~/claude-automations/git-intelligence/src/
# ... create feature ...

# 2. Add slash command
vim ~/claude-automations/core/commands/mycommand.md

# 3. Test in Claude Code
/mycommand

# 4. Add hook if needed
vim ~/claude-automations/core/hooks/my-auto-hook.py
```

### Installing for New Machine:
```bash
# 1. Clone repository
git clone <repo> ~/claude-automations

# 2. Create symlinks
ln -s ~/claude-automations/core/commands ~/.claude/commands
ln -s ~/claude-automations/core/hooks ~/.claude/hooks
ln -s ~/claude-automations/core/agents ~/.claude/agents

# 3. Done - everything works
```

## 🎓 KEY LESSONS LEARNED

1. **Day 4 Mistake**: Built standalone CLI instead of Claude integration
   - Lesson: Always integrate with Claude Code, never standalone

2. **Manual vs Automatic**: If user has to remember, it's not automation
   - Lesson: Background hooks > slash commands > external tools

3. **Configuration**: Smart defaults > required configuration
   - Lesson: Should work with zero config

4. **Output**: Silent success > verbose output
   - Lesson: Only speak when there's a problem

5. **Safety**: Frequent checkpoints > perfect commits
   - Lesson: "WIP: changes" is better than lost work

## 📝 FOR FUTURE SESSIONS

When working in claude-automations:

1. **Check this file first** (CLAUDE.md)
2. **Follow the architecture** (files in claude-automations, symlinks in .claude)
3. **Prioritize automation** (hooks > commands > tools)
4. **Test in Claude Code** (not standalone)
5. **Maintain zero friction** (no manual steps)

## 🔮 FUTURE ENHANCEMENTS

### Planned (Days 5-6):
- [ ] Auto-branching on feature detection
- [ ] PR creation automation
- [ ] PR review automation
- [ ] Smart merging strategies
- [ ] Rollback capabilities

### Possibilities:
- [ ] Learning from team patterns
- [ ] Cross-repository intelligence
- [ ] Deployment automation
- [ ] Performance monitoring
- [ ] Security scanning

---

**Remember: This is not about building tools. It's about building an intelligent safety net that makes development safer, faster, and friction-free. Everything should "just work" without the user thinking about it.**

**The user should code with Claude, and good things should just happen automatically.**

---

*If you're reading this in a future session, you now know:*
1. Where things go (claude-automations, not .claude)
2. How things work (automatic, not manual)
3. What we're building (safety net, not tools)
4. Why we're building it (never lose work, zero friction)

**Now go make development magical. ✨**