#!/usr/bin/env python3
"""
Session Lifecycle Manager - Automatic commit and PR management for Claude Code sessions
"""

import subprocess
import json
import os
import sys
import signal
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class SessionLifecycleManager:
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.session_file = self.claude_dir / 'current_session.json'
        self.checkpoint_interval = 1800  # 30 minutes
        self.running = True
        self.last_activity_check = datetime.now()
        self.checkpoint_daemon = None
        
    def detect_claude_session(self):
        """Detect if Claude Code is currently running"""
        if not HAS_PSUTIL:
            # Fallback method using ps command
            try:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                return 'claude' in result.stdout.lower()
            except Exception:
                return True  # Assume session is active if we can't detect
        
        try:
            # Look for Claude Code processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'claude' in proc.info['name'].lower():
                        return True
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline']).lower()
                        if 'claude-code' in cmdline or 'claude.ai' in cmdline:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False
    
    def get_current_project_path(self):
        """Detect current project path from various indicators"""
        # Check if we're in a git repository
        for parent in Path.cwd().parents:
            if (parent / '.git').exists():
                return str(parent)
        
        # Fallback to current directory if it has project indicators
        current = Path.cwd()
        if any((current / f).exists() for f in ['package.json', 'pyproject.toml', 'Cargo.toml', '.claude']):
            return str(current)
        
        return None
    
    def start_session(self, project_path=None):
        """Start a new Claude Code session with automatic management"""
        if not project_path:
            project_path = self.get_current_project_path()
        
        if not project_path:
            print("⚠️ No project detected. Manual project path required.")
            return False
        
        session_data = {
            'project_path': project_path,
            'start_time': datetime.now().isoformat(),
            'last_checkpoint': datetime.now().isoformat(),
            'commit_count': 0,
            'auto_pr_created': False,
            'pid': os.getpid()
        }
        
        # Save session data
        self.session_file.write_text(json.dumps(session_data, indent=2))
        
        print(f"🚀 Starting Claude Code session management")
        print(f"📁 Project: {project_path}")
        print(f"⏰ Auto-checkpoints every {self.checkpoint_interval//60} minutes")
        
        # Start checkpoint daemon
        self.start_checkpoint_daemon(project_path)
        
        # Start activity monitoring
        self.start_activity_monitoring(project_path)
        
        # Initialize branch intelligence
        self.initialize_branch_intelligence(project_path)
        
        return True
    
    def start_checkpoint_daemon(self, project_path):
        """Start the checkpoint daemon as a background thread"""
        def checkpoint_worker():
            while self.running:
                try:
                    time.sleep(self.checkpoint_interval)
                    if self.running:
                        self.create_auto_checkpoint(project_path)
                except Exception as e:
                    print(f"⚠️ Checkpoint daemon error: {e}")
        
        self.checkpoint_daemon = threading.Thread(target=checkpoint_worker, daemon=True)
        self.checkpoint_daemon.start()
        print("✅ Checkpoint daemon started")
    
    def start_activity_monitoring(self, project_path):
        """Monitor file system activity and create commits when appropriate"""
        def activity_worker():
            last_check = datetime.now()
            significant_changes_threshold = 5  # files
            
            while self.running:
                try:
                    time.sleep(300)  # Check every 5 minutes
                    if self.running:
                        changes = self.check_project_changes(project_path)
                        
                        # Auto-commit if significant changes detected
                        if changes >= significant_changes_threshold:
                            print(f"📝 Detected {changes} changed files - creating auto-commit")
                            self.create_smart_commit(project_path)
                        
                        # Check for PR creation opportunities
                        self.check_pr_creation_opportunity(project_path)
                        
                except Exception as e:
                    print(f"⚠️ Activity monitoring error: {e}")
                
                time.sleep(60)  # Base monitoring interval
        
        activity_thread = threading.Thread(target=activity_worker, daemon=True)
        activity_thread.start()
        print("✅ Activity monitoring started")
    
    def initialize_branch_intelligence(self, project_path):
        """Initialize branch intelligence for the project"""
        print("🌿 Initializing branch intelligence...")
        try:
            os.chdir(project_path)
            
            # Try to use MCP server first, fallback to hooks
            branch_hook_path = Path.home() / '.claude' / 'hooks' / 'git-branch' / 'pre-work-start.sh'
            
            if branch_hook_path.exists():
                subprocess.run([
                    str(branch_hook_path)
                ], cwd=project_path, capture_output=True)
                print("✅ Branch intelligence initialized")
            else:
                # Fallback to Python hook
                python_hook_path = Path.home() / '.claude' / 'hooks' / 'git-branch' / 'intelligent-branch-hook.py'
                if python_hook_path.exists():
                    subprocess.run([
                        'python3', str(python_hook_path), 'auto'
                    ], cwd=project_path, capture_output=True)
                    print("✅ Branch intelligence initialized (fallback)")
                else:
                    print("⚠️ Branch intelligence hooks not found")
            
        except Exception as e:
            print(f"⚠️ Branch intelligence initialization failed: {e}")
    
    def check_project_changes(self, project_path):
        """Count uncommitted changes in project"""
        try:
            os.chdir(project_path)
            
            # Get number of changed files
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, check=True
            )
            
            if result.stdout.strip():
                return len(result.stdout.strip().split('\n'))
            return 0
            
        except Exception:
            return 0
    
    def create_auto_checkpoint(self, project_path):
        """Create automatic checkpoint commit"""
        try:
            os.chdir(project_path)
            
            # Check if there are changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True
            )
            
            if not result.stdout.strip():
                print("📝 No changes for checkpoint")
                return
            
            # Use the existing checkpoint hook
            subprocess.run([
                'python3', str(Path.home() / '.claude' / 'hooks' / 'auto-checkpoint-hook.py'), '--now'
            ], cwd=project_path)
            
            # Update session data
            self.update_session_checkpoint_count()
            
            # Auto-push to backup (optional)
            self.auto_push_backup(project_path)
            
        except Exception as e:
            print(f"⚠️ Auto-checkpoint failed: {e}")
    
    def create_smart_commit(self, project_path):
        """Create intelligent commit based on file changes"""
        try:
            os.chdir(project_path)
            
            # Analyze changes to create smart commit message
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True, text=True
            )
            
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            if not changed_files:
                return
            
            # Generate smart commit message
            commit_msg = self.generate_smart_commit_message(changed_files)
            
            # Stage and commit
            subprocess.run(['git', 'add', '-A'], check=True)
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            print(f"✅ Smart commit created: {commit_msg}")
            
            # Update session data
            self.update_session_commit_count()
            
        except Exception as e:
            print(f"⚠️ Smart commit failed: {e}")
    
    def generate_smart_commit_message(self, changed_files):
        """Generate intelligent commit message based on changed files"""
        timestamp = datetime.now().strftime('%H:%M')
        
        # Categorize files
        categories = {
            'docs': [f for f in changed_files if any(doc in f.lower() for doc in ['readme', 'doc', '.md'])],
            'config': [f for f in changed_files if any(cfg in f.lower() for cfg in ['config', '.json', '.yml', '.toml'])],
            'tests': [f for f in changed_files if 'test' in f.lower()],
            'src': [f for f in changed_files if any(src in f for src in ['src/', 'lib/', 'app/'])],
            'other': []
        }
        
        # Uncategorized files go to 'other'
        categorized = set()
        for files in categories.values():
            categorized.update(files)
        categories['other'] = [f for f in changed_files if f not in categorized]
        
        # Generate message based on primary category
        if categories['src']:
            if len(categories['src']) == 1:
                return f"feat: update {categories['src'][0]} [{timestamp}]"
            else:
                return f"feat: update {len(categories['src'])} source files [{timestamp}]"
        elif categories['docs']:
            return f"docs: update documentation [{timestamp}]"
        elif categories['config']:
            return f"config: update configuration files [{timestamp}]"
        elif categories['tests']:
            return f"test: update test files [{timestamp}]"
        else:
            return f"chore: update {len(changed_files)} files [{timestamp}]"
    
    def check_pr_creation_opportunity(self, project_path):
        """Check if it's time to create a PR automatically"""
        try:
            session_data = self.load_session_data()
            if not session_data or session_data.get('auto_pr_created'):
                return
            
            os.chdir(project_path)
            
            # Check current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True
            )
            
            current_branch = result.stdout.strip()
            if current_branch in ['main', 'master', 'develop']:
                return  # Don't create PR from main branches
            
            # Check commit count and time since start
            start_time = datetime.fromisoformat(session_data['start_time'])
            time_elapsed = datetime.now() - start_time
            commit_count = session_data.get('commit_count', 0)
            
            # Create PR if significant work done
            should_create_pr = (
                commit_count >= 5 or  # At least 5 commits
                time_elapsed > timedelta(hours=2)  # Or 2+ hours of work
            )
            
            if should_create_pr:
                self.create_automatic_pr(project_path)
                
        except Exception as e:
            print(f"⚠️ PR creation check failed: {e}")
    
    def create_automatic_pr(self, project_path):
        """Create automatic PR for current work"""
        try:
            # Use existing PR creation hook
            subprocess.run([
                'python3', str(Path.home() / '.claude' / 'hooks' / 'pr-creation-hook.py'), '--force'
            ], cwd=project_path)
            
            # Mark PR as created
            session_data = self.load_session_data()
            if session_data:
                session_data['auto_pr_created'] = True
                self.session_file.write_text(json.dumps(session_data, indent=2))
            
            print("✅ Automatic PR created for current work session")
            
        except Exception as e:
            print(f"⚠️ Automatic PR creation failed: {e}")
    
    def auto_push_backup(self, project_path):
        """Automatically push commits for backup (optional)"""
        try:
            os.chdir(project_path)
            
            # Check if we have a remote
            result = subprocess.run(
                ['git', 'remote'],
                capture_output=True, text=True
            )
            
            if not result.stdout.strip():
                return  # No remote configured
            
            # Get current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True
            )
            
            current_branch = result.stdout.strip()
            
            # Push to remote for backup
            subprocess.run(['git', 'push', '-u', 'origin', current_branch], 
                         capture_output=True)
            
            print(f"📤 Auto-pushed backup to origin/{current_branch}")
            
        except Exception:
            # Silent fail - backup is optional
            pass
    
    def load_session_data(self):
        """Load current session data"""
        try:
            if self.session_file.exists():
                return json.loads(self.session_file.read_text())
        except Exception:
            pass
        return None
    
    def update_session_checkpoint_count(self):
        """Update checkpoint count in session data"""
        session_data = self.load_session_data()
        if session_data:
            session_data['last_checkpoint'] = datetime.now().isoformat()
            self.session_file.write_text(json.dumps(session_data, indent=2))
    
    def update_session_commit_count(self):
        """Update commit count in session data"""
        session_data = self.load_session_data()
        if session_data:
            session_data['commit_count'] = session_data.get('commit_count', 0) + 1
            self.session_file.write_text(json.dumps(session_data, indent=2))
    
    def end_session(self):
        """End current session and cleanup"""
        print("🛑 Ending Claude Code session...")
        
        self.running = False
        
        # Final checkpoint
        session_data = self.load_session_data()
        if session_data and session_data.get('project_path'):
            print("📝 Creating final checkpoint...")
            self.create_auto_checkpoint(session_data['project_path'])
        
        # Remove session file
        if self.session_file.exists():
            self.session_file.unlink()
        
        print("✅ Session ended cleanly")
    
    def status(self):
        """Show current session status"""
        session_data = self.load_session_data()
        
        if not session_data:
            print("❌ No active Claude Code session")
            return
        
        start_time = datetime.fromisoformat(session_data['start_time'])
        duration = datetime.now() - start_time
        
        print("📊 Claude Code Session Status")
        print("=" * 40)
        print(f"📁 Project: {session_data['project_path']}")
        print(f"⏰ Duration: {duration}")
        print(f"📝 Commits: {session_data.get('commit_count', 0)}")
        print(f"🔄 Last checkpoint: {session_data.get('last_checkpoint', 'Never')}")
        print(f"🚀 Auto-PR created: {'Yes' if session_data.get('auto_pr_created') else 'No'}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    manager = SessionLifecycleManager()
    manager.end_session()
    sys.exit(0)

def main():
    manager = SessionLifecycleManager()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            project_path = sys.argv[2] if len(sys.argv) > 2 else None
            if manager.start_session(project_path):
                try:
                    # Keep the session alive
                    while True:
                        time.sleep(10)
                        if not manager.detect_claude_session():
                            print("🔍 Claude Code session ended - stopping automation")
                            break
                except KeyboardInterrupt:
                    pass
                finally:
                    manager.end_session()
        
        elif command == 'stop':
            manager.end_session()
        
        elif command == 'status':
            manager.status()
        
        elif command == 'checkpoint':
            session_data = manager.load_session_data()
            if session_data:
                manager.create_auto_checkpoint(session_data['project_path'])
            else:
                print("❌ No active session")
        
        else:
            print("Usage: session-lifecycle-manager.py {start|stop|status|checkpoint} [project_path]")
    
    else:
        print("Usage: session-lifecycle-manager.py {start|stop|status|checkpoint} [project_path]")

if __name__ == '__main__':
    main()