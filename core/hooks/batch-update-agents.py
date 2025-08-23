#!/usr/bin/env python3
"""
Batch update all agent files to include CRITICAL_CONSTRAINTS.

This script efficiently updates all agent markdown files in the agents directory
to include the silent failure prevention constraints at the top of their instructions.
"""

import os
import re
from pathlib import Path

CRITICAL_CONSTRAINTS = """CRITICAL_CONSTRAINTS:
  - NO mock/fake responses in production paths
  - FAIL FAST when dependencies missing
  - Errors must propagate, not be swallowed
  - Every catch block must re-throw or alert
  - Required services validated at startup

"""

def find_agent_files():
    """Find all agent markdown files."""
    agents_dir = Path.home() / '.claude/agents'
    return list(agents_dir.rglob('*.md'))

def has_constraints(content):
    """Check if file already has CRITICAL_CONSTRAINTS."""
    return 'CRITICAL_CONSTRAINTS:' in content

def find_you_are_line(content):
    """Find the line that starts with 'You are' to insert constraints before it."""
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('You are '):
            return i
    return None

def update_agent_file(file_path):
    """Update a single agent file to include constraints."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_constraints(content):
            print(f"✅ {file_path.name} - Already has constraints")
            return True
        
        you_are_line = find_you_are_line(content)
        if you_are_line is None:
            print(f"⚠️  {file_path.name} - Could not find 'You are' line")
            return False
        
        lines = content.split('\n')
        lines.insert(you_are_line, CRITICAL_CONSTRAINTS.rstrip())
        
        new_content = '\n'.join(lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {file_path.name} - Updated with constraints")
        return True
        
    except Exception as e:
        print(f"❌ {file_path.name} - Error: {e}")
        return False

def main():
    """Main function to update all agent files."""
    print("🔄 Batch updating agent files with CRITICAL_CONSTRAINTS...")
    print("=" * 60)
    
    agent_files = find_agent_files()
    print(f"Found {len(agent_files)} agent files")
    print()
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for file_path in sorted(agent_files):
        relative_path = file_path.relative_to(Path.home() / '.claude/agents')
        
        if update_agent_file(file_path):
            success_count += 1
        else:
            error_count += 1
    
    print()
    print("=" * 60)
    print("📊 BATCH UPDATE SUMMARY")
    print(f"✅ Successfully updated: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📝 Total files processed: {len(agent_files)}")
    print()
    
    if error_count == 0:
        print("🎉 All agent files successfully updated with CRITICAL_CONSTRAINTS!")
    else:
        print("⚠️  Some files had issues. Review the output above for details.")

if __name__ == '__main__':
    main()