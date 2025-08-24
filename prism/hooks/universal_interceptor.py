#!/usr/bin/env python3
"""
PRISM Universal Interceptor
Makes ALL intelligence collection automatic by intercepting agent executions
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add PRISM to path
sys.path.insert(0, str(Path.home() / 'claude-automations' / 'prism' / 'src'))

try:
    from auto_collector import PRISMCollector
    
    # Initialize collector
    collector = PRISMCollector()
    
    # Get current stats
    stats = collector.get_stats()
    
    # Create status file for monitoring
    status_path = Path.home() / '.claude' / 'prism' / 'status.json'
    status_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(status_path, 'w') as f:
        json.dump({
            'active': True,
            'initialized': datetime.now().isoformat(),
            'stats': stats
        }, f, indent=2)
    
    print("[PRISM] Universal intelligence collection activated", file=sys.stderr)
    print(f"[PRISM] Database: {collector.db_path}", file=sys.stderr)
    print(f"[PRISM] Stats - Total: {stats['total']}, Success Rate: {stats['success_rate']}%", file=sys.stderr)
    
except ImportError as e:
    print(f"[PRISM] Warning: Could not import auto_collector: {e}", file=sys.stderr)
    print("[PRISM] Intelligence collection disabled", file=sys.stderr)
except Exception as e:
    print(f"[PRISM] Error initializing universal interceptor: {e}", file=sys.stderr)