#!/usr/bin/env python3
"""
Post-Edit Auto-Commit Hook
Triggers after file edits to check if auto-commit is needed.
Lightweight check that delegates to smart-auto-commit.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add hook logger to path
sys.path.insert(0, str(Path.home() / 'claude-automations' / 'core' / 'hooks'))
from hook_logger import HookLogger

def main():
    """Check if auto-commit should run after edit."""
    logger = HookLogger('post-edit-auto-commit')
    
    try:
        # Get hook input from Claude Code
        hook_input = json.loads(os.environ.get('CLAUDE_HOOK_INPUT', '{}'))
        tool_name = hook_input.get('tool', {}).get('name', 'unknown')
        
        logger.start({
            'tool': tool_name,
            'cwd': os.getcwd()
        })
        
        # Only proceed for file modification tools
        if tool_name not in ['Write', 'Edit', 'MultiEdit', 'NotebookEdit']:
            logger.info(f"Skipping - tool {tool_name} doesn't modify files")
            return 0
            
        # Check if we're in a git repository
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.info("Not in a git repository")
            return 0
            
        # Check for uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        changed_files = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        if changed_files == 0:
            logger.info("No uncommitted changes")
            return 0
            
        logger.info(f"Found {changed_files} uncommitted files")
        
        # Check thresholds for auto-commit
        STATE_FILE = Path.home() / '.claude' / 'auto-commit-state.json'
        
        # Load or create state
        state = {}
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    state = json.load(f)
            except:
                state = {}
                
        # Update file count
        last_count = state.get('last_file_count', 0)
        last_commit = state.get('last_commit_time', '')
        
        # Auto-commit triggers
        should_commit = False
        reason = ""
        
        # Trigger 1: More than 10 files changed
        if changed_files >= 10:
            should_commit = True
            reason = f"file_threshold ({changed_files} files)"
            
        # Trigger 2: Important files modified
        important_patterns = ['.md', 'package.json', 'requirements.txt', 'Dockerfile', '.yml', '.yaml']
        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            changed_names = result.stdout.strip().split('\n')
            important_changed = [f for f in changed_names if any(p in f for p in important_patterns)]
            if important_changed:
                should_commit = True
                reason = f"important_files ({', '.join(important_changed[:3])}...)"
                
        # Trigger 3: Significant increase in changes
        if changed_files >= last_count + 5:
            should_commit = True
            reason = f"change_acceleration ({last_count} -> {changed_files})"
            
        # Perform commit if triggered
        if should_commit:
            logger.info(f"Auto-commit triggered: {reason}")
            
            # Run the auto-commit script
            script_path = Path.home() / 'claude-automations' / 'scripts' / 'auto_commit.sh'
            if script_path.exists():
                result = subprocess.run(
                    [str(script_path), os.getcwd()],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    logger.success(f"Auto-commit completed: {reason}")
                    # Update state
                    state['last_commit_time'] = datetime.now().isoformat()
                    state['last_file_count'] = 0
                else:
                    logger.warning(f"Auto-commit failed: {result.stderr}")
            else:
                logger.warning("Auto-commit script not found")
        else:
            logger.info(f"No auto-commit needed ({changed_files} files)")
            
        # Update state
        state['last_file_count'] = changed_files
        state['last_check_time'] = datetime.now().isoformat()
        
        # Save state
        STATE_FILE.parent.mkdir(exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
            
        logger.success("Post-edit check complete")
        return 0
        
    except Exception as e:
        logger.error(e, "Post-edit hook failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())