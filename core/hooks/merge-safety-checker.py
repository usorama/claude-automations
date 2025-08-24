#!/usr/bin/env python3
"""
Merge Safety Checker Hook
Ensures merges are safe and creates backups
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add git-intelligence to path
sys.path.insert(0, '/Users/umasankrudhya/claude-automations/git-intelligence/src')

from smart_merge import SmartMergeManager


def detect_merge_in_progress():
    """Check if a merge is in progress"""
    git_dir = Path(".git")
    
    # Check for merge markers
    merge_markers = [
        git_dir / "MERGE_HEAD",
        git_dir / "MERGE_MSG",
        git_dir / "MERGE_MODE"
    ]
    
    return any(marker.exists() for marker in merge_markers)


def get_merge_info():
    """Get information about the pending merge"""
    info = {
        "source": "",
        "target": "",
        "conflicts": False,
        "files_changed": 0
    }
    
    try:
        # Get current branch (target)
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            info["target"] = result.stdout.strip()
        
        # Get merge head (source)
        merge_head_file = Path(".git/MERGE_HEAD")
        if merge_head_file.exists():
            with open(merge_head_file, 'r') as f:
                merge_commit = f.read().strip()
            
            # Get branch name for commit
            result = subprocess.run(
                ["git", "name-rev", "--name-only", merge_commit],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info["source"] = result.stdout.strip()
        
        # Check for conflicts
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            info["conflicts"] = True
            info["conflict_files"] = result.stdout.strip().split('\n')
        
        # Count files changed
        result = subprocess.run(
            ["git", "diff", "--cached", "--numstat"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            info["files_changed"] = len(result.stdout.strip().split('\n'))
            
    except:
        pass
    
    return info


def create_pre_merge_backup():
    """Create a backup before merge"""
    try:
        backup_dir = Path.home() / ".claude" / "smart-genie-merge-backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup ID
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save current state
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            current_commit = result.stdout.strip()
            
            # Save backup info
            backup_info = {
                "id": backup_id,
                "timestamp": datetime.now().isoformat(),
                "commit": current_commit,
                "branch": subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True,
                    text=True
                ).stdout.strip()
            }
            
            backup_file = backup_dir / f"{backup_id}.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            return backup_id
            
    except:
        pass
    
    return None


def suggest_conflict_resolution(conflict_files):
    """Suggest how to resolve conflicts"""
    suggestions = []
    
    for file in conflict_files:
        # Analyze file type
        if file.endswith('.json'):
            suggestions.append(f"  • {file}: Check JSON structure after resolution")
        elif file.endswith(('.py', '.js', '.ts')):
            suggestions.append(f"  • {file}: Verify imports and function signatures")
        elif file.endswith('.md'):
            suggestions.append(f"  • {file}: Documentation conflict - merge both versions?")
        else:
            suggestions.append(f"  • {file}: Review changes carefully")
    
    return suggestions


def main():
    """Main hook execution"""
    try:
        # Check if merge is happening
        if not detect_merge_in_progress():
            return
        
        # Get merge information
        merge_info = get_merge_info()
        
        # Create backup
        backup_id = create_pre_merge_backup()
        
        if backup_id:
            print(f"\n💾 Merge backup created: {backup_id}")
            print(f"   Rollback available with: /merge rollback")
        
        # Check for conflicts
        if merge_info["conflicts"]:
            print(f"\n⚠️ Merge conflicts detected in {len(merge_info.get('conflict_files', []))} files")
            
            # Initialize merge manager for auto-resolution
            manager = SmartMergeManager()
            
            # Check if auto-resolution is enabled
            if manager.config["conflict_resolution"]["auto_resolve_simple"]:
                print("\n🔧 Attempting automatic conflict resolution...")
                
                if manager.auto_resolve_conflicts():
                    print("✅ Conflicts auto-resolved successfully!")
                    print("   Review changes before completing merge")
                else:
                    print("❌ Could not auto-resolve all conflicts")
                    print("\n📝 Conflict resolution suggestions:")
                    
                    suggestions = suggest_conflict_resolution(merge_info.get('conflict_files', []))
                    for suggestion in suggestions[:5]:
                        print(suggestion)
                    
                    print("\n💡 Options:")
                    print("   1. Fix conflicts manually")
                    print("   2. Abort merge: git merge --abort")
                    print("   3. Use /merge resolve for assistance")
            else:
                print("\n💡 Auto-resolution disabled. Fix conflicts manually or:")
                print("   • Enable auto-resolution in config")
                print("   • Use: git merge --abort to cancel")
        else:
            # No conflicts, safe to proceed
            print(f"\n✅ Merge safety check passed")
            print(f"   Merging {merge_info['source']} → {merge_info['target']}")
            print(f"   Files affected: {merge_info['files_changed']}")
        
        # Log the merge
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "merge_safety_check",
            "merge_info": merge_info,
            "backup_id": backup_id,
            "conflicts": merge_info["conflicts"]
        }
        
        # Write to log
        log_file = Path.home() / ".claude" / "smart-genie-merges.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception as e:
        # Silent failure
        if os.environ.get("CLAUDE_DEBUG") == "true":
            print(f"Merge safety checker error: {e}")


if __name__ == "__main__":
    main()