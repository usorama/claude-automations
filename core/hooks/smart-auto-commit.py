#!/usr/bin/env python3
"""
Smart Auto-Commit Hook for Claude Code
Automatically creates checkpoint commits based on intelligent triggers.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import threading
import hashlib

# Add git-intelligence and hook logger to path
GIT_INTEL_PATH = Path.home() / 'claude-automations' / 'git-intelligence' / 'src'
HOOKS_PATH = Path.home() / 'claude-automations' / 'core' / 'hooks'
sys.path.insert(0, str(GIT_INTEL_PATH))
sys.path.insert(0, str(HOOKS_PATH))

# Import logger
from hook_logger import HookLogger, logged_hook

# Configuration
CONFIG_FILE = Path.home() / '.claude' / 'smart-commit-config.json'
STATE_FILE = Path.home() / '.claude' / 'smart-commit-state.json'

# Default configuration
DEFAULT_CONFIG = {
    'enabled': True,
    'time_interval': 1800,  # 30 minutes
    'file_threshold': 5,    # Auto-commit after 5 files changed
    'auto_push': True,       # Push after commit
    'silent_mode': True,     # Minimal output
    'work_patterns': {
        'feature': {'keywords': ['add', 'implement', 'create'], 'threshold': 3},
        'bugfix': {'keywords': ['fix', 'resolve', 'patch'], 'threshold': 2},
        'refactor': {'keywords': ['refactor', 'reorganize', 'restructure'], 'threshold': 4}
    }
}

class SmartAutoCommit:
    def __init__(self):
        self.logger = HookLogger('smart-auto-commit')
        self.config = self.load_config()
        self.state = self.load_state()
        self.last_commit_time = self.state.get('last_commit_time', datetime.now().isoformat())
        self.last_file_hashes = self.state.get('file_hashes', {})
        self.logger.info("SmartAutoCommit initialized", config=self.config)
        
    def load_config(self):
        """Load configuration or create default"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        return DEFAULT_CONFIG
    
    def load_state(self):
        """Load saved state"""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {}
    
    def save_state(self):
        """Save current state"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump({
                'last_commit_time': self.last_commit_time,
                'file_hashes': self.last_file_hashes,
                'last_check': datetime.now().isoformat()
            }, f, indent=2)
    
    def get_repo_root(self):
        """Find git repository root"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
            return Path(result.stdout.strip())
        except:
            return None
    
    def get_changed_files(self):
        """Get list of changed files"""
        try:
            # Get all changed files (staged, unstaged, untracked)
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, check=True
            )
            
            changed_files = []
            for line in result.stdout.splitlines():
                if line.strip():
                    # Extract filename (skip status codes)
                    filename = line[3:].strip()
                    changed_files.append(filename)
            
            return changed_files
        except:
            return []
    
    def should_commit_time_based(self):
        """Check if enough time has passed"""
        last_time = datetime.fromisoformat(self.last_commit_time)
        time_since = datetime.now() - last_time
        return time_since.total_seconds() >= self.config['time_interval']
    
    def should_commit_file_based(self):
        """Check if enough files have changed"""
        changed_files = self.get_changed_files()
        return len(changed_files) >= self.config['file_threshold']
    
    def detect_operation_completion(self):
        """Detect if a major operation was completed"""
        # Look for patterns indicating completed work
        try:
            # Check recent file changes for patterns
            changed_files = self.get_changed_files()
            
            # Test files added/modified - likely finished a feature
            test_files = [f for f in changed_files if 'test' in f.lower()]
            if len(test_files) >= 2:
                return 'test_completion'
            
            # Documentation updated - likely finished documenting
            doc_files = [f for f in changed_files if any(ext in f for ext in ['.md', '.rst', '.txt'])]
            if len(doc_files) >= 3:
                return 'documentation_update'
            
            # Config files changed - likely finished configuration
            config_files = [f for f in changed_files if any(name in f for name in ['config', 'settings', '.env', '.yml', '.yaml'])]
            if len(config_files) >= 2:
                return 'configuration_update'
            
            return None
        except:
            return None
    
    def generate_commit_message(self, trigger_reason):
        """Generate intelligent commit message"""
        try:
            from git_state_analyzer import GitStateAnalyzer
            from commit_generator import CommitMessageGenerator, CommitConfig
            
            # Analyze repository
            repo_root = self.get_repo_root()
            if not repo_root:
                return f"checkpoint: {trigger_reason}"
            
            analyzer = GitStateAnalyzer(str(repo_root))
            state = analyzer.analyze()
            
            # Generate message
            config = CommitConfig(
                format_type='conventional',
                include_body=False,  # Keep it concise for auto-commits
                max_subject_length=50
            )
            generator = CommitMessageGenerator(config=config)
            suggestions = generator.generate_commit_message()
            
            if suggestions and suggestions.primary_suggestion:
                message = suggestions.primary_suggestion.formatted_message
                # Add auto-commit indicator
                if '\n\n' in message:
                    message = message.replace('\n\n', f'\n\n[auto-commit: {trigger_reason}]\n\n', 1)
                else:
                    message += f"\n\n[auto-commit: {trigger_reason}]"
                return message
            else:
                return f"checkpoint: {trigger_reason}"
        except Exception as e:
            # Fallback message
            return f"checkpoint: auto-save ({trigger_reason})"
    
    def perform_commit(self, trigger_reason):
        """Perform the actual commit"""
        repo_root = self.get_repo_root()
        if not repo_root:
            self.logger.warning("Not in a git repository")
            return False
        
        # Check if there are changes
        changed_files = self.get_changed_files()
        if not changed_files:
            self.logger.info("No changes to commit")
            return False
        
        self.logger.info(f"Committing {len(changed_files)} files", repo=str(repo_root))
        
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '-A'], check=True)
            self.logger.info("Staged all changes")
            
            # Generate commit message
            message = self.generate_commit_message(trigger_reason)
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True, text=True
            )
            self.logger.info(f"Commit attempt completed", message=message[:100])
            
            if result.returncode == 0:
                # Update state
                self.last_commit_time = datetime.now().isoformat()
                self.save_state()
                
                # Get commit hash
                commit_hash = subprocess.run(
                    ['git', 'rev-parse', '--short', 'HEAD'],
                    capture_output=True, text=True
                ).stdout.strip()
                
                if not self.config['silent_mode']:
                    print(f"✅ Auto-commit created: {commit_hash} ({trigger_reason})")
                
                # Auto-push if configured
                if self.config['auto_push']:
                    self.push_changes()
                
                return True
            
        except Exception as e:
            self.logger.error(e, "Auto-commit failed")
            if not self.config['silent_mode']:
                print(f"⚠️ Auto-commit failed: {e}")
            return False
    
    def push_changes(self):
        """Push changes to remote"""
        try:
            result = subprocess.run(
                ['git', 'push'],
                capture_output=True, text=True,
                timeout=10  # Don't wait forever
            )
            if result.returncode == 0 and not self.config['silent_mode']:
                print("✅ Auto-pushed to remote")
        except:
            pass  # Silent fail for push - commit is safe locally
    
    def check_triggers(self):
        """Check all triggers and commit if needed"""
        if not self.config['enabled']:
            self.logger.info("Auto-commit disabled in config")
            return
        
        self.logger.info("Checking triggers")
        
        # Priority order of triggers
        triggers = []
        
        # 1. Operation completion (highest priority)
        operation = self.detect_operation_completion()
        if operation:
            triggers.append(operation)
            self.logger.info(f"Operation trigger detected: {operation}")
        
        # 2. File threshold
        if self.should_commit_file_based():
            triggers.append('file_threshold')
            changed = len(self.get_changed_files())
            self.logger.info(f"File threshold trigger: {changed} files changed")
        
        # 3. Time interval (lowest priority)
        if self.should_commit_time_based():
            triggers.append('time_interval')
            self.logger.info("Time interval trigger activated")
        
        # Commit if any trigger is active
        if triggers:
            trigger_reason = triggers[0]  # Use highest priority trigger
            self.logger.info(f"Performing commit with trigger: {trigger_reason}")
            success = self.perform_commit(trigger_reason)
            if success:
                self.logger.success(f"Auto-commit successful: {trigger_reason}")
            else:
                self.logger.warning(f"Auto-commit failed for trigger: {trigger_reason}")
        else:
            self.logger.info("No triggers activated")
    
    def run_continuous(self):
        """Run continuous monitoring"""
        check_interval = 60  # Check every minute
        self.logger.info("Starting continuous monitoring", interval=check_interval)
        
        while True:
            try:
                self.check_triggers()
                time.sleep(check_interval)
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(e, "Error during monitoring")
                if not self.config['silent_mode']:
                    print(f"⚠️ Auto-commit error: {e}")
                time.sleep(check_interval)

def main():
    """Main entry point for the hook"""
    # Check if we're in a git repository
    if not subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         capture_output=True).returncode == 0:
        print("Not in a git repository")
        return
    
    # Run the auto-commit monitor
    monitor = SmartAutoCommit()
    
    # Check for immediate triggers
    monitor.check_triggers()
    
    # For continuous monitoring (optional - can be run as daemon)
    if '--daemon' in sys.argv:
        print("🚀 Smart Auto-Commit daemon started")
        monitor.run_continuous()

if __name__ == '__main__':
    main()