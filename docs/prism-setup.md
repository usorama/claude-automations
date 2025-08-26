# PRISM Setup Complete 🔮

## Quick Access Commands

### From Terminal (bash/zsh):
```bash
prism          # Show dashboard
prism clear    # Clear data
prism help     # Show help
```

### From Claude Code:
```
/prism         # Show dashboard
/prism clear   # Clear data
/prism help    # Show help
```

## What's Installed

### 1. Data Collection Hook
**Location**: `~/claude-automations/core/hooks/prism-collector.py`
- Fires on PostToolUse events
- Collects: Task, Read, Write, Edit, Grep, Glob, Bash usage
- Stores in SQLite: `~/.claude/prism/intelligence.db`

### 2. Context Injection Hook
**Location**: `~/claude-automations/core/hooks/prism-injector.py`
- Fires on UserPromptSubmit events
- Injects learned patterns as context
- Shows: recent agents, hot files, active searches

### 3. Real-Time Dashboard
**Location**: `~/claude-automations/prism/src/realtime_dashboard.py`
- Shows live metrics from actual Claude Code usage
- Displays: tool counts, agent activity, file patterns, searches
- Updates automatically as you work

## How PRISM Works

1. **Automatic Collection**: Every time you use a Claude Code tool (Read, Write, Task, etc.), the PostToolUse hook captures the event and records it.

2. **Pattern Learning**: PRISM analyzes your usage to identify:
   - Which agents you use most
   - Which files you access frequently
   - Common search patterns
   - Command preferences

3. **Context Enhancement**: When you submit a prompt, PRISM injects relevant context based on recent activity.

4. **Visualization**: The dashboard shows real-time metrics so you can see what PRISM has learned.

## Accessing the Dashboard

### Method 1: Terminal Alias
After reloading your shell (`source ~/.zshrc`):
```bash
prism
```

### Method 2: Direct Path
```bash
python3 ~/claude-automations/prism/src/realtime_dashboard.py
```

### Method 3: Claude Code Command
Inside Claude Code:
```
/prism
```

### Method 4: Scripts Directory
The script is also available at:
```bash
~/claude-automations/scripts/prism
```

## Data Storage

PRISM data is stored in: `~/.claude/prism/intelligence.db`

Tables:
- `tool_usage` - All tool invocations
- `agent_usage` - Agent (Task) executions
- `file_patterns` - File access patterns
- `search_patterns` - Grep/Glob searches
- `command_patterns` - Bash commands

## Troubleshooting

### Dashboard shows no data
- The hooks are collecting data in real-time
- Use some Claude Code tools (Read files, run Tasks, etc.)
- Data will appear as you work

### Hooks not firing
- Check symlinks: `ls -la ~/.claude/hooks/`
- Should point to: `~/claude-automations/core/hooks/`
- Restart Claude Code if needed

### Clear test data
```bash
prism clear
# or
/prism clear
```

## Next Steps

Just use Claude Code normally! PRISM will:
- Learn your patterns automatically
- Build intelligence over time
- Provide better context for future sessions

The more you use Claude Code, the smarter PRISM gets!