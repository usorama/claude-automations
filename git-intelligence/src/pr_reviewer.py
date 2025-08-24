#!/usr/bin/env python3
"""
PR Auto-Review System for Smart Commit Genie
Provides automated code review comments and suggestions
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import ast
import difflib


class PRAutoReviewer:
    """Automated PR review system"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config_file = self.repo_path / ".git" / "smart-genie-review.json"
        self.load_config()
        
    def load_config(self):
        """Load review configuration and rules"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "auto_review": True,
                "review_history": [],
                "rules": {
                    "security": {
                        "enabled": True,
                        "patterns": [
                            {"pattern": r"api[_-]?key", "message": "🔐 Potential API key exposure"},
                            {"pattern": r"password\s*=\s*['\"]", "message": "🔐 Hardcoded password detected"},
                            {"pattern": r"token\s*=\s*['\"]", "message": "🔐 Hardcoded token detected"},
                            {"pattern": r"secret\s*=\s*['\"]", "message": "🔐 Hardcoded secret detected"},
                            {"pattern": r"eval\(", "message": "⚠️ Avoid using eval() - security risk"},
                            {"pattern": r"exec\(", "message": "⚠️ Avoid using exec() - security risk"},
                            {"pattern": r"os\.system\(", "message": "⚠️ Use subprocess instead of os.system"},
                            {"pattern": r"pickle\.load", "message": "⚠️ Pickle can execute arbitrary code"},
                            {"pattern": r"input\(.*\)", "message": "⚠️ Validate user input"},
                            {"pattern": r"subprocess.*shell=True", "message": "⚠️ Avoid shell=True in subprocess"}
                        ]
                    },
                    "performance": {
                        "enabled": True,
                        "patterns": [
                            {"pattern": r"for .+ in .+:\s*for .+ in .+:", "message": "🚀 Consider optimizing nested loops"},
                            {"pattern": r"\.append\(.+\) for .+ in", "message": "🚀 Consider list comprehension"},
                            {"pattern": r"time\.sleep\(\d+\)", "message": "🚀 Long sleep detected"},
                            {"pattern": r"SELECT \*", "message": "🚀 Avoid SELECT * in queries"},
                            {"pattern": r"n\+1", "message": "🚀 Potential N+1 query problem"}
                        ]
                    },
                    "best_practices": {
                        "enabled": True,
                        "patterns": [
                            {"pattern": r"TODO|FIXME|XXX", "message": "📝 TODO comment found - track in issues?"},
                            {"pattern": r"print\(", "message": "📝 Consider using logging instead of print"},
                            {"pattern": r"except:\s*$", "message": "⚠️ Avoid bare except clauses"},
                            {"pattern": r"import \*", "message": "📝 Avoid wildcard imports"},
                            {"pattern": r"global ", "message": "📝 Consider avoiding global variables"},
                            {"pattern": r"class\s+\w+\(\):", "message": "📝 Classes should inherit from object in Python 2"},
                            {"pattern": r"if .+ == True", "message": "📝 Simplify boolean comparison"},
                            {"pattern": r"if .+ == False", "message": "📝 Simplify boolean comparison"},
                            {"pattern": r"if len\(.+\) == 0", "message": "📝 Use 'if not sequence' instead"},
                            {"pattern": r"if len\(.+\) > 0", "message": "📝 Use 'if sequence' instead"}
                        ]
                    },
                    "testing": {
                        "enabled": True,
                        "indicators": {
                            "new_functions_need_tests": True,
                            "modified_functions_need_tests": True,
                            "minimum_coverage": 80
                        }
                    },
                    "documentation": {
                        "enabled": True,
                        "require_docstrings": True,
                        "require_type_hints": False
                    }
                },
                "positive_patterns": [
                    {"pattern": r"test_", "message": "✅ Good: Test added"},
                    {"pattern": r"@pytest\.mark", "message": "✅ Good: Test markers used"},
                    {"pattern": r"typing\.", "message": "✅ Good: Type hints used"},
                    {"pattern": r'""".*"""', "message": "✅ Good: Docstring added"},
                    {"pattern": r"@cache|@lru_cache", "message": "✅ Good: Caching implemented"},
                    {"pattern": r"with open\(", "message": "✅ Good: Context manager used"},
                    {"pattern": r"logger\.", "message": "✅ Good: Logging used"}
                ]
            }
            
    def save_config(self):
        """Save review configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def review_pr(self, pr_number: Optional[int] = None) -> Dict:
        """Perform automated PR review"""
        if not self.config["auto_review"]:
            return {"reviewed": False, "reason": "Auto-review disabled"}
            
        # Get PR diff
        diff_data = self.get_pr_diff(pr_number)
        if not diff_data:
            return {"reviewed": False, "reason": "Could not get PR diff"}
            
        # Perform various checks
        review_comments = []
        
        # Security review
        if self.config["rules"]["security"]["enabled"]:
            security_comments = self.review_security(diff_data)
            review_comments.extend(security_comments)
            
        # Performance review
        if self.config["rules"]["performance"]["enabled"]:
            perf_comments = self.review_performance(diff_data)
            review_comments.extend(perf_comments)
            
        # Best practices review
        if self.config["rules"]["best_practices"]["enabled"]:
            bp_comments = self.review_best_practices(diff_data)
            review_comments.extend(bp_comments)
            
        # Testing review
        if self.config["rules"]["testing"]["enabled"]:
            test_comments = self.review_testing(diff_data)
            review_comments.extend(test_comments)
            
        # Documentation review
        if self.config["rules"]["documentation"]["enabled"]:
            doc_comments = self.review_documentation(diff_data)
            review_comments.extend(doc_comments)
            
        # Positive feedback
        positive_comments = self.find_positive_patterns(diff_data)
        review_comments.extend(positive_comments)
            
        # Generate summary
        summary = self.generate_review_summary(review_comments, diff_data)
        
        # Post review if we have comments
        if review_comments or summary:
            result = self.post_review(pr_number, review_comments, summary)
            
            # Save to history
            self.config["review_history"].append({
                "pr": pr_number,
                "reviewed": datetime.now().isoformat(),
                "comments": len(review_comments),
                "summary": summary
            })
            self.save_config()
            
            return {
                "reviewed": True,
                "comments": review_comments,
                "summary": summary,
                "result": result
            }
            
        return {
            "reviewed": True,
            "comments": [],
            "summary": "No issues found - looks good! 🎉"
        }
        
    def get_pr_diff(self, pr_number: Optional[int] = None) -> Dict:
        """Get PR diff data"""
        try:
            if pr_number:
                # Get specific PR diff
                result = subprocess.run(
                    ["gh", "pr", "diff", str(pr_number)],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
            else:
                # Get diff for current branch
                base_branch = self.get_base_branch()
                result = subprocess.run(
                    ["git", "diff", f"{base_branch}...HEAD"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
            if result.returncode == 0:
                return self.parse_diff(result.stdout)
                
        except Exception as e:
            print(f"Error getting diff: {e}")
            
        return {}
        
    def parse_diff(self, diff_text: str) -> Dict:
        """Parse git diff output"""
        files = {}
        current_file = None
        current_changes = []
        
        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files[current_file] = current_changes
                    current_changes = []
                    
                # Extract filename
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
                    
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                current_changes.append({
                    "type": "add",
                    "content": line[1:],
                    "line": line
                })
                
            elif line.startswith('-') and not line.startswith('---'):
                # Removed line
                current_changes.append({
                    "type": "remove",
                    "content": line[1:],
                    "line": line
                })
                
        # Add last file
        if current_file:
            files[current_file] = current_changes
            
        return files
        
    def review_security(self, diff_data: Dict) -> List[Dict]:
        """Review for security issues"""
        comments = []
        
        for file_path, changes in diff_data.items():
            for change in changes:
                if change["type"] == "add":
                    content = change["content"]
                    
                    for rule in self.config["rules"]["security"]["patterns"]:
                        if re.search(rule["pattern"], content, re.IGNORECASE):
                            comments.append({
                                "file": file_path,
                                "line": content,
                                "type": "security",
                                "severity": "high",
                                "message": rule["message"],
                                "suggestion": self.get_security_suggestion(rule["pattern"])
                            })
                            
        return comments
        
    def review_performance(self, diff_data: Dict) -> List[Dict]:
        """Review for performance issues"""
        comments = []
        
        for file_path, changes in diff_data.items():
            # Skip non-code files
            if not self.is_code_file(file_path):
                continue
                
            for change in changes:
                if change["type"] == "add":
                    content = change["content"]
                    
                    for rule in self.config["rules"]["performance"]["patterns"]:
                        if re.search(rule["pattern"], content, re.IGNORECASE):
                            comments.append({
                                "file": file_path,
                                "line": content,
                                "type": "performance",
                                "severity": "medium",
                                "message": rule["message"],
                                "suggestion": self.get_performance_suggestion(rule["pattern"])
                            })
                            
        return comments
        
    def review_best_practices(self, diff_data: Dict) -> List[Dict]:
        """Review for best practices"""
        comments = []
        
        for file_path, changes in diff_data.items():
            if not self.is_code_file(file_path):
                continue
                
            for change in changes:
                if change["type"] == "add":
                    content = change["content"]
                    
                    for rule in self.config["rules"]["best_practices"]["patterns"]:
                        if re.search(rule["pattern"], content):
                            comments.append({
                                "file": file_path,
                                "line": content,
                                "type": "best_practice",
                                "severity": "low",
                                "message": rule["message"]
                            })
                            
        return comments
        
    def review_testing(self, diff_data: Dict) -> List[Dict]:
        """Review testing coverage"""
        comments = []
        
        # Check if tests were added for new code
        has_new_functions = False
        has_new_tests = False
        
        for file_path, changes in diff_data.items():
            if "test" in file_path.lower():
                has_new_tests = True
                
            for change in changes:
                if change["type"] == "add":
                    if re.search(r'def \w+\(', change["content"]):
                        has_new_functions = True
                        
        if has_new_functions and not has_new_tests:
            comments.append({
                "file": "general",
                "type": "testing",
                "severity": "medium",
                "message": "⚠️ New functions added but no tests found. Consider adding tests."
            })
            
        return comments
        
    def review_documentation(self, diff_data: Dict) -> List[Dict]:
        """Review documentation"""
        comments = []
        
        if not self.config["rules"]["documentation"]["require_docstrings"]:
            return comments
            
        for file_path, changes in diff_data.items():
            if not self.is_code_file(file_path):
                continue
                
            # Check for functions without docstrings
            in_function = False
            has_docstring = False
            
            for change in changes:
                if change["type"] == "add":
                    content = change["content"]
                    
                    if re.search(r'def \w+\(', content):
                        in_function = True
                        has_docstring = False
                        
                    elif in_function and '"""' in content:
                        has_docstring = True
                        
                    elif in_function and content.strip() and not content.startswith(' '):
                        if not has_docstring:
                            comments.append({
                                "file": file_path,
                                "type": "documentation",
                                "severity": "low",
                                "message": "📝 Consider adding a docstring to this function"
                            })
                        in_function = False
                        
        return comments
        
    def find_positive_patterns(self, diff_data: Dict) -> List[Dict]:
        """Find positive patterns to praise"""
        comments = []
        
        for file_path, changes in diff_data.items():
            for change in changes:
                if change["type"] == "add":
                    content = change["content"]
                    
                    for pattern in self.config["positive_patterns"]:
                        if re.search(pattern["pattern"], content):
                            comments.append({
                                "file": file_path,
                                "type": "positive",
                                "severity": "info",
                                "message": pattern["message"]
                            })
                            break  # One positive comment per line
                            
        return comments
        
    def is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file"""
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php']
        return any(file_path.endswith(ext) for ext in code_extensions)
        
    def get_security_suggestion(self, pattern: str) -> str:
        """Get suggestion for security issue"""
        suggestions = {
            r"api[_-]?key": "Store API keys in environment variables or secure vaults",
            r"password": "Use environment variables or secure configuration management",
            r"eval\(": "Use ast.literal_eval() for safe evaluation or refactor code",
            r"os\.system": "Use subprocess.run() with proper argument handling",
            r"pickle": "Consider using JSON or other safe serialization formats"
        }
        
        for key, suggestion in suggestions.items():
            if key in pattern:
                return suggestion
                
        return "Review security best practices for this pattern"
        
    def get_performance_suggestion(self, pattern: str) -> str:
        """Get suggestion for performance issue"""
        suggestions = {
            "nested loops": "Consider using vectorized operations or optimized algorithms",
            "append": "List comprehensions are often more efficient",
            "SELECT \\*": "Specify only the columns you need",
            "n\\+1": "Use eager loading or batch queries"
        }
        
        for key, suggestion in suggestions.items():
            if key in pattern:
                return suggestion
                
        return "Consider optimizing this for better performance"
        
    def generate_review_summary(self, comments: List[Dict], diff_data: Dict) -> str:
        """Generate review summary"""
        if not comments:
            return "✅ All checks passed! Great work! 🎉"
            
        # Count by severity
        high = sum(1 for c in comments if c.get("severity") == "high")
        medium = sum(1 for c in comments if c.get("severity") == "medium")
        low = sum(1 for c in comments if c.get("severity") == "low")
        positive = sum(1 for c in comments if c["type"] == "positive")
        
        summary_parts = ["## Automated Review Summary\n"]
        
        # Statistics
        summary_parts.append(f"📊 **Files reviewed**: {len(diff_data)}")
        summary_parts.append(f"💬 **Comments**: {len(comments)}")
        
        if high > 0:
            summary_parts.append(f"🔴 **High priority**: {high} issues")
        if medium > 0:
            summary_parts.append(f"🟡 **Medium priority**: {medium} issues")
        if low > 0:
            summary_parts.append(f"🟢 **Low priority**: {low} suggestions")
        if positive > 0:
            summary_parts.append(f"✨ **Positive findings**: {positive}")
            
        # Overall assessment
        if high > 0:
            summary_parts.append("\n⚠️ **Status**: Please address high-priority issues before merging")
        elif medium > 0:
            summary_parts.append("\n📝 **Status**: Consider addressing medium-priority items")
        else:
            summary_parts.append("\n✅ **Status**: Looking good, minor suggestions only")
            
        summary_parts.append("\n---")
        summary_parts.append("*Review performed by Smart Commit Genie* 🤖")
        
        return "\n".join(summary_parts)
        
    def post_review(self, pr_number: Optional[int], comments: List[Dict], summary: str) -> Dict:
        """Post review comments to PR"""
        try:
            # Format comments for posting
            formatted_comments = self.format_comments_for_github(comments)
            
            if pr_number:
                # Post to specific PR
                cmd = ["gh", "pr", "review", str(pr_number), "--comment", "--body", summary]
                
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return {"success": True, "message": "Review posted successfully"}
                else:
                    return {"success": False, "error": result.stderr}
                    
            else:
                # Save review locally for current branch
                review_file = self.repo_path / ".git" / "smart-genie-review.md"
                with open(review_file, 'w') as f:
                    f.write(summary)
                    f.write("\n\n## Detailed Comments\n\n")
                    for comment in formatted_comments:
                        f.write(f"- {comment}\n")
                        
                return {"success": True, "message": f"Review saved to {review_file}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def format_comments_for_github(self, comments: List[Dict]) -> List[str]:
        """Format comments for GitHub"""
        formatted = []
        
        for comment in comments:
            severity_emoji = {
                "high": "🔴",
                "medium": "🟡", 
                "low": "🟢",
                "info": "ℹ️"
            }.get(comment.get("severity", "info"), "")
            
            file_ref = f"`{comment['file']}`" if comment.get("file") != "general" else ""
            
            formatted_comment = f"{severity_emoji} {file_ref} {comment['message']}"
            
            if comment.get("suggestion"):
                formatted_comment += f"\n   💡 **Suggestion**: {comment['suggestion']}"
                
            formatted.append(formatted_comment)
            
        return formatted
        
    def get_base_branch(self) -> str:
        """Get base branch name"""
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
        return "master"


def integrate_with_claude_code(pr_number: Optional[int] = None):
    """Integration point for Claude Code"""
    reviewer = PRAutoReviewer()
    result = reviewer.review_pr(pr_number)
    return result


if __name__ == "__main__":
    import sys
    pr_number = int(sys.argv[1]) if len(sys.argv) > 1 else None
    result = integrate_with_claude_code(pr_number)
    print(json.dumps(result, indent=2))