---
command: branch
description: Automatically create and switch to intelligently-named branches
---

Create an intelligent branch for the current work context using the Smart Commit Genie auto-branching system.

## Usage
Just type `/branch` and the system will:
1. Analyze your current work context
2. Detect the type of work (feature, bugfix, refactor, etc.)
3. Generate an appropriate branch name
4. Create and switch to the new branch automatically

## How it works
```python
import sys
import json
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from auto_branching import AutoBranchManager

# Get context from Claude
context = {
    "changed_files": get_changed_files(),
    "current_task": "{{TASK_DESCRIPTION}}",  # Claude will fill this
    "last_commit_msg": get_last_commit_message()
}

# Initialize manager
manager = AutoBranchManager()

# Create branch if appropriate
result = manager.auto_branch(context)

if result:
    print(f"✅ Created and switched to branch: {result}")
    print("🚀 Ready to start developing!")
else:
    # Check if we should suggest merge
    merge_suggestion = manager.suggest_branch_merge()
    if merge_suggestion:
        print(f"💡 Current branch '{merge_suggestion['branch']}' has {merge_suggestion['commits']} commits")
        print("📤 Consider creating a PR with /pr command")
    else:
        print("ℹ️ Already on a feature branch or not enough changes to create new branch")
```

## Features
- **Intelligent naming**: Branch names based on work type and context
- **Automatic detection**: Knows when to create new branches
- **Pattern learning**: Learns from your team's branching patterns
- **Merge suggestions**: Tells you when branches are ready for PR

## Examples
- Working on new feature → `feature/user-auth-1223`
- Fixing a bug → `bugfix/login-error-1223`  
- Refactoring code → `refactor/database-layer-1223`
- Documentation updates → `docs/api-guide-1223`

## Tips
- The system won't create a branch if you're already on a feature branch
- It requires at least 2 changed files to trigger auto-branching
- Branch names include timestamps to ensure uniqueness
- Use `/pr` when the branch is ready to create a pull request