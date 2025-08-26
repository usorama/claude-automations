#!/usr/bin/env python3
"""
Intelligent File Watcher with Ollama Analysis
Monitors file changes in real-time and makes intelligent commit decisions.
Similar to how Cursor IDE indexes changes continuously.
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
import signal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from ollama_analyzer import OllamaGitAnalyzer

class IntelligentWatcher:
    """File watcher with intelligent analysis."""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path or os.getcwd())
        self.analyzer = OllamaGitAnalyzer()
        self.change_buffer = defaultdict(dict)
        self.file_hashes = {}
        self.watching = False
        self.check_interval = 5  # Check every 5 seconds
        self.last_commit_time = datetime.now()
        self.state_file = Path.home() / '.claude' / 'watcher-state.json'
        self.load_state()
        
        # Thresholds
        self.thresholds = {
            'time_limit': 1800,  # 30 minutes max
            'file_count': 5,      # 5 files trigger
            'line_count': 300,    # 300 lines trigger
            'test_files': 2,      # 2 test files trigger
            'config_files': 3,    # 3 config files trigger
        }
        
        # File patterns to watch
        self.watch_patterns = {
            'source': ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java'],
            'test': ['test', 'spec', '__tests__'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.env', 'config'],
            'docs': ['.md', '.rst', '.txt', 'README'],
            'critical': ['package.json', 'requirements.txt', 'Dockerfile', '.gitignore']
        }
        
    def load_state(self):
        """Load watcher state."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    state = json.load(f)
                    self.file_hashes = state.get('file_hashes', {})
                    self.last_commit_time = datetime.fromisoformat(
                        state.get('last_commit_time', datetime.now().isoformat())
                    )
            except:
                pass
                
    def save_state(self):
        """Save watcher state."""
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump({
                'file_hashes': self.file_hashes,
                'last_commit_time': self.last_commit_time.isoformat(),
                'project': str(self.project_path)
            }, f, indent=2)
            
    def get_file_hash(self, filepath: Path) -> str:
        """Get hash of file contents."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:8]
        except:
            return ""
            
    def scan_directory(self) -> Dict[str, str]:
        """Scan directory for all tracked files."""
        current_hashes = {}
        
        # Use git ls-files to get tracked files
        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for filename in result.stdout.strip().split('\n'):
                    if filename:
                        filepath = self.project_path / filename
                        if filepath.exists():
                            current_hashes[filename] = self.get_file_hash(filepath)
                            
        except:
            # Fallback to manual scan
            for pattern_list in self.watch_patterns.values():
                for pattern in pattern_list:
                    for filepath in self.project_path.rglob(f"*{pattern}*"):
                        if filepath.is_file() and '.git' not in str(filepath):
                            rel_path = str(filepath.relative_to(self.project_path))
                            current_hashes[rel_path] = self.get_file_hash(filepath)
                            
        return current_hashes
        
    def detect_changes(self) -> Dict[str, Dict]:
        """Detect what files have changed."""
        current_hashes = self.scan_directory()
        changes = {}
        
        # Find modified files
        for filepath, new_hash in current_hashes.items():
            old_hash = self.file_hashes.get(filepath)
            if old_hash != new_hash:
                change_type = 'added' if old_hash is None else 'modified'
                changes[filepath] = {
                    'type': change_type,
                    'old_hash': old_hash,
                    'new_hash': new_hash,
                    'category': self.categorize_file(filepath)
                }
                
        # Find deleted files
        for filepath in self.file_hashes:
            if filepath not in current_hashes:
                changes[filepath] = {
                    'type': 'deleted',
                    'old_hash': self.file_hashes[filepath],
                    'new_hash': None,
                    'category': self.categorize_file(filepath)
                }
                
        # Update stored hashes
        self.file_hashes = current_hashes
        self.save_state()
        
        return changes
        
    def categorize_file(self, filepath: str) -> str:
        """Categorize a file based on patterns."""
        filepath_lower = filepath.lower()
        
        # Check test files
        if any(pattern in filepath_lower for pattern in self.watch_patterns['test']):
            return 'test'
            
        # Check config files
        if any(pattern in filepath_lower for pattern in self.watch_patterns['config']):
            return 'config'
            
        # Check docs
        if any(filepath_lower.endswith(ext) for ext in self.watch_patterns['docs']):
            return 'docs'
            
        # Check critical files
        if any(pattern in filepath_lower for pattern in self.watch_patterns['critical']):
            return 'critical'
            
        # Check source files
        if any(filepath_lower.endswith(ext) for ext in self.watch_patterns['source']):
            return 'source'
            
        return 'other'
        
    def should_trigger_commit(self, changes: Dict) -> Tuple[bool, str]:
        """Determine if changes should trigger a commit."""
        
        if not changes:
            return False, ""
            
        # Count by category
        categories = defaultdict(int)
        for info in changes.values():
            categories[info['category']] += 1
            
        # Time-based trigger
        time_since_commit = datetime.now() - self.last_commit_time
        if time_since_commit.total_seconds() >= self.thresholds['time_limit'] and len(changes) > 0:
            return True, f"time_limit: {int(time_since_commit.total_seconds()/60)} minutes"
            
        # Critical file changed
        if categories['critical'] > 0:
            return True, f"critical_file: {categories['critical']} critical files modified"
            
        # Test files threshold
        if categories['test'] >= self.thresholds['test_files']:
            return True, f"test_complete: {categories['test']} test files"
            
        # Config files threshold
        if categories['config'] >= self.thresholds['config_files']:
            return True, f"config_update: {categories['config']} config files"
            
        # Total file count threshold
        if len(changes) >= self.thresholds['file_count']:
            return True, f"file_threshold: {len(changes)} files changed"
            
        # Use Ollama for intelligent decision
        if len(changes) >= 3:  # At least 3 files for AI analysis
            analysis = self.analyzer.run_analysis()
            if analysis and analysis['should_commit'] and analysis['confidence'] > 0.7:
                return True, f"ai_decision: {analysis['reason']}"
                
        return False, ""
        
    def perform_intelligent_commit(self, reason: str):
        """Perform an intelligent commit."""
        
        print(f"\n🤖 Intelligent Commit Triggered: {reason}")
        
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '-A'], cwd=self.project_path, check=True)
            
            # Get Ollama's commit message suggestion
            analysis = self.analyzer.run_analysis()
            
            if analysis and analysis.get('commit_message'):
                message = analysis['commit_message']
            else:
                # Fallback message
                message = f"auto: {reason}"
                
            # Add metadata
            message += f"\n\n[auto-commit: {reason}]"
            message += f"\n[watcher: intelligent-git]"
            message += f"\n[timestamp: {datetime.now().isoformat()}]"
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Committed: {message.split('\n')[0]}")
                self.last_commit_time = datetime.now()
                self.save_state()
                
                # Try to push (non-blocking)
                subprocess.run(
                    ['git', 'push'],
                    cwd=self.project_path,
                    capture_output=True,
                    timeout=5
                )
            else:
                print(f"❌ Commit failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
    def watch_loop(self):
        """Main watch loop."""
        print(f"👁️  Watching: {self.project_path}")
        print(f"🤖 Using Ollama model: {self.analyzer.model}")
        print("Press Ctrl+C to stop\n")
        
        # Initial scan
        self.file_hashes = self.scan_directory()
        self.save_state()
        
        while self.watching:
            try:
                time.sleep(self.check_interval)
                
                # Detect changes
                changes = self.detect_changes()
                
                if changes:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Detected {len(changes)} changes")
                    
                    # Check if we should commit
                    should_commit, reason = self.should_trigger_commit(changes)
                    
                    if should_commit:
                        self.perform_intelligent_commit(reason)
                    else:
                        # Update change buffer for next check
                        for filepath, info in changes.items():
                            self.change_buffer[filepath] = info
                            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in watch loop: {e}")
                time.sleep(1)
                
    def start(self):
        """Start watching."""
        self.watching = True
        
        # Set up signal handler
        def signal_handler(sig, frame):
            print("\n👋 Stopping watcher...")
            self.watching = False
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run watch loop
        self.watch_loop()
        
    def run_once(self):
        """Run analysis once without watching."""
        changes = self.detect_changes()
        
        if not changes:
            print("No changes detected")
            return
            
        print(f"Found {len(changes)} changes:")
        categories = defaultdict(list)
        for filepath, info in changes.items():
            categories[info['category']].append(filepath)
            
        for category, files in categories.items():
            print(f"  {category}: {len(files)} files")
            
        should_commit, reason = self.should_trigger_commit(changes)
        
        if should_commit:
            print(f"\n✅ Should commit: {reason}")
            response = input("Commit now? (y/n): ")
            if response.lower() == 'y':
                self.perform_intelligent_commit(reason)
        else:
            print("\n❌ Not enough changes for auto-commit")
            
            # Ask Ollama for advice
            analysis = self.analyzer.run_analysis()
            if analysis:
                print(f"\n🤖 AI Analysis:")
                print(f"  Pattern: {analysis.get('detected_pattern', 'unknown')}")
                print(f"  Confidence: {analysis.get('confidence', 0):.1%}")
                print(f"  Suggestion: {analysis.get('reason', 'Continue working')}")


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Git Watcher")
    parser.add_argument('path', nargs='?', default='.',
                       help='Project path to watch (default: current directory)')
    parser.add_argument('--once', action='store_true',
                       help='Run analysis once without watching')
    parser.add_argument('--interval', type=int, default=5,
                       help='Check interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    watcher = IntelligentWatcher(args.path)
    watcher.check_interval = args.interval
    
    if args.once:
        watcher.run_once()
    else:
        watcher.start()


if __name__ == "__main__":
    main()