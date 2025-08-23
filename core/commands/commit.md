---
description: Smart commit with AI-generated message
allowed_tools: ["read", "write", "bash"]
model: claude-4-turbo
---

# /commit - Smart Commit with AI-generated message

Create an intelligent commit with automatic message generation based on current changes.

## What this does:
1. Analyzes all current changes in the repository
2. Detects work patterns (feature, bugfix, docs, etc.)
3. Generates appropriate conventional commit message
4. Commits and optionally pushes

## Usage:
- `/commit` - Analyze, generate message, and commit
- `/commit --push` - Also push to remote after commit
- `/commit --message "custom message"` - Override with custom message
- `/commit --dry-run` - Preview what would be committed

## Auto-commit triggers:
This command is also triggered automatically by Claude Code hooks when:
- 30 minutes have passed since last commit
- 5+ files have been modified
- Major operation completed (refactor, feature, etc.)
- Before risky operations (as safety checkpoint)

## Implementation:

```bash
#!/bin/bash
# Get the current working directory
REPO_PATH=$(pwd)

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check for changes
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo "📊 Analyzing repository changes..."
    
    # Run the Python analyzer from smart-commit-genie
    python3 -c "
import sys
import os
import subprocess
sys.path.insert(0, '${HOME}/claude-automations/git-intelligence/src')

from git_state_analyzer import GitStateAnalyzer
from commit_generator import CommitMessageGenerator, CommitConfig

# Analyze current repository
analyzer = GitStateAnalyzer('.')
state = analyzer.analyze()

# Check if there are changes to commit
if not state.staged_changes and not state.uncommitted_changes:
    print('ℹ️ No changes to commit')
    sys.exit(0)

# Stage all changes
subprocess.run(['git', 'add', '-A'], check=True)

# Generate commit message
config = CommitConfig(format_type='conventional', include_body=True)
generator = CommitMessageGenerator(config=config)
suggestions = generator.generate_commit_message()

if suggestions and suggestions.primary_suggestion:
    message = suggestions.primary_suggestion.formatted_message
    print(f'✅ Generated commit message:')
    print(f'   {message.split(chr(10))[0]}')  # First line only
    
    # Create the commit
    result = subprocess.run(
        ['git', 'commit', '-m', message],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print('✅ Changes committed successfully')
        
        # Get commit hash
        commit_hash = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True
        ).stdout.strip()
        print(f'   Commit: {commit_hash}')
        
        # Push if requested
        if '--push' in sys.argv:
            print('📤 Pushing to remote...')
            push_result = subprocess.run(['git', 'push'], capture_output=True, text=True)
            if push_result.returncode == 0:
                print('✅ Pushed to remote')
            else:
                print('⚠️ Push failed - commit saved locally')
    else:
        print('❌ Commit failed:', result.stderr)
else:
    # Fallback to simple message
    print('⚠️ Using fallback commit message')
    subprocess.run(['git', 'commit', '-m', 'checkpoint: auto-commit by Smart Commit Genie'], check=True)
    print('✅ Changes committed')
"
else
    echo "ℹ️ No changes to commit"
fi
```

## Examples:

```bash
# In a Claude Code session
/commit                    # Auto-analyze and commit
/commit --push            # Commit and push
/commit --dry-run         # Preview only
```

## Benefits:
- Never lose work with automatic checkpoints
- Consistent commit message format
- Smart pattern detection
- Zero friction - just works
- Safety net for your code