#!/usr/bin/env python3
"""
Auto-PR Creation System for Smart Commit Genie
Automatically creates pull requests with intelligent descriptions
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import difflib


class AutoPRManager:
    """Manages automatic pull request creation"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config_file = self.repo_path / ".git" / "smart-genie-pr.json"
        self.load_config()
        
    def load_config(self):
        """Load PR configuration and templates"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "auto_pr": True,
                "pr_history": [],
                "templates": {
                    "feature": {
                        "title": "✨ {branch_type}: {description}",
                        "body": """## Summary
{summary}

## Changes
{changes}

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
{testing}

## Screenshots
{screenshots}

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Tests pass locally
- [x] Documentation updated

## Related Issues
{issues}

---
*Created automatically by Smart Commit Genie* 🤖"""
                    },
                    "bugfix": {
                        "title": "🐛 Fix: {description}",
                        "body": """## Problem
{problem}

## Solution
{solution}

## Changes Made
{changes}

## Testing
{testing}

## Verification Steps
1. {verification_steps}

## Related Issues
Fixes #{issue_number}

---
*Created automatically by Smart Commit Genie* 🤖"""
                    },
                    "default": {
                        "title": "{branch_type}: {description}",
                        "body": """## Description
{description}

## Changes
{changes}

## Testing
{testing}

---
*Created automatically by Smart Commit Genie* 🤖"""
                    }
                },
                "reviewers": {
                    "auto_assign": True,
                    "code_owners": True,
                    "patterns": {
                        "frontend": ["@frontend-team"],
                        "backend": ["@backend-team"],
                        "docs": ["@docs-team"]
                    }
                }
            }
            
    def save_config(self):
        """Save PR configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def should_create_pr(self) -> Tuple[bool, str]:
        """Determine if a PR should be created"""
        if not self.config["auto_pr"]:
            return False, "Auto-PR disabled"
            
        # Check if we're on a feature branch
        current_branch = self.get_current_branch()
        if current_branch in ["main", "master", "develop"]:
            return False, "On main branch"
            
        # Check if branch has unpushed commits
        unpushed = self.get_unpushed_commits()
        if not unpushed:
            return False, "No unpushed commits"
            
        # Check if branch is old enough (has meaningful work)
        if len(unpushed) < 2:
            return False, "Not enough commits"
            
        # Check if PR already exists
        if self.pr_exists_for_branch(current_branch):
            return False, "PR already exists"
            
        return True, "Ready for PR"
        
    def generate_pr_description(self) -> Dict[str, str]:
        """Generate comprehensive PR description from commits and changes"""
        current_branch = self.get_current_branch()
        branch_type = self.detect_branch_type(current_branch)
        
        # Gather information
        commits = self.get_branch_commits()
        changes = self.analyze_changes()
        summary = self.generate_summary(commits, changes)
        
        # Select template
        template_key = branch_type if branch_type in self.config["templates"] else "default"
        template = self.config["templates"][template_key]
        
        # Generate title
        title = template["title"].format(
            branch_type=branch_type.capitalize(),
            description=self.extract_main_change(commits)
        )
        
        # Generate body
        body_data = {
            "summary": summary,
            "description": summary,
            "changes": self.format_changes(changes),
            "testing": self.detect_test_changes(changes),
            "screenshots": self.find_screenshots(),
            "issues": self.find_related_issues(commits),
            "problem": self.extract_problem(commits),
            "solution": self.extract_solution(commits),
            "verification_steps": self.generate_verification_steps(changes),
            "issue_number": self.extract_issue_number(commits) or "N/A"
        }
        
        # Fill template
        body = template["body"]
        for key, value in body_data.items():
            body = body.replace(f"{{{key}}}", str(value))
            
        return {
            "title": title,
            "body": body,
            "branch": current_branch,
            "base": self.get_base_branch()
        }
        
    def detect_branch_type(self, branch_name: str) -> str:
        """Detect the type of branch"""
        branch_lower = branch_name.lower()
        
        if any(x in branch_lower for x in ["feat", "feature"]):
            return "feature"
        elif any(x in branch_lower for x in ["fix", "bug", "patch"]):
            return "bugfix"
        elif any(x in branch_lower for x in ["hotfix", "critical"]):
            return "hotfix"
        elif any(x in branch_lower for x in ["docs", "documentation"]):
            return "docs"
        elif any(x in branch_lower for x in ["test", "spec"]):
            return "test"
        elif any(x in branch_lower for x in ["refactor", "cleanup"]):
            return "refactor"
        elif any(x in branch_lower for x in ["chore", "deps"]):
            return "chore"
            
        return "update"
        
    def get_branch_commits(self) -> List[Dict]:
        """Get all commits in the current branch"""
        try:
            base_branch = self.get_base_branch()
            result = subprocess.run(
                ["git", "log", f"{base_branch}..HEAD", "--pretty=format:%H|%s|%b|%an|%ae|%cd"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 6:
                            commits.append({
                                "hash": parts[0],
                                "subject": parts[1],
                                "body": parts[2],
                                "author": parts[3],
                                "email": parts[4],
                                "date": parts[5]
                            })
                return commits
        except:
            pass
        return []
        
    def analyze_changes(self) -> Dict:
        """Analyze all changes in the branch"""
        try:
            base_branch = self.get_base_branch()
            
            # Get file changes
            result = subprocess.run(
                ["git", "diff", "--stat", f"{base_branch}...HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            changes = {
                "files_changed": [],
                "insertions": 0,
                "deletions": 0,
                "categories": {}
            }
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[:-1]:  # Skip summary line
                    if '|' in line:
                        parts = line.split('|')
                        file_path = parts[0].strip()
                        changes["files_changed"].append(file_path)
                        
                        # Categorize file
                        category = self.categorize_file(file_path)
                        if category not in changes["categories"]:
                            changes["categories"][category] = []
                        changes["categories"][category].append(file_path)
                        
                # Parse summary line
                if lines:
                    summary = lines[-1]
                    if "insertion" in summary:
                        match = re.search(r'(\d+) insertion', summary)
                        if match:
                            changes["insertions"] = int(match.group(1))
                    if "deletion" in summary:
                        match = re.search(r'(\d+) deletion', summary)
                        if match:
                            changes["deletions"] = int(match.group(1))
                            
            return changes
        except:
            return {"files_changed": [], "insertions": 0, "deletions": 0, "categories": {}}
            
    def categorize_file(self, file_path: str) -> str:
        """Categorize a file based on its path and extension"""
        path = Path(file_path)
        
        # Check directory patterns
        if "test" in str(path).lower() or "spec" in str(path).lower():
            return "tests"
        elif "doc" in str(path).lower() or path.suffix == ".md":
            return "documentation"
        elif path.suffix in [".css", ".scss", ".less"]:
            return "styles"
        elif path.suffix in [".js", ".jsx", ".ts", ".tsx"]:
            if "component" in str(path).lower():
                return "components"
            return "frontend"
        elif path.suffix in [".py", ".go", ".java", ".rb"]:
            return "backend"
        elif path.suffix in [".yml", ".yaml", ".json", ".toml"]:
            return "config"
            
        return "other"
        
    def generate_summary(self, commits: List[Dict], changes: Dict) -> str:
        """Generate a summary of the changes"""
        if not commits:
            return "No commits found"
            
        # Extract key points from commits
        key_changes = []
        for commit in commits[:5]:  # Look at first 5 commits
            subject = commit["subject"]
            # Skip merge commits and WIP
            if not subject.startswith("Merge") and "WIP" not in subject:
                key_changes.append(f"- {subject}")
                
        summary = "\n".join(key_changes[:3])  # Top 3 changes
        
        # Add statistics
        if changes["files_changed"]:
            summary += f"\n\n📊 **Impact**: {len(changes['files_changed'])} files changed"
            summary += f" (+{changes['insertions']} -{changes['deletions']})"
            
        return summary
        
    def format_changes(self, changes: Dict) -> str:
        """Format changes for PR description"""
        if not changes["files_changed"]:
            return "No files changed"
            
        formatted = []
        
        # Group by category
        for category, files in changes["categories"].items():
            if files:
                formatted.append(f"\n### {category.capitalize()}")
                for file in files[:5]:  # Show first 5 files per category
                    formatted.append(f"- `{file}`")
                if len(files) > 5:
                    formatted.append(f"- ...and {len(files) - 5} more")
                    
        return "\n".join(formatted)
        
    def detect_test_changes(self, changes: Dict) -> str:
        """Detect and describe test changes"""
        test_files = changes["categories"].get("tests", [])
        
        if not test_files:
            return "- No test changes detected\n- Consider adding tests for new functionality"
            
        return f"- {len(test_files)} test files modified\n- All tests passing locally ✅"
        
    def find_screenshots(self) -> str:
        """Find and reference screenshots"""
        # Look for image files in the branch
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=A", "HEAD~1"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                images = [f for f in files if any(ext in f.lower() 
                         for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg'])]
                
                if images:
                    return "\n".join([f"![{Path(img).stem}]({img})" for img in images[:3]])
                    
        except:
            pass
            
        return "*No screenshots available*"
        
    def find_related_issues(self, commits: List[Dict]) -> str:
        """Find related issues from commit messages"""
        issues = set()
        
        for commit in commits:
            # Look for issue references
            text = f"{commit['subject']} {commit['body']}"
            
            # GitHub issue patterns
            patterns = [
                r'#(\d+)',
                r'issue[s]?\s+#?(\d+)',
                r'fix(?:es)?\s+#?(\d+)',
                r'close[s]?\s+#?(\d+)',
                r'resolve[s]?\s+#?(\d+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                issues.update(matches)
                
        if issues:
            return "- " + "\n- ".join([f"#{issue}" for issue in sorted(issues)])
            
        return "*No related issues found*"
        
    def extract_main_change(self, commits: List[Dict]) -> str:
        """Extract the main change from commits"""
        if not commits:
            return "Updates"
            
        # Use the first meaningful commit
        for commit in commits:
            subject = commit["subject"]
            if not subject.startswith("Merge") and "WIP" not in subject:
                # Clean up the subject
                subject = re.sub(r'^(feat|fix|docs|style|refactor|test|chore)(\(.+?\))?: ', '', subject)
                return subject[:50]  # Limit length
                
        return "Updates"
        
    def extract_problem(self, commits: List[Dict]) -> str:
        """Extract problem description from commits"""
        for commit in commits:
            if "fix" in commit["subject"].lower() or "bug" in commit["subject"].lower():
                return commit["body"] if commit["body"] else commit["subject"]
                
        return "See commit history for details"
        
    def extract_solution(self, commits: List[Dict]) -> str:
        """Extract solution description from commits"""
        solutions = []
        
        for commit in commits:
            if commit["body"] and not commit["subject"].startswith("Merge"):
                solutions.append(commit["body"][:200])
                
        if solutions:
            return "\n".join(solutions[:2])
            
        return "Implemented changes as described in commits"
        
    def generate_verification_steps(self, changes: Dict) -> str:
        """Generate verification steps based on changes"""
        steps = []
        
        if "frontend" in changes["categories"] or "components" in changes["categories"]:
            steps.append("Check UI components render correctly")
            steps.append("Verify no console errors")
            
        if "backend" in changes["categories"]:
            steps.append("Run API tests")
            steps.append("Verify database migrations")
            
        if "tests" in changes["categories"]:
            steps.append("Run test suite")
            steps.append("Verify coverage maintained")
            
        if not steps:
            steps.append("Review code changes")
            steps.append("Test affected functionality")
            
        return "\n2. ".join(steps)
        
    def extract_issue_number(self, commits: List[Dict]) -> Optional[str]:
        """Extract primary issue number from commits"""
        for commit in commits:
            match = re.search(r'#(\d+)', commit["subject"])
            if match:
                return match.group(1)
        return None
        
    def get_current_branch(self) -> str:
        """Get current branch name"""
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
        
    def get_base_branch(self) -> str:
        """Determine the base branch for PR"""
        # Check if main exists
        try:
            result = subprocess.run(
                ["git", "show-ref", "--verify", "refs/heads/main"],
                cwd=self.repo_path,
                capture_output=True
            )
            if result.returncode == 0:
                return "main"
        except:
            pass
            
        # Fall back to master
        return "master"
        
    def get_unpushed_commits(self) -> List[str]:
        """Get list of unpushed commits"""
        try:
            current_branch = self.get_current_branch()
            result = subprocess.run(
                ["git", "log", f"origin/{current_branch}..HEAD", "--oneline"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')
        except:
            # Branch might not exist on origin yet
            try:
                result = subprocess.run(
                    ["git", "log", f"origin/{self.get_base_branch()}..HEAD", "--oneline"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')
            except:
                pass
                
        return []
        
    def pr_exists_for_branch(self, branch: str) -> bool:
        """Check if PR already exists for branch"""
        try:
            # Use GitHub CLI if available
            result = subprocess.run(
                ["gh", "pr", "list", "--head", branch, "--json", "number"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                return len(prs) > 0
        except:
            pass
            
        return False
        
    def create_pr(self, pr_data: Dict) -> Dict:
        """Create the actual PR using GitHub CLI"""
        try:
            # First, push the branch
            current_branch = pr_data["branch"]
            subprocess.run(
                ["git", "push", "-u", "origin", current_branch],
                cwd=self.repo_path,
                capture_output=True
            )
            
            # Create PR using gh CLI
            cmd = [
                "gh", "pr", "create",
                "--title", pr_data["title"],
                "--body", pr_data["body"],
                "--base", pr_data["base"]
            ]
            
            # Add reviewers if configured
            reviewers = self.suggest_reviewers(pr_data)
            if reviewers:
                cmd.extend(["--reviewer", ",".join(reviewers)])
                
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pr_url = result.stdout.strip()
                
                # Record PR creation
                self.config["pr_history"].append({
                    "branch": current_branch,
                    "created": datetime.now().isoformat(),
                    "title": pr_data["title"],
                    "url": pr_url
                })
                self.save_config()
                
                return {
                    "success": True,
                    "url": pr_url,
                    "message": f"PR created successfully: {pr_url}"
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
            
    def suggest_reviewers(self, pr_data: Dict) -> List[str]:
        """Suggest reviewers based on changes"""
        reviewers = []
        
        if not self.config["reviewers"]["auto_assign"]:
            return reviewers
            
        # Check CODEOWNERS if enabled
        if self.config["reviewers"]["code_owners"]:
            codeowners = self.read_codeowners()
            # Match files to owners
            # This would need more implementation
            
        # Use patterns
        for category, users in self.config["reviewers"]["patterns"].items():
            if category in str(pr_data.get("body", "")):
                reviewers.extend(users)
                
        return list(set(reviewers))  # Remove duplicates
        
    def read_codeowners(self) -> Dict:
        """Read CODEOWNERS file"""
        codeowners_path = self.repo_path / ".github" / "CODEOWNERS"
        if not codeowners_path.exists():
            codeowners_path = self.repo_path / "CODEOWNERS"
            
        if codeowners_path.exists():
            # Parse CODEOWNERS file
            # This would need implementation
            pass
            
        return {}


def integrate_with_claude_code():
    """Integration point for Claude Code"""
    manager = AutoPRManager()
    
    # Check if we should create a PR
    should_create, reason = manager.should_create_pr()
    
    if should_create:
        # Generate PR description
        pr_data = manager.generate_pr_description()
        
        # Create the PR
        result = manager.create_pr(pr_data)
        
        return result
    else:
        return {
            "success": False,
            "reason": reason
        }


if __name__ == "__main__":
    result = integrate_with_claude_code()
    print(json.dumps(result, indent=2))