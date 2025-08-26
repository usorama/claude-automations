#!/usr/bin/env python3
"""
PRISM Simple Collector Hook
Collects intelligence every time it's called
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add PRISM to path
sys.path.insert(0, str(Path.home() / 'claude-automations' / 'prism' / 'src'))

try:
    from auto_collector import PRISMCollector
    
    # Initialize collector
    collector = PRISMCollector()
    
    # Generate session ID
    session_id = collector.generate_session_id()
    
    # Capture context
    context = collector.capture_context_state()
    
    # Get current working directory as a hint about the task
    cwd = os.getcwd()
    project_name = Path(cwd).name
    
    # Record a simple collection
    collector.record_usage(
        session_id=session_id,
        agent_type='hook-trigger',
        task=f'Hook triggered in {project_name}',
        context_before=context,
        context_after=context,
        execution_time=10,
        success=True,
        error_message=None
    )
    
    # Silent success - only output on error
    
except Exception as e:
    # Silent fail to not disrupt workflow
    pass