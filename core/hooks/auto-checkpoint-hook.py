#!/usr/bin/env python3
"""
Auto-Checkpoint Hook - Creates checkpoint commits every 30 minutes or after major operations
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import threading
import signal

CHECKPOINT_INTERVAL = 1800  # 30 minutes in seconds
CHECKPOINT_FILE = Path.home() / '.claude' / 'last_checkpoint.json'

class AutoCheckpointer:
    def __init__(self):
        self.last_checkpoint = self.load_last_checkpoint()
        self.running = True
        
    def load_last_checkpoint(self):
        """Load the timestamp of the last checkpoint"""
        if CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE) as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get('timestamp', ''))
        return datetime.now() - timedelta(hours=1)  # Force immediate checkpoint
    
    def save_checkpoint_time(self):
        """Save the current time as last checkpoint"""
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'commit_hash': self.get_last_commit_hash()
            }, f)
    
    def get_last_commit_hash(self):
        """Get the hash of the last commit"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()[:7]  # Short hash
        except subprocess.CalledProcessError:
            return 'unknown'
    
    def has_changes(self):
        """Check if there are uncommitted changes"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() != ''
        except subprocess.CalledProcessError:
            return False
    
    def get_change_summary(self):
        """Generate a summary of changes"""
        try:
            # Get list of modified files
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            if not lines or lines == ['']:
                return "No changes"
            
            # Count changes by type
            added = len([l for l in lines if l.startswith('A ') or l.startswith('?? ')])
            modified = len([l for l in lines if l.startswith('M ') or l.startswith(' M')])
            deleted = len([l for l in lines if l.startswith('D ')])
            
            summary_parts = []
            if added:
                summary_parts.append(f"{added} added")
            if modified:
                summary_parts.append(f"{modified} modified")
            if deleted:
                summary_parts.append(f"{deleted} deleted")
            
            return ', '.join(summary_parts) if summary_parts else "Minor changes"
            
        except subprocess.CalledProcessError:
            return "Changes detected"
    
    def generate_semantic_commit_message(self):
        """Generate a semantic commit message based on changes"""
        try:
            # Check what files were changed
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = result.stdout.strip().split('\n')
            
            # Determine commit type based on changed files
            if any('.github/workflows' in f for f in changed_files):
                prefix = 'ci'
                desc = 'Update CI/CD workflows'
            elif any('test' in f.lower() for f in changed_files):
                prefix = 'test'
                desc = 'Update test files'
            elif any('doc' in f.lower() or '.md' in f for f in changed_files):
                prefix = 'docs'
                desc = 'Update documentation'
            elif any('hook' in f for f in changed_files):
                prefix = 'feat'
                desc = 'Update automation hooks'
            elif any('manifest' in f for f in changed_files):
                prefix = 'feat'
                desc = 'Update code intelligence manifests'
            else:
                prefix = 'chore'
                desc = self.get_change_summary()
            
            timestamp = datetime.now().strftime('%H:%M')
            return f"{prefix}: {desc} [{timestamp}]"
            
        except subprocess.CalledProcessError:
            return f"chore: Auto-checkpoint [{datetime.now().strftime('%H:%M')}]"
    
    def create_checkpoint_commit(self):
        """Create a checkpoint commit"""
        if not self.has_changes():
            print("📝 No changes to checkpoint")
            return False
        
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '-A'], check=True)
            
            # Generate commit message
            message = self.generate_semantic_commit_message()
            
            # Create commit
            result = subprocess.run([
                'git', 'commit', '-m', 
                f"{message}\n\n🔄 Auto-checkpoint\n{self.get_change_summary()}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                commit_hash = self.get_last_commit_hash()
                print(f"✅ Checkpoint created: {commit_hash} - {message}")
                self.save_checkpoint_time()
                return True
            else:
                print(f"⚠️ Checkpoint failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating checkpoint: {e}")
            return False
    
    def should_checkpoint(self):
        """Check if enough time has passed for a checkpoint"""
        time_since_last = datetime.now() - self.last_checkpoint
        return time_since_last.total_seconds() >= CHECKPOINT_INTERVAL
    
    def checkpoint_after_operation(self, operation_type='operation'):
        """Create checkpoint after a major operation"""
        print(f"🎯 Checkpoint after {operation_type}...")
        if self.create_checkpoint_commit():
            return True
        return False
    
    def run_periodic_checkpoints(self):
        """Run checkpoints periodically in the background"""
        while self.running:
            if self.should_checkpoint():
                print(f"\n⏰ Periodic checkpoint (every {CHECKPOINT_INTERVAL//60} minutes)...")
                self.create_checkpoint_commit()
            
            # Check every minute
            time.sleep(60)
    
    def stop(self):
        """Stop the checkpointer"""
        self.running = False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Stopping auto-checkpoint...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("Not in a git repository")
        return
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--daemon':
            # Run as daemon for periodic checkpoints
            print("🚀 Starting auto-checkpoint daemon...")
            print(f"📍 Checkpoints every {CHECKPOINT_INTERVAL//60} minutes")
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            checkpointer = AutoCheckpointer()
            checkpointer.run_periodic_checkpoints()
            
        elif sys.argv[1] == '--now':
            # Force immediate checkpoint
            print("💾 Creating checkpoint now...")
            checkpointer = AutoCheckpointer()
            checkpointer.create_checkpoint_commit()
            
        elif sys.argv[1] == '--after':
            # Checkpoint after specific operation
            operation = sys.argv[2] if len(sys.argv) > 2 else 'operation'
            checkpointer = AutoCheckpointer()
            checkpointer.checkpoint_after_operation(operation)
    else:
        # Default: create checkpoint if needed
        checkpointer = AutoCheckpointer()
        if checkpointer.should_checkpoint():
            print("⏰ Time for checkpoint...")
            checkpointer.create_checkpoint_commit()
        else:
            time_until = CHECKPOINT_INTERVAL - (datetime.now() - checkpointer.last_checkpoint).total_seconds()
            print(f"⏳ Next checkpoint in {int(time_until//60)} minutes")

if __name__ == '__main__':
    main()