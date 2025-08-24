#!/usr/bin/env python3
"""
PR Ready Detector Hook
Detects when a branch is ready for PR and suggests creation
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Add git-intelligence to path
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from auto_pr import AutoPRManager
from auto_branching import AutoBranchManager


def get_branch_info():
    """Get information about current branch"""
    info = {
        "name": "",
        "commits": 0,
        "age_hours": 0,
        "unpushed": 0
    }
    
    try:
        # Get current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            info["name"] = result.stdout.strip()
        
        # Skip if on main branch
        if info["name"] in ["main", "master", "develop"]:
            return None
        
        # Count commits ahead of main
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD", "^main"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            info["commits"] = int(result.stdout.strip())
        
        # Get branch age
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            timestamp = int(result.stdout.strip())
            age = datetime.now() - datetime.fromtimestamp(timestamp)
            info["age_hours"] = age.total_seconds() / 3600
        
        # Count unpushed commits
        try:
            result = subprocess.run(
                ["git", "log", f"origin/{info['name']}..HEAD", "--oneline"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                info["unpushed"] = len(result.stdout.strip().split('\n'))
        except:
            # Branch might not exist on origin
            info["unpushed"] = info["commits"]
            
    except:
        return None
    
    return info


def should_suggest_pr(branch_info):
    """Determine if we should suggest creating a PR"""
    if not branch_info:
        return False
    
    # Criteria for suggesting PR
    criteria = [
        branch_info["commits"] >= 3,  # At least 3 commits
        branch_info["age_hours"] >= 2,  # At least 2 hours old
        branch_info["unpushed"] >= 2,  # Has unpushed work
    ]
    
    # Need at least 2 criteria met
    return sum(criteria) >= 2


def check_pr_exists(branch_name):
    """Check if PR already exists for branch"""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--head", branch_name, "--json", "number"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            prs = json.loads(result.stdout)
            return len(prs) > 0
    except:
        pass
    
    return False


def main():
    """Main hook execution"""
    try:
        # Check if we should run
        if os.environ.get("CLAUDE_DISABLE_PR_SUGGESTIONS") == "true":
            return
        
        # Get branch information
        branch_info = get_branch_info()
        
        if not branch_info:
            return
        
        # Check if PR already exists
        if check_pr_exists(branch_info["name"]):
            return
        
        # Check if we should suggest PR
        if should_suggest_pr(branch_info):
            print(f"\n📊 Branch Status: {branch_info['name']}")
            print(f"   • {branch_info['commits']} commits")
            print(f"   • {branch_info['unpushed']} unpushed")
            print(f"   • {int(branch_info['age_hours'])} hours old")
            print("\n🎯 This branch appears ready for a pull request!")
            print("   Use /pr to create one with auto-generated description")
            
            # Check if we should also run review
            pr_manager = AutoPRManager()
            should_create, reason = pr_manager.should_create_pr()
            
            if should_create:
                print("\n✅ All PR requirements met - ready to create")
            else:
                print(f"\n⚠️ Note: {reason}")
            
            # Log the suggestion
            log_entry = {
                "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
                "action": "pr_suggestion",
                "branch": branch_info["name"],
                "stats": {
                    "commits": branch_info["commits"],
                    "unpushed": branch_info["unpushed"],
                    "age_hours": branch_info["age_hours"]
                }
            }
            
            # Write to log
            log_file = Path.home() / ".claude" / "smart-genie-pr-suggestions.log"
            log_file.parent.mkdir(exist_ok=True)
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
                
    except Exception as e:
        # Silent failure
        if os.environ.get("CLAUDE_DEBUG") == "true":
            print(f"PR ready detector error: {e}")


if __name__ == "__main__":
    main()