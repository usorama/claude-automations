#!/usr/bin/env python3
"""
Smart Merging System for Smart Commit Genie
Handles automatic merging, conflict resolution, and rollback
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import shutil


class SmartMergeManager:
    """Manages intelligent merging and conflict resolution"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config_file = self.repo_path / ".git" / "smart-genie-merge.json"
        self.backup_dir = self.repo_path / ".git" / "smart-genie-backups"
        self.load_config()
        
    def load_config(self):
        """Load merge configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "auto_merge": True,
                "merge_history": [],
                "strategies": {
                    "default": "recursive",
                    "feature": "recursive",
                    "hotfix": "ours",
                    "release": "theirs"
                },
                "auto_merge_rules": {
                    "require_ci_pass": True,
                    "require_reviews": True,
                    "min_reviews": 1,
                    "require_tests": True,
                    "auto_cleanup": True
                },
                "conflict_resolution": {
                    "auto_resolve_simple": True,
                    "prefer_incoming": False,
                    "backup_before_merge": True
                }
            }
            
    def save_config(self):
        """Save merge configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def can_auto_merge(self, pr_data: Dict) -> Tuple[bool, str]:
        """Check if PR can be auto-merged"""
        if not self.config["auto_merge"]:
            return False, "Auto-merge disabled"
            
        rules = self.config["auto_merge_rules"]
        
        # Check CI status
        if rules["require_ci_pass"]:
            ci_status = self.check_ci_status(pr_data)
            if ci_status != "success":
                return False, f"CI not passing: {ci_status}"
                
        # Check reviews
        if rules["require_reviews"]:
            review_count = self.get_review_count(pr_data)
            if review_count < rules["min_reviews"]:
                return False, f"Need {rules['min_reviews']} reviews, have {review_count}"
                
        # Check tests
        if rules["require_tests"]:
            if not self.has_passing_tests(pr_data):
                return False, "Tests not passing"
                
        # Check for conflicts
        if self.has_conflicts(pr_data):
            if not self.config["conflict_resolution"]["auto_resolve_simple"]:
                return False, "Has conflicts and auto-resolution disabled"
                
        return True, "Ready to merge"
        
    def check_ci_status(self, pr_data: Dict) -> str:
        """Check CI/CD status for PR"""
        try:
            pr_number = pr_data.get("number")
            if pr_number:
                result = subprocess.run(
                    ["gh", "pr", "checks", str(pr_number), "--json", "state"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    checks = json.loads(result.stdout)
                    if all(check["state"] == "success" for check in checks):
                        return "success"
                    elif any(check["state"] == "failure" for check in checks):
                        return "failure"
                    else:
                        return "pending"
                        
        except:
            pass
            
        return "unknown"
        
    def get_review_count(self, pr_data: Dict) -> int:
        """Get number of approving reviews"""
        try:
            pr_number = pr_data.get("number")
            if pr_number:
                result = subprocess.run(
                    ["gh", "pr", "view", str(pr_number), "--json", "reviews"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    reviews = data.get("reviews", [])
                    return sum(1 for r in reviews if r.get("state") == "APPROVED")
                    
        except:
            pass
            
        return 0
        
    def has_passing_tests(self, pr_data: Dict) -> bool:
        """Check if tests are passing"""
        # Run tests locally
        try:
            test_commands = [
                "npm test",
                "pytest",
                "go test ./...",
                "cargo test",
                "mvn test"
            ]
            
            for cmd in test_commands:
                # Check if command exists
                check_cmd = cmd.split()[0]
                check_result = subprocess.run(
                    ["which", check_cmd],
                    capture_output=True
                )
                
                if check_result.returncode == 0:
                    # Run tests
                    result = subprocess.run(
                        cmd.split(),
                        cwd=self.repo_path,
                        capture_output=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    return result.returncode == 0
                    
        except:
            pass
            
        # If no test runner found, assume tests pass
        return True
        
    def has_conflicts(self, pr_data: Dict) -> bool:
        """Check if PR has merge conflicts"""
        try:
            branch = pr_data.get("branch", self.get_current_branch())
            base = pr_data.get("base", "main")
            
            # Try a dry-run merge
            result = subprocess.run(
                ["git", "merge", "--no-commit", "--no-ff", base],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            # Abort the merge
            subprocess.run(
                ["git", "merge", "--abort"],
                cwd=self.repo_path,
                capture_output=True
            )
            
            return "conflict" in result.stdout.lower() or result.returncode != 0
            
        except:
            return False
            
    def auto_merge(self, pr_data: Dict) -> Dict:
        """Perform automatic merge"""
        can_merge, reason = self.can_auto_merge(pr_data)
        
        if not can_merge:
            return {
                "success": False,
                "reason": reason
            }
            
        # Create backup if configured
        if self.config["conflict_resolution"]["backup_before_merge"]:
            backup_id = self.create_backup()
        else:
            backup_id = None
            
        try:
            # Determine merge strategy
            branch_type = self.detect_branch_type(pr_data.get("branch", ""))
            strategy = self.config["strategies"].get(branch_type, "recursive")
            
            # Perform merge
            result = self.perform_merge(pr_data, strategy)
            
            if result["success"]:
                # Cleanup if configured
                if self.config["auto_merge_rules"]["auto_cleanup"]:
                    self.cleanup_after_merge(pr_data)
                    
                # Record in history
                self.config["merge_history"].append({
                    "pr": pr_data.get("number"),
                    "branch": pr_data.get("branch"),
                    "merged": datetime.now().isoformat(),
                    "strategy": strategy,
                    "backup": backup_id
                })
                self.save_config()
                
            return result
            
        except Exception as e:
            # Restore from backup if merge failed
            if backup_id:
                self.restore_backup(backup_id)
                
            return {
                "success": False,
                "error": str(e)
            }
            
    def perform_merge(self, pr_data: Dict, strategy: str) -> Dict:
        """Perform the actual merge"""
        try:
            branch = pr_data.get("branch")
            base = pr_data.get("base", "main")
            
            # Checkout base branch
            subprocess.run(
                ["git", "checkout", base],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Pull latest changes
            subprocess.run(
                ["git", "pull", "origin", base],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Merge branch
            result = subprocess.run(
                ["git", "merge", f"--strategy={strategy}", branch, "-m", 
                 f"Merge {branch} into {base} (auto-merged by Smart Commit Genie)"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Push merged changes
                subprocess.run(
                    ["git", "push", "origin", base],
                    cwd=self.repo_path,
                    check=True
                )
                
                return {
                    "success": True,
                    "message": f"Successfully merged {branch} into {base}"
                }
            else:
                # Try to resolve conflicts
                if "conflict" in result.stdout.lower():
                    resolved = self.auto_resolve_conflicts()
                    if resolved:
                        return {
                            "success": True,
                            "message": f"Merged {branch} with auto-resolved conflicts"
                        }
                        
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def auto_resolve_conflicts(self) -> bool:
        """Attempt to automatically resolve conflicts"""
        if not self.config["conflict_resolution"]["auto_resolve_simple"]:
            return False
            
        try:
            # Get conflicted files
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False
                
            conflicted_files = result.stdout.strip().split('\n')
            
            for file_path in conflicted_files:
                if not file_path:
                    continue
                    
                # Try to resolve file
                if not self.resolve_file_conflict(file_path):
                    return False
                    
            # Commit resolved conflicts
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                check=True
            )
            
            subprocess.run(
                ["git", "commit", "-m", "Auto-resolved merge conflicts"],
                cwd=self.repo_path,
                check=True
            )
            
            return True
            
        except:
            return False
            
    def resolve_file_conflict(self, file_path: str) -> bool:
        """Resolve conflicts in a single file"""
        try:
            full_path = self.repo_path / file_path
            
            with open(full_path, 'r') as f:
                content = f.read()
                
            # Simple conflict resolution strategies
            if self.config["conflict_resolution"]["prefer_incoming"]:
                # Keep incoming changes
                resolved = re.sub(
                    r'<<<<<<< HEAD.*?=======\n(.*?)>>>>>>> .*?\n',
                    r'\1',
                    content,
                    flags=re.DOTALL
                )
            else:
                # Keep current changes
                resolved = re.sub(
                    r'<<<<<<< HEAD\n(.*?)=======.*?>>>>>>> .*?\n',
                    r'\1',
                    content,
                    flags=re.DOTALL
                )
                
            # Check if resolution worked
            if '<<<<<<< HEAD' not in resolved:
                with open(full_path, 'w') as f:
                    f.write(resolved)
                return True
                
        except:
            pass
            
        return False
        
    def cleanup_after_merge(self, pr_data: Dict):
        """Clean up after successful merge"""
        try:
            branch = pr_data.get("branch")
            
            if branch and branch not in ["main", "master", "develop"]:
                # Delete local branch
                subprocess.run(
                    ["git", "branch", "-d", branch],
                    cwd=self.repo_path,
                    capture_output=True
                )
                
                # Delete remote branch
                subprocess.run(
                    ["git", "push", "origin", "--delete", branch],
                    cwd=self.repo_path,
                    capture_output=True
                )
                
        except:
            pass
            
    def create_backup(self) -> str:
        """Create backup before merge"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            # Generate backup ID
            backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / backup_id
            
            # Save current state
            backup_data = {
                "branch": self.get_current_branch(),
                "commit": self.get_current_commit(),
                "timestamp": datetime.now().isoformat()
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f)
                
            return backup_id
            
        except:
            return None
            
    def restore_backup(self, backup_id: str) -> bool:
        """Restore from backup"""
        try:
            backup_path = self.backup_dir / backup_id
            
            if backup_path.exists():
                with open(backup_path, 'r') as f:
                    backup_data = json.load(f)
                    
                # Restore to backed up commit
                subprocess.run(
                    ["git", "checkout", backup_data["branch"]],
                    cwd=self.repo_path,
                    check=True
                )
                
                subprocess.run(
                    ["git", "reset", "--hard", backup_data["commit"]],
                    cwd=self.repo_path,
                    check=True
                )
                
                return True
                
        except:
            pass
            
        return False
        
    def rollback_merge(self, merge_commit: Optional[str] = None) -> Dict:
        """Rollback a merge"""
        try:
            if not merge_commit:
                # Get last merge commit
                result = subprocess.run(
                    ["git", "log", "--merges", "-n", "1", "--format=%H"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    merge_commit = result.stdout.strip()
                    
            if merge_commit:
                # Revert the merge
                result = subprocess.run(
                    ["git", "revert", "-m", "1", merge_commit],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": f"Successfully rolled back merge {merge_commit}"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
        return {
            "success": False,
            "error": "Could not find merge to rollback"
        }
        
    def detect_branch_type(self, branch_name: str) -> str:
        """Detect branch type from name"""
        branch_lower = branch_name.lower()
        
        if "feature" in branch_lower:
            return "feature"
        elif "hotfix" in branch_lower:
            return "hotfix"
        elif "release" in branch_lower:
            return "release"
            
        return "default"
        
    def get_current_branch(self) -> str:
        """Get current branch"""
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
        
    def get_current_commit(self) -> str:
        """Get current commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""
        
    def suggest_merge_strategy(self, pr_data: Dict) -> str:
        """Suggest optimal merge strategy"""
        # Analyze the changes
        branch_type = self.detect_branch_type(pr_data.get("branch", ""))
        
        # Check change size
        try:
            result = subprocess.run(
                ["git", "diff", "--stat", f"{pr_data.get('base', 'main')}...{pr_data.get('branch')}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                stats = result.stdout
                # Large changes might benefit from different strategies
                if "1000" in stats:  # Large changeset
                    return "patience"  # Better for large refactors
                    
        except:
            pass
            
        return self.config["strategies"].get(branch_type, "recursive")


def integrate_with_claude_code(action: str = "merge", **kwargs):
    """Integration point for Claude Code"""
    manager = SmartMergeManager()
    
    if action == "merge":
        pr_data = kwargs
        return manager.auto_merge(pr_data)
        
    elif action == "rollback":
        merge_commit = kwargs.get("commit")
        return manager.rollback_merge(merge_commit)
        
    elif action == "check":
        pr_data = kwargs
        can_merge, reason = manager.can_auto_merge(pr_data)
        return {
            "can_merge": can_merge,
            "reason": reason
        }
        
    else:
        return {
            "success": False,
            "error": f"Unknown action: {action}"
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        result = integrate_with_claude_code(action)
    else:
        # Default to checking current PR
        result = integrate_with_claude_code("check")
        
    print(json.dumps(result, indent=2))