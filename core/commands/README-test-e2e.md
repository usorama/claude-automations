# E2E Testing Slash Command Usage

## Installation Complete ✅
The E2E testing slash command has been installed at:
`~/.claude/commands/test-e2e.md`

## How to Use

### In Claude Code:
1. Start Claude Code in your project directory:
   ```bash
   cd your-project
   claude
   ```

2. Use the slash command:
   ```
   /test-e2e
   ```
   
   Or specify a different project path:
   ```
   /test-e2e /path/to/project
   ```

### What It Does:
1. Checks for existing test infrastructure in your project
2. Copies the testing framework files if needed
3. Guides Claude through comprehensive E2E testing
4. Follows the systematic checklist approach
5. Generates all required test artifacts

### Framework Files Location:
- **Prompt**: ~/.claude/process-templates-n-prompts/testing-prompt.md
- **Template**: ~/.claude/process-templates-n-prompts/testing-template.md
- **Checklist**: ~/.claude/process-templates-n-prompts/testing-checklist.md

### Project Testing Files (Created):
- .claude/testing/testing-prompt.md
- .claude/testing/testing-template.md
- .claude/testing/testing-checklist.md

### Tips:
- The command will be available after restarting Claude Code
- Type `/` in Claude Code to see all available commands
- The command respects existing test infrastructure
- Progress is tracked in the checklist file

### Quick Test:
```bash
# Create a test project
mkdir -p ~/test-project
cd ~/test-project

# Start Claude Code
claude

# Run the E2E testing command
/test-e2e
```

---
Created: $(date)
Command Name: /test-e2e
