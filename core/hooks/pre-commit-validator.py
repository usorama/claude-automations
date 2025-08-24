#!/usr/bin/env python3
"""
Pre-Commit Validator Hook
Automatically validates code before commits to prevent failures
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add git-intelligence to path
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from failure_prevention import FailurePreventionSystem


def should_run():
    """Check if validation should run"""
    # Check if disabled
    if os.environ.get("CLAUDE_SKIP_VALIDATION") == "true":
        return False
    
    # Check if we have staged files
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            files = result.stdout.strip()
            return bool(files)
    except:
        pass
    
    return False


def main():
    """Main hook execution"""
    try:
        if not should_run():
            return
        
        # Initialize prevention system
        prevention = FailurePreventionSystem()
        
        # Run validation
        results = prevention.pre_commit_checks()
        
        if results.get('skipped'):
            return
        
        # Check if we had any failures
        if not results['passed']:
            print("\n⚠️ Pre-commit validation found issues:")
            
            # Show summary of failures
            for check in results['checks']:
                if not check['passed']:
                    print(f"  ❌ {check['check'].upper()}")
                    
                    # Show first error for each check
                    if check.get('errors') and len(check['errors']) > 0:
                        error = check['errors'][0]
                        if isinstance(error, dict):
                            print(f"     {error.get('file', '')}: {error.get('error', error.get('issue', ''))}")
                    elif check.get('issues'):
                        issue = check['issues'][0]
                        print(f"     {issue.get('file', '')}: {issue.get('issue', '')}")
                    elif check.get('large_files'):
                        file = check['large_files'][0]
                        print(f"     {file['file']}: {file['size_mb']} MB")
            
            # Check if we applied any fixes
            if results.get('fixes_applied'):
                print("\n🔧 Auto-fixes were applied:")
                for fix in results['fixes_applied']:
                    if fix.get('actions'):
                        for action in fix['actions']:
                            print(f"  ✅ {action}")
                print("\n💡 Review changes and stage fixed files if needed")
            else:
                print("\n💡 Fix issues manually or run /validate for details")
        else:
            # Silent success - don't interrupt flow
            if results.get('fixes_applied'):
                print("\n✅ Pre-commit validation passed (after auto-fixes)")
                
        # Log the validation
        log_entry = {
            "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
            "action": "pre_commit_validation",
            "passed": results['passed'],
            "checks_run": len(results.get('checks', [])),
            "fixes_applied": len(results.get('fixes_applied', []))
        }
        
        # Write to log
        log_file = Path.home() / ".claude" / "smart-genie-validation.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception as e:
        # Silent failure - don't block commits
        if os.environ.get("CLAUDE_DEBUG") == "true":
            print(f"Pre-commit validator error: {e}")


if __name__ == "__main__":
    main()