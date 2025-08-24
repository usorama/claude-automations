#!/usr/bin/env python3
"""
Auto-Branching System for Smart Commit Genie
Automatically detects when to create new branches and switches seamlessly
"""

import os
import re
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
from analytics import track_feature_usage, track_automation_success, measure_impact

class AutoBranchManager:
    """Manages automatic branch creation and switching"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config_file = self.repo_path / ".git" / "smart-genie-branch.json"
        self.load_config()
        
    def load_config(self):
        """Load branching configuration and history"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "auto_branch": True,
                "branch_history": [],
                "patterns": {
                    "feature": ["feat", "feature", "add", "implement", "create"],
                    "bugfix": ["fix", "bug", "patch", "repair", "resolve"],
                    "hotfix": ["hotfix", "critical", "urgent", "emergency"],
                    "refactor": ["refactor", "cleanup", "reorganize", "restructure"],
                    "docs": ["docs", "documentation", "readme", "guide"],
                    "test": ["test", "spec", "testing", "coverage"],
                    "chore": ["chore", "maintenance", "deps", "dependencies"]
                }
            }
            
    def save_config(self):
        """Save branching configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def detect_work_type(self, context: Dict) -> str:
        """Detect the type of work being done"""
        # Check recent file changes
        changed_files = context.get("changed_files", [])
        commit_msg = context.get("last_commit_msg", "")
        current_task = context.get("current_task", "")
        
        # Combine all context for analysis
        context_text = f"{commit_msg} {current_task} {' '.join(changed_files)}".lower()
        
        # Score each work type
        scores = {}
        for work_type, keywords in self.config["patterns"].items():
            score = sum(1 for keyword in keywords if keyword in context_text)
            if score > 0:
                scores[work_type] = score
                
        # Return highest scoring type or default to feature
        if scores:
            return max(scores, key=scores.get)
        return "feature"
        
    def should_create_branch(self, context: Dict) -> bool:
        """Determine if a new branch should be created"""
        if not self.config["auto_branch"]:
            return False
            
        # Check if we're on main/master
        current_branch = self.get_current_branch()
        if current_branch not in ["main", "master", "develop"]:
            return False
            
        # Check for significant changes
        changed_files = context.get("changed_files", [])
        if len(changed_files) < 2:  # Minor changes don't need new branch
            return False
            
        # Check if work seems to be starting (not finishing)
        if context.get("completing_work", False):
            return False
            
        # Look for indicators of new work
        indicators = [
            len(changed_files) >= 2,
            context.get("new_feature", False),
            context.get("fixing_bug", False),
            "TODO" in context.get("current_task", ""),
            "implement" in context.get("current_task", "").lower(),
            "create" in context.get("current_task", "").lower(),
            "add" in context.get("current_task", "").lower()
        ]
        
        return sum(indicators) >= 2
        
    def generate_branch_name(self, context: Dict) -> str:
        """Generate an intelligent branch name"""
        work_type = self.detect_work_type(context)
        
        # Extract key terms from context
        task = context.get("current_task", "")
        files = context.get("changed_files", [])
        
        # Clean and extract main topic
        topic = self._extract_topic(task, files)
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%m%d")
        
        # Generate branch name
        branch_name = f"{work_type}/{topic}-{timestamp}"
        
        # Ensure branch name is valid
        branch_name = re.sub(r'[^a-zA-Z0-9/_-]', '-', branch_name)
        branch_name = re.sub(r'-+', '-', branch_name)
        branch_name = branch_name.strip('-')
        
        # Ensure uniqueness
        if self.branch_exists(branch_name):
            hash_suffix = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:4]
            branch_name = f"{branch_name}-{hash_suffix}"
            
        return branch_name
        
    def _extract_topic(self, task: str, files: List[str]) -> str:
        """Extract the main topic from task and files"""
        # Try to extract from task description
        if task:
            # Remove common words
            stop_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                         "of", "with", "by", "from", "as", "is", "was", "are", "were"]
            words = task.lower().split()
            words = [w for w in words if w not in stop_words and len(w) > 2]
            if words:
                return "-".join(words[:3])  # Take first 3 meaningful words
                
        # Fall back to file analysis
        if files:
            # Find common directory or component
            common_parts = []
            for file in files[:3]:  # Look at first 3 files
                parts = Path(file).parts
                if parts:
                    common_parts.extend(parts)
                    
            if common_parts:
                # Find most common non-generic part
                from collections import Counter
                counter = Counter(common_parts)
                for part, _ in counter.most_common():
                    if part not in ["src", "lib", "test", "docs", ".", ".."]:
                        return part
                        
        return "update"
        
    def create_and_switch_branch(self, branch_name: str, context: Dict) -> bool:
        """Create a new branch and switch to it"""
        try:
            # Create branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Record in history
                self.config["branch_history"].append({
                    "branch": branch_name,
                    "created": datetime.now().isoformat(),
                    "context": {
                        "task": context.get("current_task", ""),
                        "files": context.get("changed_files", [])[:5]  # Store first 5 files
                    }
                })
                self.save_config()
                return True
                
        except Exception as e:
            print(f"Error creating branch: {e}")
            
        return False
        
    def get_current_branch(self) -> str:
        """Get the current branch name"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "main"
        
    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch already exists"""
        try:
            result = subprocess.run(
                ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
            
    def auto_branch(self, context: Dict) -> Optional[str]:
        """Main auto-branching logic"""
        start_time = time.time()
        
        try:
            if not self.should_create_branch(context):
                track_feature_usage("auto_branch", start_time, True, {"reason": "not_needed"})
                return None
                
            branch_name = self.generate_branch_name(context)
            
            if self.create_and_switch_branch(branch_name, context):
                track_feature_usage("auto_branch", start_time, True, {
                    "branch_name": branch_name,
                    "files_changed": len(context.get("changed_files", []))
                })
                track_automation_success("auto_branch", {"branch": branch_name})
                measure_impact("manual_branch_time", 30.0, 2.0, "auto_branch_creation")
                return branch_name
            else:
                track_feature_usage("auto_branch", start_time, False, {"reason": "creation_failed"})
                
        except Exception as e:
            track_feature_usage("auto_branch", start_time, False, {"error": str(e)})
            
        return None
        
    def suggest_branch_merge(self) -> Optional[Dict]:
        """Suggest when a branch might be ready to merge"""
        current_branch = self.get_current_branch()
        
        if current_branch in ["main", "master", "develop"]:
            return None
            
        # Check branch age and activity
        try:
            # Get branch creation time
            result = subprocess.run(
                ["git", "log", "--format=%cr", "-n", "1", "--reverse", f"{current_branch}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if "hour" in result.stdout or "day" in result.stdout:
                # Check commit count
                result = subprocess.run(
                    ["git", "rev-list", "--count", f"HEAD...origin/main"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                commit_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
                
                if commit_count >= 3:  # Enough work done
                    return {
                        "branch": current_branch,
                        "commits": commit_count,
                        "suggestion": "Branch appears ready for PR"
                    }
                    
        except:
            pass
            
        return None
        
    def cleanup_merged_branches(self):
        """Clean up branches that have been merged"""
        try:
            # Get merged branches
            result = subprocess.run(
                ["git", "branch", "--merged", "main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                branches = result.stdout.strip().split('\n')
                for branch in branches:
                    branch = branch.strip().replace('*', '').strip()
                    if branch and branch not in ["main", "master", "develop"]:
                        # Delete merged branch
                        subprocess.run(
                            ["git", "branch", "-d", branch],
                            cwd=self.repo_path,
                            capture_output=True
                        )
                        
        except:
            pass


class BranchPatternLearner:
    """Learns from team branching patterns"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.patterns_file = self.repo_path / ".git" / "learned-branch-patterns.json"
        self.load_patterns()
        
    def load_patterns(self):
        """Load learned patterns"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                self.patterns = json.load(f)
        else:
            self.patterns = {
                "naming_patterns": {},
                "work_associations": {},
                "user_preferences": {}
            }
            
    def save_patterns(self):
        """Save learned patterns"""
        self.patterns_file.parent.mkdir(exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
            
    def learn_from_history(self):
        """Learn from git branch history"""
        try:
            # Get all branches
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                branches = result.stdout.strip().split('\n')
                
                for branch in branches:
                    branch = branch.strip().replace('*', '').strip()
                    if '/' in branch:
                        # Extract pattern
                        parts = branch.split('/')
                        if len(parts) >= 2:
                            prefix = parts[0].replace('remotes/origin/', '')
                            if prefix not in ["HEAD", "main", "master"]:
                                self.patterns["naming_patterns"][prefix] = \
                                    self.patterns["naming_patterns"].get(prefix, 0) + 1
                                    
        except:
            pass
            
        self.save_patterns()
        
    def suggest_branch_prefix(self, context: Dict) -> Optional[str]:
        """Suggest branch prefix based on learned patterns"""
        if self.patterns["naming_patterns"]:
            # Find most common pattern matching context
            context_text = str(context).lower()
            
            for prefix, count in sorted(self.patterns["naming_patterns"].items(), 
                                       key=lambda x: x[1], reverse=True):
                if prefix.lower() in context_text or \
                   any(word in prefix.lower() for word in context_text.split()):
                    return prefix
                    
        return None


def integrate_with_claude_code():
    """Integration point for Claude Code"""
    # This will be called by hooks and commands
    
    # Get current context
    context = {
        "changed_files": get_changed_files(),
        "current_task": get_current_task(),
        "last_commit_msg": get_last_commit_message()
    }
    
    # Initialize manager
    manager = AutoBranchManager()
    
    # Check if we should auto-branch
    new_branch = manager.auto_branch(context)
    
    if new_branch:
        return {
            "action": "created_branch",
            "branch": new_branch,
            "message": f"Auto-created branch: {new_branch}"
        }
        
    # Check if we should suggest merge
    merge_suggestion = manager.suggest_branch_merge()
    if merge_suggestion:
        return {
            "action": "suggest_merge",
            "suggestion": merge_suggestion
        }
        
    return {"action": "none"}


def get_changed_files() -> List[str]:
    """Get list of changed files"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
    except:
        pass
    return []


def get_current_task() -> str:
    """Get current task from Claude context"""
    # This would integrate with Claude's task context
    # For now, return empty
    return os.environ.get("CLAUDE_CURRENT_TASK", "")


def get_last_commit_message() -> str:
    """Get last commit message"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return ""


if __name__ == "__main__":
    # Run auto-branching
    result = integrate_with_claude_code()
    print(json.dumps(result, indent=2))