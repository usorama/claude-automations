---
command: pr
description: Automatically create pull requests with AI-generated descriptions
---

Create a pull request with an intelligently generated description using Smart Commit Genie.

## Usage
Type `/pr` to:
1. Analyze all commits in your branch
2. Generate comprehensive PR description
3. Create PR with proper formatting
4. Assign reviewers automatically
5. Link related issues

## How it works
```python
import sys
import json
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from auto_pr import AutoPRManager

# Initialize manager
manager = AutoPRManager()

# Check if PR should be created
should_create, reason = manager.should_create_pr()

if should_create:
    print("📝 Analyzing branch changes...")
    
    # Generate PR description
    pr_data = manager.generate_pr_description()
    
    print(f"📋 PR Title: {pr_data['title']}")
    print(f"🎯 Target Branch: {pr_data['base']}")
    print("\n📄 PR Description Preview:")
    print("=" * 50)
    print(pr_data['body'][:500] + "...")
    print("=" * 50)
    
    # Create the PR
    print("\n🚀 Creating pull request...")
    result = manager.create_pr(pr_data)
    
    if result['success']:
        print(f"✅ PR created successfully!")
        print(f"🔗 {result['url']}")
        print("\n🤖 Auto-review will run shortly...")
    else:
        print(f"❌ Failed to create PR: {result.get('error', 'Unknown error')}")
else:
    print(f"ℹ️ Cannot create PR: {reason}")
    
    if reason == "No unpushed commits":
        print("💡 Tip: Make some commits first with /commit")
    elif reason == "PR already exists":
        print("💡 Tip: Check existing PRs with 'gh pr list'")
```

## Features
- **Smart descriptions**: Analyzes commits to write comprehensive PR descriptions
- **Auto-categorization**: Detects feature, bugfix, refactor, etc.
- **Change summary**: Lists all modified files by category
- **Test detection**: Identifies test changes and coverage
- **Issue linking**: Automatically finds and links related issues
- **Review assignment**: Suggests reviewers based on code ownership

## PR Description Includes
- Summary of changes
- Detailed change list by category
- Type of change checklist
- Testing information
- Screenshots (if found)
- Related issues
- Verification steps

## Examples

### Feature PR
```markdown
✨ Feature: Add user authentication system

## Summary
- Implement JWT-based authentication
- Add login/logout endpoints
- Create user session management

## Changes
### Backend
- `src/auth/jwt.py`
- `src/auth/session.py`

### Frontend
- `components/LoginForm.tsx`
- `components/UserMenu.tsx`

### Tests
- `tests/test_auth.py`
- All tests passing locally ✅
```

### Bugfix PR
```markdown
🐛 Fix: Resolve login timeout issue

## Problem
Users were experiencing timeouts during login

## Solution
Increased connection timeout and added retry logic

## Verification Steps
1. Attempt login with slow connection
2. Verify no timeout occurs
```

## Tips
- Commit messages matter - they're used to generate the PR description
- The more detailed your commits, the better the PR description
- Use conventional commit format for best results
- PR will be auto-reviewed after creation