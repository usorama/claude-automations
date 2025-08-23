#!/usr/bin/env python3
"""
Global switch processor for Claude Code text replacement switches.
This hook processes text replacement switches like -u, -r, -o, -t, -p from settings.json.
"""

import json
import os
import sys
from pathlib import Path

def process_global_switches():
    """Process global text replacement switches with built-in configuration."""
    
    # Built-in switch configuration (since textReplacementSwitches isn't valid in settings.json)
    switches = {
        "-u": "Think deeply and thoroughly about this problem. Consider multiple perspectives, edge cases, and implications. Take time to analyze all aspects before responding.",
        "-r": "Research this topic thoroughly using all available resources. Provide comprehensive, well-sourced information with deep analysis.",
        "-o": "Optimize this solution for maximum performance, efficiency, and adherence to best practices. Consider scalability and maintainability.",
        "-t": "Think through this step-by-step with careful reasoning and logical analysis. Break down complex problems into manageable parts.",
        "-p": "Create a detailed, actionable plan with clear steps, milestones, dependencies, and success criteria. Include risk assessment and contingencies."
    }
    
    try:
        
        # Get user prompt from environment variable
        user_prompt = os.environ.get("CLAUDE_USER_PROMPT", "")
        
        # Process switches in the prompt
        for switch, replacement in switches.items():
            if switch in user_prompt:
                # Replace the switch with the expanded text
                expanded_prompt = user_prompt.replace(switch, replacement)
                print(f"[Switch Processor] Expanded '{switch}' to '{replacement}'")
                # Set the expanded prompt back to environment
                os.environ["CLAUDE_USER_PROMPT"] = expanded_prompt
                
    except Exception as e:
        print(f"[Switch Processor] Error: {e}")

if __name__ == "__main__":
    process_global_switches()