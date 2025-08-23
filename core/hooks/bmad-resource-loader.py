#!/usr/bin/env python3
"""
BMAD Resource Loader Hook
Automatically loads BMAD-METHOD resources for BMAD agents
"""

import os
import json
import sys
from pathlib import Path

# BMAD agent identifiers
BMAD_AGENTS = [
    'bmad-analyst', 'bmad-architect', 'bmad-developer', 'bmad-master',
    'bmad-orchestrator', 'bmad-product-owner', 'bmad-project-manager',
    'bmad-qa', 'bmad-scrum-master', 'bmad-ux-expert', 'completion-enforcer'
]

def is_bmad_agent_active():
    """Check if a BMAD agent is being used"""
    # Check environment variables or context
    agent_name = os.environ.get('CLAUDE_AGENT_NAME', '')
    task_description = os.environ.get('CLAUDE_TASK_DESCRIPTION', '')
    
    # Check if any BMAD agent is mentioned
    for agent in BMAD_AGENTS:
        if agent in agent_name.lower() or agent in task_description.lower():
            return True
    
    # Check for BMAD-related keywords
    bmad_keywords = ['bmad', 'story', 'epic', 'brownfield', 'gaal', 'dod']
    combined_context = f"{agent_name} {task_description}".lower()
    
    return any(keyword in combined_context for keyword in bmad_keywords)

def inject_bmad_context():
    """Inject BMAD resource paths into the context"""
    bmad_core_path = Path.home() / '.claude' / '.bmad-core'
    
    if not bmad_core_path.exists():
        return None
    
    context = {
        'bmad_resources': {
            'tasks': str(bmad_core_path / 'tasks'),
            'templates': str(bmad_core_path / 'templates'),
            'workflows': str(bmad_core_path / 'workflows'),
            'checklists': str(bmad_core_path / 'checklists'),
            'data': str(bmad_core_path / 'data'),
            'docs': str(bmad_core_path / 'docs')
        },
        'bmad_instructions': """
You have access to comprehensive BMAD-METHOD resources at:
- Tasks: ~/.claude/.bmad-core/tasks/
- Templates: ~/.claude/.bmad-core/templates/
- Workflows: ~/.claude/.bmad-core/workflows/
- Checklists: ~/.claude/.bmad-core/checklists/

Use these resources to ensure adherence to BMAD Method best practices.
Reference specific templates and checklists when creating artifacts.
Follow the workflows for complex multi-phase operations.
        """
    }
    
    return context

def main():
    """Main hook execution"""
    try:
        if is_bmad_agent_active():
            context = inject_bmad_context()
            if context:
                # Output context for agent to use
                print(json.dumps(context, indent=2))
                
                # Log for debugging
                debug_log = Path.home() / '.claude' / 'logs' / 'bmad-resource-loader.log'
                debug_log.parent.mkdir(parents=True, exist_ok=True)
                
                with open(debug_log, 'a') as f:
                    f.write(f"BMAD resources loaded at {os.environ.get('CLAUDE_TIMESTAMP', 'unknown')}\n")
    
    except Exception as e:
        # Silent failure to not disrupt Claude
        error_log = Path.home() / '.claude' / 'logs' / 'bmad-resource-loader-error.log'
        error_log.parent.mkdir(parents=True, exist_ok=True)
        
        with open(error_log, 'a') as f:
            f.write(f"Error: {str(e)}\n")

if __name__ == "__main__":
    main()