#!/usr/bin/env python3
"""
Real-Time Development Automation System
Monitors file changes and triggers:
1. Manifest updates on ANY change
2. Auto-commits every 30 minutes
3. PR creation when appropriate
4. Continuous checkpoint management
"""

import os
import sys
import time
import json
import subprocess
import threading
import signal
from datetime import datetime, timedelta
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib

# Configuration
CHECKPOINT_INTERVAL = 1800  # 30 minutes
MANIFEST_UPDATE_DELAY = 5   # 5 seconds after changes stop
COMMIT_BATCH_SIZE = 50       # Commit after 50 file changes
PR_THRESHOLD = 200           # Create PR after 200 changes

class RealTimeAutomation:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path or os.getcwd())
        self.last_checkpoint = datetime.now()
        self.last_manifest_update = datetime.now()
        self.pending_changes = set()
        self.change_count = 0
        self.running = True
        self.manifest_timer = None
        self.checkpoint_file = Path.home() / '.claude' / 'automation' / 'state.json'
        self.load_state()
        
    def load_state(self):
        """Load saved automation state"""
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                state = json.load(f)
                self.last_checkpoint = datetime.fromisoformat(state.get('last_checkpoint', datetime.now().isoformat()))
                self.change_count = state.get('change_count', 0)
    
    def save_state(self):
        """Save automation state"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump({
                'last_checkpoint': self.last_checkpoint.isoformat(),
                'last_manifest_update': self.last_manifest_update.isoformat(),
                'change_count': self.change_count,
                'project': str(self.project_path)
            }, f, indent=2)
    
    def update_manifests(self):
        """Update all manifests intelligently"""
        print(f"📊 Updating manifests for {len(self.pending_changes)} changes...")
        
        try:
            # Use our smart manifest update command
            result = subprocess.run([
                'python3',
                str(Path.home() / '.claude' / 'automation' / 'smart-manifest-update.py'),
                '--incremental',
                '--preserve-manual'
            ], cwd=self.project_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Manifests updated successfully")
                self.last_manifest_update = datetime.now()
                self.pending_changes.clear()
            else:
                print(f"⚠️ Manifest update warning: {result.stderr}")
        except Exception as e:
            print(f"❌ Manifest update error: {e}")
    
    def create_checkpoint(self):
        """Create git checkpoint commit"""
        try:
            # Check for changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                return False
            
            # Count changes
            changes = result.stdout.strip().split('\n')
            added = len([l for l in changes if l.startswith('A ') or l.startswith('?? ')])
            modified = len([l for l in changes if l.startswith('M ')])
            deleted = len([l for l in changes if l.startswith('D ')])
            
            # Generate commit message
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            summary = []
            if added: summary.append(f"{added} new")
            if modified: summary.append(f"{modified} modified")
            if deleted: summary.append(f"{deleted} deleted")
            
            message = f"checkpoint: {', '.join(summary)} files - {timestamp}"
            
            # Stage all changes
            subprocess.run(['git', 'add', '-A'], cwd=self.project_path)
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message, '--no-verify'],
                cwd=self.project_path,
                capture_output=True
            )
            
            if result.returncode == 0:
                print(f"✅ Checkpoint created: {message}")
                self.last_checkpoint = datetime.now()
                self.change_count = 0
                self.save_state()
                
                # Check if we should create PR
                self.check_pr_threshold()
                return True
            
        except Exception as e:
            print(f"❌ Checkpoint error: {e}")
        
        return False
    
    def check_pr_threshold(self):
        """Check if we should create a PR"""
        try:
            # Count commits since last PR
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'origin/main..HEAD'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            commit_count = int(result.stdout.strip())
            
            if commit_count >= 10:  # Create PR after 10 commits
                print("🚀 Creating PR for accumulated changes...")
                self.create_pr()
                
        except Exception as e:
            print(f"⚠️ PR check error: {e}")
    
    def create_pr(self):
        """Create GitHub PR"""
        try:
            # Push to remote
            branch_name = f"auto-checkpoint-{datetime.now().strftime('%Y%m%d-%H%M')}"
            subprocess.run(['git', 'checkout', '-b', branch_name], cwd=self.project_path)
            subprocess.run(['git', 'push', '-u', 'origin', branch_name], cwd=self.project_path)
            
            # Create PR using gh CLI
            pr_title = f"Auto-checkpoint: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            pr_body = "Automated checkpoint of recent development work"
            
            result = subprocess.run([
                'gh', 'pr', 'create',
                '--title', pr_title,
                '--body', pr_body,
                '--base', 'main'
            ], cwd=self.project_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ PR created: {result.stdout.strip()}")
            else:
                print(f"⚠️ PR creation failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ PR creation error: {e}")
    
    def schedule_manifest_update(self):
        """Schedule manifest update after changes settle"""
        if self.manifest_timer:
            self.manifest_timer.cancel()
        
        self.manifest_timer = threading.Timer(MANIFEST_UPDATE_DELAY, self.update_manifests)
        self.manifest_timer.start()
    
    def periodic_checkpoint(self):
        """Run periodic checkpoints"""
        while self.running:
            time_since_checkpoint = datetime.now() - self.last_checkpoint
            
            if time_since_checkpoint.total_seconds() >= CHECKPOINT_INTERVAL:
                print(f"\n⏰ Periodic checkpoint (30 minutes)...")
                self.create_checkpoint()
            
            # Check every minute
            time.sleep(60)
    
    def start(self):
        """Start the automation system"""
        print("🚀 Real-Time Automation System Started")
        print(f"📍 Monitoring: {self.project_path}")
        print(f"⏰ Checkpoints: Every {CHECKPOINT_INTERVAL//60} minutes")
        print(f"📊 Manifests: Update on file changes")
        print("-" * 50)
        
        # Start file watcher
        event_handler = FileChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.project_path), recursive=True)
        observer.start()
        
        # Start periodic checkpoint thread
        checkpoint_thread = threading.Thread(target=self.periodic_checkpoint)
        checkpoint_thread.daemon = True
        checkpoint_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            observer.stop()
        
        observer.join()
    
    def stop(self):
        """Stop the automation system"""
        print("\n🛑 Stopping automation system...")
        self.running = False
        if self.manifest_timer:
            self.manifest_timer.cancel()
        self.save_state()

class FileChangeHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, automation):
        self.automation = automation
        self.ignore_patterns = [
            '.git/', 'node_modules/', '.claude/automation/',
            '__pycache__/', '.pytest_cache/', '.next/'
        ]
    
    def should_ignore(self, path):
        """Check if path should be ignored"""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.ignore_patterns)
    
    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.handle_change(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.handle_change(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.handle_change(event.src_path)
    
    def handle_change(self, path):
        """Handle a file change"""
        self.automation.pending_changes.add(path)
        self.automation.change_count += 1
        
        # Schedule manifest update (debounced)
        self.automation.schedule_manifest_update()
        
        # Check if we should checkpoint based on change count
        if self.automation.change_count >= COMMIT_BATCH_SIZE:
            print(f"\n📦 Batch checkpoint ({COMMIT_BATCH_SIZE} changes)...")
            self.automation.create_checkpoint()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Received shutdown signal...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get project path from argument or current directory
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    # Check if it's a git repository
    if not os.path.exists(os.path.join(project_path, '.git')):
        print("❌ Error: Not a git repository")
        print("Usage: real-time-system.py [project-path]")
        sys.exit(1)
    
    # Start automation
    automation = RealTimeAutomation(project_path)
    automation.start()

if __name__ == '__main__':
    main()