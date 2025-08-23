#!/usr/bin/env python3
"""
Update all global agents with Critical Constraints section
Ensures all agents know to read manifests before implementation
"""

import os
import sys
from pathlib import Path
import re

def add_constraints_to_agent(agent_file):
    """Add Critical Constraints section to an agent file"""
    
    # Read the agent file
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check if constraints already exist
    if 'Critical Constraints' in content or 'MUST read these manifests' in content:
        print(f"  ✓ Already has constraints: {agent_file.name}")
        return False
    
    # Find the end of the YAML frontmatter
    frontmatter_end = content.find('---', 3)  # Find second ---
    if frontmatter_end == -1:
        print(f"  ⚠️  No valid frontmatter found: {agent_file.name}")
        return False
    
    # Critical Constraints section to add
    constraints_section = """

## Critical Constraints

Before starting any work, you MUST read and understand these manifests:

**Required Context Files:**
- `@.claude/manifests/CODEBASE_MANIFEST.yaml` - Overall codebase structure and organization
- `@.claude/manifests/FUNCTION_REGISTRY.md` - All available functions and their purposes  
- `@.claude/manifests/EXPORT_REGISTRY.json` - Module exports and public interfaces
- `@.claude/manifests/CODE_PATTERNS.md` - Established patterns and conventions
- `@.claude/manifests/DEPENDENCY_GRAPH.json` - Module relationships and dependencies
- `@.claude/manifests/ERROR_HANDLING.md` - Error handling patterns and practices
- `@.claude/manifests/PROJECT_CONTEXT.yaml` - Project-specific configuration
- `@.claude/manifests/TYPE_DEFINITIONS.ts` - TypeScript type definitions

**Why This Matters:**
1. **Prevents Silent Failures** - Understanding existing error handling prevents bugs
2. **Maintains Consistency** - Following patterns keeps code maintainable
3. **Avoids Duplication** - Knowing existing functions prevents recreating them
4. **Enables Smart Decisions** - Understanding structure helps make better choices

**Before Implementation:**
1. Load manifests: `python3 ~/.claude/hooks/pre-agent-context.py`
2. Check branch: `.claude/hooks/suggest-branch.sh`
3. Create checkpoint after work: `python3 ~/.claude/hooks/auto-checkpoint-hook.py --now`

**Validation Requirements:**
- Follow patterns from CODE_PATTERNS.md
- Use utilities from FUNCTION_REGISTRY.md
- Maintain types from TYPE_DEFINITIONS.ts
- Never create empty catch blocks
- Always handle errors appropriately
"""
    
    # Insert after frontmatter but before main content
    insertion_point = frontmatter_end + 3  # After the closing ---
    
    # Find where the main agent description starts (usually after a blank line)
    main_content_start = content.find('\n\n', insertion_point)
    if main_content_start == -1:
        main_content_start = insertion_point
    
    # Insert the constraints section
    new_content = (
        content[:main_content_start] + 
        constraints_section + 
        content[main_content_start:]
    )
    
    # Write back the updated content
    with open(agent_file, 'w') as f:
        f.write(new_content)
    
    print(f"  ✅ Added constraints to: {agent_file.name}")
    return True

def process_agents_directory(agents_dir):
    """Process all agent files in directory and subdirectories"""
    
    updated_count = 0
    total_count = 0
    
    # Find all .md files in agents directory
    for agent_file in agents_dir.rglob('*.md'):
        # Skip README files and other non-agent files
        if 'README' in agent_file.name or 'CRITICAL_CONSTRAINTS' in agent_file.name:
            continue
        
        total_count += 1
        if add_constraints_to_agent(agent_file):
            updated_count += 1
    
    return updated_count, total_count

def main():
    """Main function to update all agents"""
    
    print("🔧 Updating Global Agents with Critical Constraints")
    print("=" * 50)
    
    # Global agents directory
    agents_dir = Path.home() / '.claude' / 'agents'
    
    if not agents_dir.exists():
        print("❌ Global agents directory not found!")
        return 1
    
    print(f"📁 Processing agents in: {agents_dir}")
    print()
    
    # Process all agents
    updated, total = process_agents_directory(agents_dir)
    
    print()
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   Total agents found: {total}")
    print(f"   Agents updated: {updated}")
    print(f"   Already had constraints: {total - updated}")
    
    if updated > 0:
        print()
        print("✅ Successfully updated agents with Critical Constraints!")
        print()
        print("These agents will now:")
        print("  • Read manifests before implementation")
        print("  • Follow established patterns")
        print("  • Prevent silent failures")
        print("  • Maintain code consistency")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())