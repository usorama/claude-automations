---
command: review
description: Perform automated code review with security and performance checks
---

Run an intelligent automated code review on the current branch or a specific PR.

## Usage
- `/review` - Review current branch changes
- `/review 123` - Review specific PR number

## How it works
```python
import sys
import json
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from pr_reviewer import PRAutoReviewer

# Parse PR number if provided
pr_number = None
if "{{PR_NUMBER}}":  # Claude will fill this if provided
    pr_number = int("{{PR_NUMBER}}")

# Initialize reviewer
reviewer = PRAutoReviewer()

print("🔍 Starting automated code review...")
print("=" * 50)

# Perform review
result = reviewer.review_pr(pr_number)

if result['reviewed']:
    # Display summary
    print(result['summary'])
    
    # Display comments by type
    if result['comments']:
        print("\n## Detailed Findings\n")
        
        # Group by severity
        high_priority = [c for c in result['comments'] if c.get('severity') == 'high']
        medium_priority = [c for c in result['comments'] if c.get('severity') == 'medium']
        low_priority = [c for c in result['comments'] if c.get('severity') == 'low']
        positive = [c for c in result['comments'] if c['type'] == 'positive']
        
        if high_priority:
            print("🔴 **High Priority Issues**")
            for comment in high_priority[:5]:
                print(f"  - {comment['file']}: {comment['message']}")
                if comment.get('suggestion'):
                    print(f"    💡 {comment['suggestion']}")
            print()
            
        if medium_priority:
            print("🟡 **Medium Priority Issues**")
            for comment in medium_priority[:5]:
                print(f"  - {comment['file']}: {comment['message']}")
            print()
            
        if low_priority:
            print("🟢 **Suggestions**")
            for comment in low_priority[:5]:
                print(f"  - {comment['message']}")
            print()
            
        if positive:
            print("✨ **Good Practices Found**")
            for comment in positive[:3]:
                print(f"  - {comment['message']}")
            print()
    else:
        print("\n🎉 No issues found - great work!")
        
    # Post result
    if pr_number and result.get('result', {}).get('success'):
        print(f"\n✅ Review posted to PR #{pr_number}")
else:
    print(f"❌ Could not review: {result.get('reason', 'Unknown error')}")
```

## Review Checks

### 🔐 Security
- API key exposure
- Hardcoded passwords/tokens
- Dangerous functions (eval, exec)
- SQL injection risks
- Insecure dependencies

### 🚀 Performance
- Nested loops
- N+1 queries
- Large file operations
- Inefficient algorithms
- Memory leaks

### 📝 Best Practices
- Code style consistency
- Error handling
- Import organization
- Variable naming
- Documentation

### 🧪 Testing
- Test coverage
- New functions without tests
- Test quality
- Edge cases

### 📚 Documentation
- Missing docstrings
- Outdated comments
- TODO tracking
- API documentation

## Review Output Example
```
## Automated Review Summary

📊 Files reviewed: 12
💬 Comments: 8

🔴 High priority: 2 issues
🟡 Medium priority: 3 issues
🟢 Low priority: 2 suggestions
✨ Positive findings: 1

⚠️ Status: Please address high-priority issues before merging

### Details:

🔴 `config.py` 🔐 Potential API key exposure
   💡 Suggestion: Store API keys in environment variables

🟡 `handlers.py` 🚀 Consider optimizing nested loops
   💡 Suggestion: Use vectorized operations

✅ `tests/test_auth.py` Good: Comprehensive test coverage
```

## Features
- **Multi-language support**: Python, JavaScript, TypeScript, and more
- **Contextual suggestions**: Provides fixes for identified issues
- **Positive reinforcement**: Highlights good practices
- **Severity levels**: Prioritizes issues by importance
- **Auto-posting**: Posts reviews directly to GitHub PRs

## Tips
- Run before creating PR to catch issues early
- Reviews are non-blocking but highly recommended
- High-priority issues should be addressed immediately
- Use with `/merge` for safe auto-merging