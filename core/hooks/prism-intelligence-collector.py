#!/usr/bin/env python3
"""
PRISM Intelligence Collector Hook
Intercepts agent executions to collect intelligence automatically
This is a pre-agent hook that wraps all agent executions
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add PRISM to path
sys.path.insert(0, str(Path.home() / 'claude-automations' / 'prism' / 'src'))

def main():
    """Main hook entry point"""
    try:
        # Import collector
        from auto_collector import PRISMCollector
        
        # Initialize collector if not already done
        collector = PRISMCollector()
        
        # Read the agent context from environment or arguments
        agent_type = os.environ.get('CLAUDE_AGENT_TYPE', 'unknown')
        task = os.environ.get('CLAUDE_TASK', '')
        
        # Check if we're in an agent execution context
        if 'CLAUDE_AGENT_EXECUTION' in os.environ:
            # We're in an agent execution, collect data
            session_id = collector.generate_session_id()
            start_time = time.time()
            
            # Capture initial context
            context_before = collector.capture_context_state()
            
            # Log the collection
            print(f"[PRISM] Collecting intelligence for {agent_type}", file=sys.stderr)
            
            # Register a cleanup function to record after execution
            import atexit
            
            def cleanup():
                """Record intelligence after agent execution"""
                execution_time = int((time.time() - start_time) * 1000)
                context_after = collector.capture_context_state()
                
                # Determine success (would need to check exit code or result)
                success = True  # Default to success unless we detect failure
                
                # Record the usage
                collector.record_usage(
                    session_id=session_id,
                    agent_type=agent_type,
                    task=task,
                    context_before=context_before,
                    context_after=context_after,
                    execution_time=execution_time,
                    success=success,
                    error_message=None
                )
                
                print(f"[PRISM] Intelligence collected: {execution_time}ms", file=sys.stderr)
            
            atexit.register(cleanup)
        else:
            # Not in agent context, just report status
            stats = collector.get_stats()
            if stats['total'] > 0:
                print(f"[PRISM] Active - {stats['total']} collections, {stats['success_rate']}% success", file=sys.stderr)
    
    except ImportError as e:
        # PRISM not installed, silent fail
        pass
    except Exception as e:
        # Log error but don't interrupt workflow
        print(f"[PRISM] Collection error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()