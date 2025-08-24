#!/usr/bin/env python3
"""
Git Intelligence Orchestrator Hook
Master coordinator for all Smart Commit Genie features
Runs appropriate automation based on git state and Claude context
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add git-intelligence to path
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

# Import all managers
from auto_branching import AutoBranchManager
from auto_pr import AutoPRManager
from pr_reviewer import PRAutoReviewer
from smart_merge import SmartMergeManager
from failure_prevention import FailurePreventionSystem


class GitIntelligenceOrchestrator:
    """Orchestrates all git intelligence features"""
    
    def __init__(self):
        self.config_file = Path.home() / ".claude" / "smart-genie-orchestrator.json"
        self.load_config()
        self.state = self.analyze_git_state()
        
    def load_config(self):
        """Load orchestrator configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "enabled": True,
                "features": {
                    "auto_branch": True,
                    "auto_pr": True,
                    "auto_review": True,
                    "auto_merge": True,
                    "auto_validate": True
                },
                "triggers": {
                    "on_file_change": True,
                    "on_commit": True,
                    "on_push": True,
                    "on_pr": True,
                    "periodic": True
                },
                "intelligence": {
                    "learn_patterns": True,
                    "suggest_improvements": True,
                    "detect_issues": True
                }
            }
            
    def save_config(self):
        """Save orchestrator configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def analyze_git_state(self):
        """Analyze current git repository state"""
        state = {
            "has_changes": False,
            "has_staged": False,
            "has_commits": False,
            "on_feature_branch": False,
            "pr_exists": False,
            "merge_in_progress": False,
            "branch_info": {},
            "context": {}
        }
        
        try:
            # Check for changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                state["has_changes"] = True
                
                # Check for staged changes
                lines = result.stdout.strip().split('\n')
                state["has_staged"] = any(line[0] in 'MADRC' for line in lines if line)
            
            # Get branch info
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                state["branch_info"]["name"] = branch
                state["on_feature_branch"] = branch not in ["main", "master", "develop"]
            
            # Check for unpushed commits
            if state["on_feature_branch"]:
                result = subprocess.run(
                    ["git", "log", "origin/main..HEAD", "--oneline"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    state["has_commits"] = True
                    state["branch_info"]["commits"] = len(result.stdout.strip().split('\n'))
            
            # Check for merge in progress
            state["merge_in_progress"] = (Path(".git") / "MERGE_HEAD").exists()
            
            # Get Claude context
            state["context"]["task"] = os.environ.get("CLAUDE_CURRENT_TASK", "")
            state["context"]["session_id"] = os.environ.get("CLAUDE_SESSION_ID", "")
            
        except:
            pass
            
        return state
        
    def determine_actions(self):
        """Determine which actions to take based on state"""
        actions = []
        
        if not self.config["enabled"]:
            return actions
        
        features = self.config["features"]
        
        # Branch creation logic
        if features["auto_branch"]:
            if not self.state["on_feature_branch"] and self.state["has_changes"]:
                if len(self.get_changed_files()) >= 2:
                    actions.append("create_branch")
        
        # Validation logic
        if features["auto_validate"]:
            if self.state["has_staged"]:
                actions.append("validate")
        
        # PR creation logic
        if features["auto_pr"]:
            if self.state["on_feature_branch"] and self.state["has_commits"]:
                if self.state["branch_info"].get("commits", 0) >= 3:
                    if not self.check_pr_exists():
                        actions.append("suggest_pr")
        
        # Review logic
        if features["auto_review"]:
            if self.check_pr_exists():
                actions.append("review_pr")
        
        # Merge logic
        if features["auto_merge"]:
            if self.state["merge_in_progress"]:
                actions.append("check_merge_safety")
        
        return actions
        
    def get_changed_files(self):
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split('\n') if f]
        except:
            pass
        return []
        
    def check_pr_exists(self):
        """Check if PR exists for current branch"""
        if not self.state["on_feature_branch"]:
            return False
            
        try:
            branch = self.state["branch_info"]["name"]
            result = subprocess.run(
                ["gh", "pr", "list", "--head", branch, "--json", "number"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                return len(prs) > 0
        except:
            pass
            
        return False
        
    def execute_actions(self, actions):
        """Execute determined actions"""
        results = []
        
        for action in actions:
            try:
                if action == "create_branch":
                    manager = AutoBranchManager()
                    context = {
                        "changed_files": self.get_changed_files(),
                        "current_task": self.state["context"]["task"]
                    }
                    result = manager.auto_branch(context)
                    if result:
                        results.append(f"Created branch: {result}")
                        
                elif action == "validate":
                    prevention = FailurePreventionSystem()
                    result = prevention.pre_commit_checks()
                    if not result["passed"]:
                        results.append("Validation issues found - see details above")
                        
                elif action == "suggest_pr":
                    results.append("Branch ready for PR - use /pr to create")
                    
                elif action == "review_pr":
                    reviewer = PRAutoReviewer()
                    result = reviewer.review_pr()
                    if result["reviewed"]:
                        results.append("PR reviewed automatically")
                        
                elif action == "check_merge_safety":
                    manager = SmartMergeManager()
                    backup_id = manager.create_backup()
                    if backup_id:
                        results.append(f"Merge backup created: {backup_id}")
                        
            except Exception as e:
                if os.environ.get("CLAUDE_DEBUG") == "true":
                    results.append(f"Error in {action}: {e}")
                    
        return results
        
    def learn_patterns(self):
        """Learn from user patterns and improve suggestions"""
        if not self.config["intelligence"]["learn_patterns"]:
            return
        
        try:
            # Analyze commit patterns
            result = subprocess.run(
                ["git", "log", "--pretty=format:%s", "-20"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                
                # Learn commit message patterns
                patterns = {}
                for commit in commits:
                    # Extract pattern (e.g., "feat:", "fix:", etc.)
                    if ':' in commit:
                        prefix = commit.split(':')[0].lower()
                        patterns[prefix] = patterns.get(prefix, 0) + 1
                
                # Save learned patterns
                if patterns:
                    learned_file = Path.home() / ".claude" / "smart-genie-learned.json"
                    
                    if learned_file.exists():
                        with open(learned_file, 'r') as f:
                            learned = json.load(f)
                    else:
                        learned = {"commit_patterns": {}, "branch_patterns": {}}
                    
                    # Update patterns
                    for pattern, count in patterns.items():
                        learned["commit_patterns"][pattern] = \
                            learned["commit_patterns"].get(pattern, 0) + count
                    
                    with open(learned_file, 'w') as f:
                        json.dump(learned, f, indent=2)
                        
        except:
            pass
            
    def suggest_improvements(self):
        """Suggest workflow improvements based on patterns"""
        suggestions = []
        
        if not self.config["intelligence"]["suggest_improvements"]:
            return suggestions
        
        # Check for common issues
        if self.state["has_changes"] and not self.state["has_staged"]:
            # Many unstaged changes
            changed_files = self.get_changed_files()
            if len(changed_files) > 10:
                suggestions.append("Consider breaking changes into smaller commits")
        
        # Check commit frequency
        if self.state["on_feature_branch"]:
            commits = self.state["branch_info"].get("commits", 0)
            if commits > 20:
                suggestions.append("Large branch - consider creating PR soon")
            elif commits == 1:
                suggestions.append("Single commit - add more context with additional commits")
        
        return suggestions
        
    def run(self):
        """Main orchestration logic"""
        try:
            # Determine what actions to take
            actions = self.determine_actions()
            
            # Execute actions
            if actions:
                results = self.execute_actions(actions)
                
                # Display results if any
                if results and os.environ.get("CLAUDE_VERBOSE") == "true":
                    print("\n🤖 Git Intelligence Active:")
                    for result in results:
                        print(f"   • {result}")
            
            # Learn from patterns
            self.learn_patterns()
            
            # Suggest improvements
            suggestions = self.suggest_improvements()
            if suggestions and os.environ.get("CLAUDE_SUGGESTIONS") != "false":
                print("\n💡 Workflow Suggestions:")
                for suggestion in suggestions:
                    print(f"   • {suggestion}")
            
            # Log activity
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "state": {
                    "branch": self.state["branch_info"].get("name", "unknown"),
                    "has_changes": self.state["has_changes"],
                    "has_commits": self.state["has_commits"]
                },
                "actions": actions,
                "suggestions": suggestions
            }
            
            log_file = Path.home() / ".claude" / "smart-genie-orchestrator.log"
            log_file.parent.mkdir(exist_ok=True)
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            if os.environ.get("CLAUDE_DEBUG") == "true":
                print(f"Orchestrator error: {e}")


def main():
    """Main entry point"""
    # Check if orchestrator is disabled
    if os.environ.get("CLAUDE_DISABLE_GIT_INTELLIGENCE") == "true":
        return
    
    # Run orchestrator
    orchestrator = GitIntelligenceOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()