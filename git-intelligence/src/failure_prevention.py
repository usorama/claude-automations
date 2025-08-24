#!/usr/bin/env python3
"""
Failure Prevention System for Smart Commit Genie
Prevents common failures before they happen
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import ast


class FailurePreventionSystem:
    """Prevents failures before they happen"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config_file = self.repo_path / ".git" / "smart-genie-prevention.json"
        self.load_config()
        
    def load_config(self):
        """Load prevention configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "enabled": True,
                "prevention_history": [],
                "checks": {
                    "pre_commit": {
                        "syntax_check": True,
                        "lint_check": True,
                        "security_scan": True,
                        "large_file_check": True,
                        "credentials_check": True,
                        "broken_imports": True,
                        "todo_check": False
                    },
                    "pre_push": {
                        "test_execution": True,
                        "build_verification": True,
                        "coverage_check": True,
                        "dependency_check": True
                    },
                    "pre_merge": {
                        "conflict_check": True,
                        "regression_check": True,
                        "performance_check": True
                    }
                },
                "auto_fix": {
                    "enabled": True,
                    "fix_formatting": True,
                    "fix_imports": True,
                    "fix_simple_errors": True,
                    "update_dependencies": False
                },
                "thresholds": {
                    "max_file_size_mb": 10,
                    "min_coverage_percent": 70,
                    "max_complexity": 10,
                    "max_line_length": 120
                }
            }
            
    def save_config(self):
        """Save prevention configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def pre_commit_checks(self) -> Dict:
        """Run pre-commit checks"""
        if not self.config["enabled"]:
            return {"passed": True, "skipped": True}
            
        results = {
            "passed": True,
            "checks": [],
            "fixes_applied": []
        }
        
        checks = self.config["checks"]["pre_commit"]
        
        # Syntax check
        if checks["syntax_check"]:
            syntax_result = self.check_syntax()
            results["checks"].append(syntax_result)
            if not syntax_result["passed"]:
                if self.config["auto_fix"]["enabled"] and self.config["auto_fix"]["fix_simple_errors"]:
                    fix_result = self.auto_fix_syntax(syntax_result["errors"])
                    if fix_result["fixed"]:
                        results["fixes_applied"].append(fix_result)
                    else:
                        results["passed"] = False
                else:
                    results["passed"] = False
                    
        # Lint check
        if checks["lint_check"]:
            lint_result = self.check_linting()
            results["checks"].append(lint_result)
            if not lint_result["passed"]:
                if self.config["auto_fix"]["enabled"] and self.config["auto_fix"]["fix_formatting"]:
                    fix_result = self.auto_fix_linting(lint_result["errors"])
                    if fix_result["fixed"]:
                        results["fixes_applied"].append(fix_result)
                    else:
                        results["passed"] = False
                else:
                    results["passed"] = False
                    
        # Security scan
        if checks["security_scan"]:
            security_result = self.check_security()
            results["checks"].append(security_result)
            if not security_result["passed"]:
                results["passed"] = False
                
        # Large file check
        if checks["large_file_check"]:
            large_file_result = self.check_large_files()
            results["checks"].append(large_file_result)
            if not large_file_result["passed"]:
                results["passed"] = False
                
        # Credentials check
        if checks["credentials_check"]:
            creds_result = self.check_credentials()
            results["checks"].append(creds_result)
            if not creds_result["passed"]:
                results["passed"] = False
                
        # Broken imports check
        if checks["broken_imports"]:
            imports_result = self.check_imports()
            results["checks"].append(imports_result)
            if not imports_result["passed"]:
                if self.config["auto_fix"]["enabled"] and self.config["auto_fix"]["fix_imports"]:
                    fix_result = self.auto_fix_imports(imports_result["errors"])
                    if fix_result["fixed"]:
                        results["fixes_applied"].append(fix_result)
                    else:
                        results["passed"] = False
                else:
                    results["passed"] = False
                    
        # TODO check (optional)
        if checks["todo_check"]:
            todo_result = self.check_todos()
            results["checks"].append(todo_result)
            # TODOs don't fail the check, just warn
            
        # Record in history
        self.config["prevention_history"].append({
            "type": "pre_commit",
            "timestamp": datetime.now().isoformat(),
            "passed": results["passed"],
            "checks_run": len(results["checks"]),
            "fixes_applied": len(results["fixes_applied"])
        })
        self.save_config()
        
        return results
        
    def check_syntax(self) -> Dict:
        """Check syntax of changed files"""
        errors = []
        files_checked = 0
        
        # Get changed files
        changed_files = self.get_changed_files()
        
        for file_path in changed_files:
            if file_path.endswith('.py'):
                files_checked += 1
                error = self.check_python_syntax(file_path)
                if error:
                    errors.append({
                        "file": file_path,
                        "error": error
                    })
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                files_checked += 1
                error = self.check_javascript_syntax(file_path)
                if error:
                    errors.append({
                        "file": file_path,
                        "error": error
                    })
                    
        return {
            "check": "syntax",
            "passed": len(errors) == 0,
            "files_checked": files_checked,
            "errors": errors
        }
        
    def check_python_syntax(self, file_path: str) -> Optional[str]:
        """Check Python syntax"""
        try:
            full_path = self.repo_path / file_path
            with open(full_path, 'r') as f:
                source = f.read()
                
            compile(source, file_path, 'exec')
            return None
            
        except SyntaxError as e:
            return f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return str(e)
            
    def check_javascript_syntax(self, file_path: str) -> Optional[str]:
        """Check JavaScript/TypeScript syntax"""
        try:
            # Try using available tools
            tools = [
                ["eslint", "--no-eslintrc"],
                ["tsc", "--noEmit"],
                ["node", "--check"]
            ]
            
            full_path = self.repo_path / file_path
            
            for tool in tools:
                check_result = subprocess.run(
                    ["which", tool[0]],
                    capture_output=True
                )
                
                if check_result.returncode == 0:
                    result = subprocess.run(
                        tool + [str(full_path)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        return result.stderr[:200]  # First 200 chars of error
                        
            return None
            
        except Exception as e:
            return str(e)
            
    def check_linting(self) -> Dict:
        """Check linting issues"""
        errors = []
        files_checked = 0
        
        # Python linting
        if self.has_python_files():
            pylint_errors = self.run_pylint()
            errors.extend(pylint_errors)
            files_checked += len(pylint_errors)
            
        # JavaScript linting
        if self.has_javascript_files():
            eslint_errors = self.run_eslint()
            errors.extend(eslint_errors)
            files_checked += len(eslint_errors)
            
        return {
            "check": "linting",
            "passed": len(errors) == 0,
            "files_checked": files_checked,
            "errors": errors
        }
        
    def check_security(self) -> Dict:
        """Check for security issues"""
        issues = []
        
        # Common security patterns
        patterns = [
            (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "API key hardcoded"),
            (r"password\s*=\s*['\"][^'\"]+['\"]", "Password hardcoded"),
            (r"secret\s*=\s*['\"][^'\"]+['\"]", "Secret hardcoded"),
            (r"token\s*=\s*['\"][^'\"]+['\"]", "Token hardcoded"),
            (r"private[_-]?key", "Private key reference"),
            (r"AWS[_-]?ACCESS[_-]?KEY", "AWS key detected"),
            (r"GITHUB[_-]?TOKEN", "GitHub token detected")
        ]
        
        changed_files = self.get_changed_files()
        
        for file_path in changed_files:
            try:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        content = f.read()
                        
                    for pattern, message in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            issues.append({
                                "file": file_path,
                                "issue": message
                            })
                            break
                            
            except:
                pass
                
        return {
            "check": "security",
            "passed": len(issues) == 0,
            "issues": issues
        }
        
    def check_large_files(self) -> Dict:
        """Check for large files"""
        large_files = []
        max_size = self.config["thresholds"]["max_file_size_mb"] * 1024 * 1024
        
        changed_files = self.get_changed_files()
        
        for file_path in changed_files:
            try:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    size = full_path.stat().st_size
                    if size > max_size:
                        large_files.append({
                            "file": file_path,
                            "size_mb": round(size / 1024 / 1024, 2)
                        })
                        
            except:
                pass
                
        return {
            "check": "large_files",
            "passed": len(large_files) == 0,
            "large_files": large_files
        }
        
    def check_credentials(self) -> Dict:
        """Check for exposed credentials"""
        exposed = []
        
        # Check common credential files
        sensitive_files = [
            ".env",
            ".env.local",
            ".env.production",
            "config.json",
            "secrets.yml",
            "credentials.json"
        ]
        
        for file_name in sensitive_files:
            file_path = self.repo_path / file_name
            if file_path.exists():
                # Check if file is in gitignore
                if not self.is_ignored(file_name):
                    exposed.append({
                        "file": file_name,
                        "issue": "Sensitive file not in .gitignore"
                    })
                    
        return {
            "check": "credentials",
            "passed": len(exposed) == 0,
            "exposed": exposed
        }
        
    def check_imports(self) -> Dict:
        """Check for broken imports"""
        errors = []
        
        changed_files = self.get_changed_files()
        
        for file_path in changed_files:
            if file_path.endswith('.py'):
                import_errors = self.check_python_imports(file_path)
                errors.extend(import_errors)
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                import_errors = self.check_javascript_imports(file_path)
                errors.extend(import_errors)
                
        return {
            "check": "imports",
            "passed": len(errors) == 0,
            "errors": errors
        }
        
    def check_python_imports(self, file_path: str) -> List[Dict]:
        """Check Python imports"""
        errors = []
        
        try:
            full_path = self.repo_path / file_path
            with open(full_path, 'r') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not self.module_exists(alias.name):
                            errors.append({
                                "file": file_path,
                                "import": alias.name,
                                "issue": "Module not found"
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not self.module_exists(node.module):
                        errors.append({
                            "file": file_path,
                            "import": node.module,
                            "issue": "Module not found"
                        })
                        
        except:
            pass
            
        return errors
        
    def check_javascript_imports(self, file_path: str) -> List[Dict]:
        """Check JavaScript imports"""
        errors = []
        
        try:
            full_path = self.repo_path / file_path
            with open(full_path, 'r') as f:
                content = f.read()
                
            # Simple regex for imports
            import_patterns = [
                r"import .+ from ['\"](.+?)['\"]",
                r"require\(['\"](.+?)['\"]\)"
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for module in matches:
                    if not module.startswith('.') and not self.npm_module_exists(module):
                        errors.append({
                            "file": file_path,
                            "import": module,
                            "issue": "Module not installed"
                        })
                        
        except:
            pass
            
        return errors
        
    def check_todos(self) -> Dict:
        """Check for TODO comments"""
        todos = []
        
        changed_files = self.get_changed_files()
        
        for file_path in changed_files:
            try:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        for i, line in enumerate(f, 1):
                            if re.search(r'TODO|FIXME|XXX|HACK', line, re.IGNORECASE):
                                todos.append({
                                    "file": file_path,
                                    "line": i,
                                    "content": line.strip()[:100]
                                })
                                
            except:
                pass
                
        return {
            "check": "todos",
            "passed": True,  # TODOs don't fail the check
            "todos": todos,
            "warning": f"Found {len(todos)} TODO comments" if todos else None
        }
        
    def auto_fix_syntax(self, errors: List[Dict]) -> Dict:
        """Attempt to auto-fix syntax errors"""
        fixed = []
        failed = []
        
        for error in errors:
            file_path = error["file"]
            
            if file_path.endswith('.py'):
                if self.fix_python_syntax(file_path):
                    fixed.append(file_path)
                else:
                    failed.append(file_path)
                    
        return {
            "fixed": len(fixed) > 0,
            "fixed_files": fixed,
            "failed_files": failed
        }
        
    def auto_fix_linting(self, errors: List[Dict]) -> Dict:
        """Attempt to auto-fix linting issues"""
        fixed = []
        
        # Run auto-fixers
        if self.has_python_files():
            # Try black for Python
            result = subprocess.run(
                ["black", "--quiet", "."],
                cwd=self.repo_path,
                capture_output=True
            )
            if result.returncode == 0:
                fixed.append("Python files formatted with black")
                
            # Try autopep8
            result = subprocess.run(
                ["autopep8", "--in-place", "--recursive", "."],
                cwd=self.repo_path,
                capture_output=True
            )
            if result.returncode == 0:
                fixed.append("Python files fixed with autopep8")
                
        if self.has_javascript_files():
            # Try prettier
            result = subprocess.run(
                ["prettier", "--write", "**/*.{js,jsx,ts,tsx}"],
                cwd=self.repo_path,
                capture_output=True
            )
            if result.returncode == 0:
                fixed.append("JavaScript files formatted with prettier")
                
            # Try eslint --fix
            result = subprocess.run(
                ["eslint", "--fix", "."],
                cwd=self.repo_path,
                capture_output=True
            )
            if result.returncode == 0:
                fixed.append("JavaScript files fixed with eslint")
                
        return {
            "fixed": len(fixed) > 0,
            "actions": fixed
        }
        
    def auto_fix_imports(self, errors: List[Dict]) -> Dict:
        """Attempt to auto-fix import issues"""
        fixed = []
        
        # Group by language
        python_modules = set()
        npm_modules = set()
        
        for error in errors:
            if error["file"].endswith('.py'):
                python_modules.add(error["import"])
            else:
                npm_modules.add(error["import"])
                
        # Install missing Python modules
        if python_modules and self.config["auto_fix"]["update_dependencies"]:
            for module in python_modules:
                result = subprocess.run(
                    ["pip", "install", module],
                    capture_output=True
                )
                if result.returncode == 0:
                    fixed.append(f"Installed Python module: {module}")
                    
        # Install missing npm modules
        if npm_modules and self.config["auto_fix"]["update_dependencies"]:
            for module in npm_modules:
                result = subprocess.run(
                    ["npm", "install", module],
                    cwd=self.repo_path,
                    capture_output=True
                )
                if result.returncode == 0:
                    fixed.append(f"Installed npm module: {module}")
                    
        return {
            "fixed": len(fixed) > 0,
            "installed": fixed
        }
        
    def fix_python_syntax(self, file_path: str) -> bool:
        """Try to fix Python syntax errors"""
        try:
            # Try using autopep8 or black
            full_path = self.repo_path / file_path
            
            # Try autopep8
            result = subprocess.run(
                ["autopep8", "--in-place", str(full_path)],
                capture_output=True
            )
            
            if result.returncode == 0:
                # Verify it's fixed
                return self.check_python_syntax(file_path) is None
                
        except:
            pass
            
        return False
        
    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return [f for f in files if f]
                
        except:
            pass
            
        return []
        
    def has_python_files(self) -> bool:
        """Check if repository has Python files"""
        return any(f.endswith('.py') for f in self.get_changed_files())
        
    def has_javascript_files(self) -> bool:
        """Check if repository has JavaScript files"""
        extensions = ['.js', '.jsx', '.ts', '.tsx']
        return any(any(f.endswith(ext) for ext in extensions) 
                  for f in self.get_changed_files())
        
    def is_ignored(self, file_path: str) -> bool:
        """Check if file is in .gitignore"""
        try:
            result = subprocess.run(
                ["git", "check-ignore", file_path],
                cwd=self.repo_path,
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
            
    def module_exists(self, module_name: str) -> bool:
        """Check if Python module exists"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
            
    def npm_module_exists(self, module_name: str) -> bool:
        """Check if npm module exists"""
        package_json = self.repo_path / "package.json"
        
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            
            return module_name in deps or module_name in dev_deps
            
        return False
        
    def run_pylint(self) -> List[Dict]:
        """Run pylint on Python files"""
        errors = []
        
        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues[:10]:  # Limit to first 10
                    errors.append({
                        "file": issue.get("path"),
                        "line": issue.get("line"),
                        "message": issue.get("message")
                    })
                    
        except:
            pass
            
        return errors
        
    def run_eslint(self) -> List[Dict]:
        """Run eslint on JavaScript files"""
        errors = []
        
        try:
            result = subprocess.run(
                ["eslint", "--format=json", "."],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                for file_result in data[:5]:  # Limit to first 5 files
                    for message in file_result.get("messages", [])[:2]:  # 2 per file
                        errors.append({
                            "file": file_result.get("filePath"),
                            "line": message.get("line"),
                            "message": message.get("message")
                        })
                        
        except:
            pass
            
        return errors


def integrate_with_claude_code(check_type: str = "pre_commit"):
    """Integration point for Claude Code"""
    prevention = FailurePreventionSystem()
    
    if check_type == "pre_commit":
        return prevention.pre_commit_checks()
    else:
        return {"error": f"Unknown check type: {check_type}"}


if __name__ == "__main__":
    result = integrate_with_claude_code()
    print(json.dumps(result, indent=2))