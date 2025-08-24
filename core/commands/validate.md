---
command: validate
description: Pre-commit validation to prevent failures before they happen
---

Run comprehensive validation checks before committing to prevent common failures.

## Usage
Type `/validate` to:
1. Check syntax errors
2. Run linting
3. Scan for security issues
4. Detect large files
5. Find exposed credentials
6. Verify imports
7. Auto-fix issues when possible

## How it works
```python
import sys
import json
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from failure_prevention import FailurePreventionSystem

# Initialize prevention system
prevention = FailurePreventionSystem()

print("🛡️ Running pre-commit validation...")
print("=" * 50)

# Run checks
results = prevention.pre_commit_checks()

if results.get('skipped'):
    print("⏭️ Validation skipped (disabled in config)")
else:
    # Display results
    total_checks = len(results['checks'])
    passed = sum(1 for c in results['checks'] if c['passed'])
    
    print(f"\n📊 Validation Summary")
    print(f"  Checks run: {total_checks}")
    print(f"  Passed: {passed}/{total_checks}")
    
    if results['fixes_applied']:
        print(f"\n🔧 Auto-fixes Applied: {len(results['fixes_applied'])}")
        for fix in results['fixes_applied']:
            if fix.get('fixed_files'):
                print(f"  ✅ Fixed {len(fix['fixed_files'])} files")
            if fix.get('actions'):
                for action in fix['actions']:
                    print(f"  ✅ {action}")
    
    # Show check details
    print("\n📋 Check Results:")
    
    for check in results['checks']:
        icon = "✅" if check['passed'] else "❌"
        print(f"\n{icon} {check['check'].upper()}")
        
        if not check['passed']:
            if check.get('errors'):
                for error in check['errors'][:3]:  # Show first 3 errors
                    if isinstance(error, dict):
                        print(f"  • {error.get('file', '')}: {error.get('error', error.get('issue', ''))}")
                    else:
                        print(f"  • {error}")
                        
                if len(check.get('errors', [])) > 3:
                    print(f"  • ...and {len(check['errors']) - 3} more")
                    
            elif check.get('issues'):
                for issue in check['issues'][:3]:
                    print(f"  • {issue.get('file', '')}: {issue.get('issue', '')}")
                    
            elif check.get('large_files'):
                for file in check['large_files']:
                    print(f"  • {file['file']}: {file['size_mb']} MB")
                    
            elif check.get('exposed'):
                for item in check['exposed']:
                    print(f"  • {item['file']}: {item['issue']}")
                    
        elif check.get('warning'):
            print(f"  ⚠️ {check['warning']}")
            
        if check.get('todos'):
            print(f"  📝 Found {len(check['todos'])} TODO comments")
            for todo in check['todos'][:2]:
                print(f"    • {todo['file']}:{todo['line']} - {todo['content'][:50]}...")
    
    # Final status
    print("\n" + "=" * 50)
    if results['passed']:
        print("✅ All validations passed! Ready to commit.")
        print("💡 Use /commit to create an intelligent commit")
    else:
        print("❌ Validation failed. Please fix issues before committing.")
        print("\n🔧 Suggested actions:")
        
        # Provide specific suggestions
        for check in results['checks']:
            if not check['passed']:
                if check['check'] == 'syntax':
                    print("  • Fix syntax errors in affected files")
                elif check['check'] == 'linting':
                    print("  • Run auto-formatter (black, prettier, etc.)")
                elif check['check'] == 'security':
                    print("  • Move secrets to environment variables")
                elif check['check'] == 'large_files':
                    print("  • Add large files to .gitignore or use Git LFS")
                elif check['check'] == 'credentials':
                    print("  • Add sensitive files to .gitignore")
                elif check['check'] == 'imports':
                    print("  • Install missing dependencies")
```

## Validation Checks

### 🔍 Syntax Check
- Python syntax validation
- JavaScript/TypeScript parsing
- JSON/YAML structure verification
- Auto-fix simple syntax errors

### 🎨 Linting
- Code style consistency
- Format violations
- Auto-fix with black/prettier
- PEP8/ESLint compliance

### 🔐 Security Scan
- Hardcoded API keys
- Exposed passwords
- Dangerous functions
- Credential leaks

### 📦 Large Files
- Files over 10MB threshold
- Binary files that shouldn't be committed
- Suggestions for Git LFS

### 🔑 Credentials Check
- .env files not in .gitignore
- Config files with secrets
- Private keys exposure

### 📚 Import Verification
- Missing Python modules
- Uninstalled npm packages
- Broken relative imports
- Auto-install option

### 📝 TODO Tracking
- TODO/FIXME comments
- Technical debt markers
- Won't fail validation (informational)

## Auto-Fix Capabilities

When enabled, the system can automatically:
- ✅ Format code with black/prettier
- ✅ Fix simple syntax errors
- ✅ Organize imports
- ✅ Remove trailing whitespace
- ✅ Fix line endings
- ✅ Update .gitignore

## Configuration

Customize in `.git/smart-genie-prevention.json`:
```json
{
  "enabled": true,
  "checks": {
    "pre_commit": {
      "syntax_check": true,
      "lint_check": true,
      "security_scan": true,
      "large_file_check": true,
      "credentials_check": true,
      "broken_imports": true,
      "todo_check": false
    }
  },
  "auto_fix": {
    "enabled": true,
    "fix_formatting": true,
    "fix_imports": true,
    "fix_simple_errors": true
  },
  "thresholds": {
    "max_file_size_mb": 10,
    "min_coverage_percent": 70,
    "max_complexity": 10
  }
}
```

## Examples

### All Checks Passed
```
🛡️ Running pre-commit validation...
==================================================

📊 Validation Summary
  Checks run: 6
  Passed: 6/6

📋 Check Results:

✅ SYNTAX
✅ LINTING
✅ SECURITY
✅ LARGE_FILES
✅ CREDENTIALS
✅ IMPORTS

==================================================
✅ All validations passed! Ready to commit.
💡 Use /commit to create an intelligent commit
```

### Issues Found and Fixed
```
🛡️ Running pre-commit validation...
==================================================

📊 Validation Summary
  Checks run: 6
  Passed: 5/6

🔧 Auto-fixes Applied: 2
  ✅ Python files formatted with black
  ✅ JavaScript files formatted with prettier

📋 Check Results:

✅ SYNTAX
✅ LINTING (after auto-fix)
❌ SECURITY
  • config.py: API key hardcoded
  • settings.js: Token hardcoded
✅ LARGE_FILES
✅ CREDENTIALS
✅ IMPORTS

==================================================
❌ Validation failed. Please fix issues before committing.

🔧 Suggested actions:
  • Move secrets to environment variables
```

## Tips
- Run `/validate` before every commit
- Enable auto-fix for faster development
- Add custom validation rules as needed
- Use with `/commit` for smooth workflow
- Configure thresholds per project needs