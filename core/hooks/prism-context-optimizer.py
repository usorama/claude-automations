#!/usr/bin/env python3
"""
PRISM Context Optimizer Hook - PreToolUse Hook for Claude Code

This hook intercepts Task tool calls and triggers PRISM to provide
optimized context to agents via MCP.

Hook Flow:
1. Intercepts Task tool invocation
2. Extracts agent type and task description
3. Calls PRISM MCP server for optimized context
4. Injects context into agent's environment
5. Allows Task to proceed with optimized context
"""

import json
import sys
import os
from pathlib import Path
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[PRISM Hook] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_hook_input():
    """Read hook input from stdin"""
    try:
        input_data = sys.stdin.read()
        if input_data:
            return json.loads(input_data)
    except Exception as e:
        logger.error(f"Failed to parse hook input: {e}")
    return {}

def extract_task_details(hook_input):
    """Extract agent type and task from Task tool parameters"""
    try:
        # Get tool parameters
        tool_params = hook_input.get('tool_params', {})
        
        # Extract agent type (subagent_type parameter)
        agent_type = tool_params.get('subagent_type', 'general')
        
        # Extract task description (prompt parameter)
        task_description = tool_params.get('prompt', '')
        
        # Extract project path from environment
        project_path = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
        
        return {
            'agent_type': agent_type,
            'task': task_description,
            'project_path': project_path
        }
    except Exception as e:
        logger.error(f"Failed to extract task details: {e}")
        return None

def call_prism_mcp(agent_type, task, project_path):
    """Call PRISM MCP server to get optimized context"""
    try:
        # Use Claude Code's MCP client to call PRISM
        # This assumes PRISM MCP server is configured and running
        
        # Build MCP request
        mcp_request = {
            "tool": "get_optimal_context",
            "parameters": {
                "agent_type": agent_type,
                "task_description": task,
                "project_path": project_path
            }
        }
        
        # Try to call PRISM via Claude's MCP interface
        # For now, we'll write a marker file that PRISM can detect
        prism_request_file = Path.home() / '.claude' / 'prism' / 'pending_request.json'
        prism_request_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(prism_request_file, 'w') as f:
            json.dump({
                'agent_type': agent_type,
                'task': task,
                'project_path': project_path,
                'timestamp': str(Path.ctime(Path()))
            }, f)
        
        logger.info(f"PRISM request created for {agent_type}")
        
        # Check if PRISM has created optimized context
        prism_context_file = Path(project_path) / '.claude' / 'manifests' / 'PRISM_OPTIMIZED_CONTEXT.json'
        
        # Give PRISM a moment to process (in production, this would be async)
        import time
        time.sleep(0.5)
        
        if prism_context_file.exists():
            with open(prism_context_file) as f:
                context = json.load(f)
                logger.info(f"PRISM context loaded: {context.get('size_kb', 0):.1f}KB")
                return context
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to call PRISM: {e}")
        return None

def inject_context(context_data):
    """Inject optimized context for the agent"""
    try:
        if not context_data:
            return
        
        # Create output that adds context to the agent
        output = {
            "continue": True,  # Allow Task to proceed
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": f"""
### PRISM Optimized Context

This context has been optimized specifically for your task by PRISM.
Only relevant manifests are included to improve focus and performance.

Manifests included: {', '.join(context_data.get('manifests_included', []))}
Context size: {context_data.get('size_kb', 0):.1f}KB
Optimization method: {context_data.get('optimization_method', 'unknown')}

---

{context_data.get('context', '')}
"""
            }
        }
        
        print(json.dumps(output))
        logger.info("Context injected successfully")
        
    except Exception as e:
        logger.error(f"Failed to inject context: {e}")
        # Allow continuation even if injection fails
        print(json.dumps({"continue": True}))

def main():
    """Main hook entry point"""
    try:
        # Get hook input
        hook_input = get_hook_input()
        
        # Check if this is a Task tool call
        tool_name = hook_input.get('tool_name', '')
        if tool_name != 'Task':
            # Not a Task call, allow it to proceed normally
            print(json.dumps({"continue": True}))
            return
        
        logger.info("Intercepted Task tool call")
        
        # Extract task details
        task_details = extract_task_details(hook_input)
        if not task_details:
            print(json.dumps({"continue": True}))
            return
        
        logger.info(f"Task: {task_details['agent_type']} - {task_details['task'][:100]}...")
        
        # Check if PRISM is enabled
        prism_enabled = os.environ.get('PRISM_ENABLED', 'true').lower() == 'true'
        if not prism_enabled:
            logger.info("PRISM disabled, using standard context")
            print(json.dumps({"continue": True}))
            return
        
        # Call PRISM for optimized context
        context = call_prism_mcp(
            task_details['agent_type'],
            task_details['task'],
            task_details['project_path']
        )
        
        if context and context.get('success'):
            # Inject optimized context
            inject_context(context)
        else:
            # Fallback to standard context
            logger.info("PRISM unavailable, using standard context")
            print(json.dumps({"continue": True}))
        
    except Exception as e:
        logger.error(f"Hook error: {e}")
        # Always allow continuation to prevent blocking
        print(json.dumps({"continue": True}))
        sys.exit(0)

if __name__ == "__main__":
    main()