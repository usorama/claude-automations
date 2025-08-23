---
description: Smart commit with AI-generated message
---

# Smart Commit

Analyze the repository changes and create an intelligent commit with an AI-generated message.

First, check the git status to see what changes need to be committed. Then use the git-intelligence analyzer at ~/claude-automations/git-intelligence/src/ to analyze the changes and generate an appropriate conventional commit message.

The process should be:
1. Run `git status` to see current changes
2. If there are changes, run `git add -A` to stage everything
3. Use the Python script below to analyze and generate a commit message:

```python
import sys
import os
sys.path.insert(0, os.path.expanduser('~/claude-automations/git-intelligence/src'))

from git_state_analyzer import GitStateAnalyzer
from commit_generator import CommitMessageGenerator, CommitConfig

# Analyze current repository
analyzer = GitStateAnalyzer('.')
state = analyzer.analyze()

if not state.staged_changes and not state.uncommitted_changes:
    print('No changes to commit')
else:
    # Generate commit message
    config = CommitConfig(format_type='conventional', include_body=True)
    generator = CommitMessageGenerator(config=config)
    suggestions = generator.generate_commit_message()
    
    if suggestions and suggestions.primary_suggestion:
        message = suggestions.primary_suggestion.formatted_message
        print(f"Generated message:\n{message}")
```

4. Create the commit with the generated message using `git commit -m "message"`
5. If the user wants to push, also run `git push`

Execute this workflow automatically without asking for confirmation unless there's an error. The goal is zero-friction commits.