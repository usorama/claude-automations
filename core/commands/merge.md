---
command: merge
description: Intelligently merge PRs with conflict resolution and rollback
---

Perform smart automatic merging with safety checks and rollback capabilities.

## Usage
- `/merge` - Auto-merge current branch PR if ready
- `/merge 123` - Merge specific PR number
- `/merge rollback` - Rollback last merge

## How it works
```python
import sys
import json
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from smart_merge import SmartMergeManager

# Parse command
action = "merge"
pr_number = None

if "{{COMMAND}}":  # Claude will fill this
    parts = "{{COMMAND}}".split()
    if "rollback" in parts:
        action = "rollback"
    elif parts and parts[0].isdigit():
        pr_number = int(parts[0])

# Initialize manager
manager = SmartMergeManager()

if action == "rollback":
    print("⏮️ Rolling back last merge...")
    result = manager.rollback_merge()
    
    if result['success']:
        print(f"✅ {result['message']}")
        print("🔄 Repository restored to pre-merge state")
    else:
        print(f"❌ Rollback failed: {result.get('error', 'Unknown error')}")
else:
    # Prepare PR data
    pr_data = {"number": pr_number} if pr_number else {}
    
    # Check if can merge
    print("🔍 Checking merge readiness...")
    can_merge, reason = manager.can_auto_merge(pr_data)
    
    if can_merge:
        print("✅ All checks passed!")
        print("🔀 Starting merge process...")
        
        # Perform merge
        result = manager.auto_merge(pr_data)
        
        if result['success']:
            print(f"🎉 {result['message']}")
            print("🧹 Branch cleaned up automatically")
            
            # Show rollback option
            print("\n💡 If needed, rollback with: /merge rollback")
        else:
            print(f"❌ Merge failed: {result.get('error', result.get('reason', 'Unknown'))}")
            
            # Check if we can help
            if "conflict" in str(result.get('error', '')).lower():
                print("\n🔧 Conflicts detected. Options:")
                print("  1. Fix conflicts manually")
                print("  2. Use '/merge resolve' for auto-resolution")
                print("  3. Abort with 'git merge --abort'")
    else:
        print(f"⚠️ Cannot merge: {reason}")
        
        # Provide helpful suggestions
        if "CI not passing" in reason:
            print("💡 Fix failing tests and try again")
        elif "Need" in reason and "reviews" in reason:
            print("💡 Request reviews from team members")
        elif "Tests not passing" in reason:
            print("💡 Run tests locally with appropriate test command")
        elif "conflicts" in reason:
            print("💡 Resolve conflicts first or enable auto-resolution")
```

## Safety Features

### Pre-Merge Checks
- ✅ CI/CD status verification
- ✅ Required reviews obtained
- ✅ Tests passing
- ✅ No merge conflicts (or auto-resolvable)
- ✅ Branch protection rules satisfied

### During Merge
- 🔄 Automatic backup creation
- 🤖 Smart merge strategy selection
- 🔧 Conflict auto-resolution (when safe)
- 📊 Change impact analysis

### Post-Merge
- 🧹 Branch cleanup
- 📝 Merge history tracking
- ⏮️ One-command rollback
- 📢 Team notifications

## Merge Strategies

The system automatically selects the best strategy:

| Branch Type | Strategy | When Used |
|------------|----------|-----------|
| feature/* | recursive | Standard feature merges |
| hotfix/* | ours | Priority fixes |
| release/* | theirs | Release branches |
| Large changes | patience | Better for big refactors |

## Conflict Resolution

When conflicts occur:
1. **Simple conflicts**: Auto-resolved based on patterns
2. **Complex conflicts**: Suggestions provided
3. **Critical conflicts**: Manual intervention required

Configuration options:
- `prefer_incoming`: Keep incoming changes in conflicts
- `auto_resolve_simple`: Attempt automatic resolution
- `backup_before_merge`: Create safety backup

## Rollback

If something goes wrong after merge:
```
/merge rollback
```

This will:
1. Locate the last merge commit
2. Revert all changes safely
3. Restore branch state
4. Preserve commit history

## Examples

### Successful Auto-Merge
```
🔍 Checking merge readiness...
✅ All checks passed!
🔀 Starting merge process...
🎉 Successfully merged feature/user-auth into main
🧹 Branch cleaned up automatically

💡 If needed, rollback with: /merge rollback
```

### Blocked Merge
```
⚠️ Cannot merge: Need 2 reviews, have 1
💡 Request reviews from team members
```

### Conflict Resolution
```
⚠️ Cannot merge: Has conflicts and auto-resolution disabled
🔧 Conflicts detected. Options:
  1. Fix conflicts manually
  2. Enable auto-resolution in config
  3. Abort with 'git merge --abort'
```

## Configuration

Customize in `.git/smart-genie-merge.json`:
```json
{
  "auto_merge": true,
  "auto_merge_rules": {
    "require_ci_pass": true,
    "require_reviews": true,
    "min_reviews": 1,
    "require_tests": true,
    "auto_cleanup": true
  },
  "conflict_resolution": {
    "auto_resolve_simple": true,
    "prefer_incoming": false,
    "backup_before_merge": true
  }
}
```

## Tips
- Always ensure CI is green before merging
- Use `/review` first to catch issues
- Enable auto-resolution for smoother merges
- Keep backups enabled for safety
- Rollback immediately if issues detected