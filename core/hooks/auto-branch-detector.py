#!/usr/bin/env python3
"""
Auto-Branch Detector Hook
Automatically creates branches when detecting new feature work
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add git-intelligence to path
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from auto_branching import AutoBranchManager


def get_claude_context():
    """Get context from Claude environment"""
    context = {
        "changed_files": [],
        "current_task": os.environ.get("CLAUDE_CURRENT_TASK", ""),
        "last_commit_msg": "",
        "new_feature": False,
        "fixing_bug": False
    }
    
    # Get changed files
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            context["changed_files"] = [f for f in result.stdout.strip().split('\n') if f]
    except:
        pass
    
    # Get last commit message
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            context["last_commit_msg"] = result.stdout.strip()
    except:
        pass
    
    # Detect work type from Claude's current activity
    task_lower = context["current_task"].lower()
    context["new_feature"] = any(word in task_lower for word in ["implement", "create", "add", "feature"])
    context["fixing_bug"] = any(word in task_lower for word in ["fix", "bug", "error", "issue"])
    
    return context


def main():
    """Main hook execution"""
    try:
        # Check if we should run
        if os.environ.get("CLAUDE_DISABLE_AUTO_BRANCH") == "true":
            return
        
        # Get context
        context = get_claude_context()
        
        # Skip if not enough changes
        if len(context["changed_files"]) < 2:
            return
        
        # Initialize branch manager
        manager = AutoBranchManager()
        
        # Check current branch
        current_branch = manager.get_current_branch()
        
        # Only create branch if on main/master/develop
        if current_branch not in ["main", "master", "develop"]:
            # Check if we should suggest merge
            merge_suggestion = manager.suggest_branch_merge()
            if merge_suggestion:
                print(f"\n💡 Branch '{merge_suggestion['branch']}' has {merge_suggestion['commits']} commits")
                print("   Consider creating a PR with /pr command")
            return
        
        # Attempt auto-branching
        new_branch = manager.auto_branch(context)
        
        if new_branch:
            print(f"\n🌿 Auto-created branch: {new_branch}")
            print("   Continue working - commits will go to this branch")
            print("   Use /pr when ready to create pull request")
            
            # Log the action
            log_entry = {
                "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
                "action": "auto_branch",
                "branch": new_branch,
                "context": {
                    "files_changed": len(context["changed_files"]),
                    "task": context["current_task"][:100] if context["current_task"] else "unknown"
                }
            }
            
            # Write to log
            log_file = Path.home() / ".claude" / "smart-genie-auto-branch.log"
            log_file.parent.mkdir(exist_ok=True)
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
                
    except Exception as e:
        # Silent failure - don't interrupt Claude's workflow
        if os.environ.get("CLAUDE_DEBUG") == "true":
            print(f"Auto-branch hook error: {e}")


if __name__ == "__main__":
    main()