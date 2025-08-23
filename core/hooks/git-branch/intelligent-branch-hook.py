#!/usr/bin/env python3
"""
Intelligent Branch Hook - Fallback system when MCP server is unavailable
Provides basic branching intelligence through git hooks
"""

import subprocess
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

class IntelligentBranchHook:
    def __init__(self):
        self.project_root = self.find_git_root()
        self.claude_dir = Path.home() / '.claude'
        self.debug_mode = os.getenv('GIT_BRANCH_DEBUG', 'false').lower() == 'true'
        
    def log(self, message):
        """Log debug messages if debug mode is enabled"""
        if self.debug_mode:
            print(f"[BranchHook] {datetime.now().isoformat()}: {message}", file=sys.stderr)
    
    def find_git_root(self):
        """Find the git repository root"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            return Path.cwd()
    
    def is_mcp_server_available(self):
        """Check if the MCP server is available"""
        try:
            # Simple check - try to find MCP server process or config
            mcp_config = Path.home() / '.claude-code' / 'mcp' / 'global.json'
            if mcp_config.exists():
                with open(mcp_config) as f:
                    config = json.load(f)
                    return 'git-branch-intelligence' in config.get('mcpServers', {})
            return False
        except Exception:
            return False
    
    def get_current_branch(self):
        """Get current branch name"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_git_status(self):
        """Get git status information"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, check=True
            )
            
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            status = {
                'modified': [],
                'added': [],
                'deleted': [],
                'untracked': []
            }
            
            for line in lines:
                if line:
                    status_code = line[:2]
                    filename = line[3:]
                    
                    if 'M' in status_code:
                        status['modified'].append(filename)
                    elif 'A' in status_code:
                        status['added'].append(filename)
                    elif 'D' in status_code:
                        status['deleted'].append(filename)
                    elif '??' in status_code:
                        status['untracked'].append(filename)
            
            return status
        except subprocess.CalledProcessError:
            return {}
    
    def detect_work_type(self):
        """Detect the type of work being done based on file changes"""
        status = self.get_git_status()
        all_files = (
            status.get('modified', []) + 
            status.get('added', []) + 
            status.get('untracked', [])
        )
        
        if not all_files:
            return {'type': 'unknown', 'confidence': 0}
        
        # Analyze file patterns
        test_files = len([f for f in all_files if 'test' in f.lower() or 'spec' in f.lower()])
        doc_files = len([f for f in all_files if f.endswith('.md') or 'doc' in f.lower()])
        config_files = len([f for f in all_files if any(ext in f for ext in ['.json', '.yml', '.yaml', '.toml', 'config'])])
        source_files = len([f for f in all_files if any(ext in f for ext in ['.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp', '.c'])])
        
        total_files = len(all_files)
        
        # Determine work type based on file patterns
        if test_files / total_files > 0.5:
            return {'type': 'test', 'confidence': 0.8}
        elif doc_files / total_files > 0.5:
            return {'type': 'docs', 'confidence': 0.8}
        elif config_files / total_files > 0.3:
            return {'type': 'config', 'confidence': 0.7}
        elif source_files / total_files > 0.6:
            return {'type': 'feat', 'confidence': 0.6}
        else:
            return {'type': 'chore', 'confidence': 0.4}
    
    def generate_branch_name(self, context=None, work_type=None):
        """Generate an intelligent branch name"""
        if not work_type:
            work_detection = self.detect_work_type()
            work_type = work_detection.get('type', 'feat')
        
        if context:
            # Clean up the context for branch naming
            clean_context = re.sub(r'[^a-zA-Z0-9\s]', '', context)
            clean_context = re.sub(r'\s+', '-', clean_context.strip())
            clean_context = clean_context.lower()[:30]  # Limit length
            
            return f"{work_type}/{clean_context}"
        else:
            # Generate based on current changes
            status = self.get_git_status()
            modified_files = status.get('modified', [])
            
            if modified_files:
                # Try to infer context from modified files
                first_file = modified_files[0]
                file_base = Path(first_file).stem
                clean_name = re.sub(r'[^a-zA-Z0-9]', '-', file_base)
                return f"{work_type}/{clean_name}"
            else:
                # Fallback to timestamp
                timestamp = datetime.now().strftime('%m%d-%H%M')
                return f"{work_type}/update-{timestamp}"
    
    def create_branch(self, branch_name, base_branch=None):
        """Create a new branch"""
        try:
            # Get default base branch if not specified
            if not base_branch:
                base_branch = self.get_default_base_branch()
            
            # Ensure we're on the base branch
            subprocess.run(['git', 'checkout', base_branch], check=True, capture_output=True)
            
            # Create and switch to new branch
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True, capture_output=True)
            
            self.log(f"Created and switched to branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to create branch {branch_name}: {e}")
            return False
    
    def get_default_base_branch(self):
        """Get the default base branch (main, master, etc.)"""
        try:
            # Get all branches
            result = subprocess.run(
                ['git', 'branch', '-a'],
                capture_output=True, text=True, check=True
            )
            
            branches = result.stdout
            
            # Check for common main branches
            if 'main' in branches:
                return 'main'
            elif 'master' in branches:
                return 'master'
            elif 'develop' in branches:
                return 'develop'
            else:
                # Return current branch as fallback
                return self.get_current_branch()
                
        except subprocess.CalledProcessError:
            return 'main'  # Safe fallback
    
    def switch_branch_smart(self, target_branch, create_if_missing=False):
        """Smart branch switching with safety checks"""
        try:
            # Check if branch exists
            result = subprocess.run(
                ['git', 'branch', '-a'],
                capture_output=True, text=True
            )
            
            branch_exists = target_branch in result.stdout
            
            # Check for uncommitted changes
            status = self.get_git_status()
            has_changes = any(len(files) > 0 for files in status.values())
            
            if has_changes:
                # Stash changes before switching
                subprocess.run(['git', 'stash', 'push', '-m', f'Auto-stash before switching to {target_branch}'], 
                             check=True, capture_output=True)
                self.log("Stashed changes before branch switch")
            
            if branch_exists:
                # Switch to existing branch
                subprocess.run(['git', 'checkout', target_branch], check=True, capture_output=True)
                self.log(f"Switched to existing branch: {target_branch}")
                return True
            elif create_if_missing:
                # Create new branch
                return self.create_branch(target_branch)
            else:
                self.log(f"Branch {target_branch} does not exist and create_if_missing is False")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to switch to branch {target_branch}: {e}")
            return False
    
    def suggest_branch_action(self):
        """Suggest branch action based on current state"""
        current_branch = self.get_current_branch()
        work_type = self.detect_work_type()
        status = self.get_git_status()
        
        suggestions = []
        
        # Check if on main/master with changes
        if current_branch in ['main', 'master', 'develop'] and any(len(files) > 0 for files in status.values()):
            branch_name = self.generate_branch_name()
            suggestions.append({
                'action': 'create_branch',
                'branch_name': branch_name,
                'reason': f'Working directly on {current_branch} - consider creating feature branch',
                'priority': 'high'
            })
        
        # Check if work type suggests different branch
        if work_type['confidence'] > 0.7 and not current_branch.startswith(work_type['type']):
            branch_name = self.generate_branch_name(work_type=work_type['type'])
            suggestions.append({
                'action': 'create_branch',
                'branch_name': branch_name,
                'reason': f'Current work appears to be {work_type["type"]} but branch doesn\'t match',
                'priority': 'medium'
            })
        
        return suggestions
    
    def auto_branch_management(self, context=None):
        """Automatic branch management based on work context"""
        if self.is_mcp_server_available():
            self.log("MCP server available, skipping hook-based branch management")
            return True
        
        self.log("MCP server not available, using hook-based branch management")
        
        suggestions = self.suggest_branch_action()
        
        # Auto-create branch if high priority suggestion
        for suggestion in suggestions:
            if suggestion['priority'] == 'high' and suggestion['action'] == 'create_branch':
                print(f"🌿 Auto-creating branch: {suggestion['branch_name']}")
                print(f"   Reason: {suggestion['reason']}")
                
                if self.create_branch(suggestion['branch_name']):
                    return True
        
        # Print suggestions for user consideration
        if suggestions:
            print("🌿 Branch suggestions:")
            for suggestion in suggestions:
                print(f"   {suggestion['action']}: {suggestion.get('branch_name', 'N/A')}")
                print(f"   Reason: {suggestion['reason']}")
        
        return True

def main():
    """Main entry point for hook execution"""
    hook = IntelligentBranchHook()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'suggest':
            suggestions = hook.suggest_branch_action()
            print(json.dumps(suggestions, indent=2))
        
        elif command == 'create':
            context = sys.argv[2] if len(sys.argv) > 2 else None
            work_type = sys.argv[3] if len(sys.argv) > 3 else None
            branch_name = hook.generate_branch_name(context, work_type)
            
            if hook.create_branch(branch_name):
                print(f"✅ Created branch: {branch_name}")
            else:
                print(f"❌ Failed to create branch: {branch_name}")
        
        elif command == 'switch':
            target = sys.argv[2] if len(sys.argv) > 2 else None
            if not target:
                print("❌ Target branch name required")
                return 1
            
            create_missing = '--create' in sys.argv
            
            if hook.switch_branch_smart(target, create_missing):
                print(f"✅ Switched to branch: {target}")
            else:
                print(f"❌ Failed to switch to branch: {target}")
        
        elif command == 'auto':
            context = sys.argv[2] if len(sys.argv) > 2 else None
            hook.auto_branch_management(context)
        
        else:
            print(f"Unknown command: {command}")
            return 1
    else:
        # Default: auto branch management
        hook.auto_branch_management()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())