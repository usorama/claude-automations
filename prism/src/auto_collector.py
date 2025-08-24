#!/usr/bin/env python3
"""
PRISM Auto-Collector
Automatically collects intelligence from EVERY agent execution
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import functools
import time
import hashlib
import subprocess
import sys

class PRISMCollector:
    """Automatically collects intelligence from EVERY agent execution"""
    
    def __init__(self):
        self.db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        self.collection_active = True
        
    def init_database(self):
        """Initialize SQLite database with schema"""
        schema_path = Path.home() / 'claude-automations' / 'prism' / 'database' / 'schema.sql'
        
        # Create database and execute schema
        with sqlite3.connect(self.db_path) as conn:
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
            else:
                # Fallback: create minimal schema if file not found
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS context_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        session_id TEXT NOT NULL,
                        agent_type TEXT NOT NULL,
                        task_description TEXT,
                        task_type TEXT,
                        manifests_loaded TEXT,
                        manifests_used TEXT,
                        context_size_kb REAL,
                        execution_time_ms INTEGER,
                        success BOOLEAN,
                        error_message TEXT
                    );
                    
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        severity TEXT,
                        component TEXT NOT NULL,
                        message TEXT NOT NULL,
                        details TEXT,
                        acknowledged BOOLEAN DEFAULT FALSE,
                        acknowledged_at DATETIME,
                        resolution TEXT
                    );
                """)
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        unique_str = f"{timestamp}-{time.time()}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:8]
    
    def intercept_agent(self, agent_func):
        """Decorator that automatically collects intelligence from any agent"""
        @functools.wraps(agent_func)
        def wrapper(*args, **kwargs):
            if not self.collection_active:
                return agent_func(*args, **kwargs)
            
            # Pre-execution collection
            session_id = self.generate_session_id()
            start_time = time.time()
            agent_type = kwargs.get('agent_type', kwargs.get('subagent_type', 'unknown'))
            task = kwargs.get('task', kwargs.get('prompt', ''))
            
            # Capture context loading
            context_before = self.capture_context_state()
            
            try:
                # Execute agent
                result = agent_func(*args, **kwargs)
                success = True
                error_message = None
                
            except Exception as e:
                result = None
                success = False
                error_message = str(e)
                
                # Create alert for failure
                self.create_alert('error', f'Agent {agent_type} failed', {
                    'error': str(e),
                    'task': task[:200] if task else 'No task description'
                })
            
            finally:
                # Post-execution collection
                execution_time = int((time.time() - start_time) * 1000)
                context_after = self.capture_context_state()
                
                # Store intelligence
                self.record_usage(
                    session_id=session_id,
                    agent_type=agent_type,
                    task=task,
                    context_before=context_before,
                    context_after=context_after,
                    execution_time=execution_time,
                    success=success,
                    error_message=error_message
                )
                
                # Learn from this execution
                self.update_learning_patterns(agent_type, task, success, execution_time)
                
            return result
        
        return wrapper
    
    def capture_context_state(self) -> Dict:
        """Capture current context state"""
        manifest_dir = Path.home() / '.claude' / 'manifests'
        loaded_manifests = []
        total_size = 0
        
        if manifest_dir.exists():
            for manifest_file in manifest_dir.glob('*.json'):
                size = manifest_file.stat().st_size / 1024  # KB
                loaded_manifests.append(manifest_file.stem)
                total_size += size
        
        # Also check for any active context files
        context_files = []
        context_dir = Path.home() / '.claude' / 'context'
        if context_dir.exists():
            for ctx_file in context_dir.glob('*'):
                if ctx_file.is_file():
                    context_files.append(ctx_file.name)
        
        return {
            'manifests': loaded_manifests,
            'context_files': context_files,
            'total_size_kb': round(total_size, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def record_usage(self, **kwargs):
        """Record context usage to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Extract task type from task description
                task = kwargs.get('task', '')
                task_type = self.classify_task(task)
                
                conn.execute("""
                    INSERT INTO context_usage 
                    (session_id, agent_type, task_description, task_type, manifests_loaded, 
                     manifests_used, context_size_kb, execution_time_ms, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    kwargs['session_id'],
                    kwargs['agent_type'],
                    task[:500] if task else None,  # Truncate long tasks
                    task_type,
                    json.dumps(kwargs['context_before'].get('manifests', [])),
                    json.dumps(kwargs['context_after'].get('manifests', [])),
                    kwargs['context_before'].get('total_size_kb', 0),
                    kwargs['execution_time'],
                    kwargs['success'],
                    kwargs['error_message']
                ))
        except Exception as e:
            print(f"[PRISM] Error recording usage: {e}", file=sys.stderr)
    
    def classify_task(self, task_description: str) -> str:
        """Classify task type from description"""
        if not task_description:
            return 'unknown'
        
        task_lower = task_description.lower()
        
        # Task type classification
        if any(word in task_lower for word in ['test', 'spec', 'jest', 'pytest', 'unit']):
            return 'testing'
        elif any(word in task_lower for word in ['review', 'analyze', 'check', 'audit']):
            return 'review'
        elif any(word in task_lower for word in ['fix', 'bug', 'error', 'issue']):
            return 'bugfix'
        elif any(word in task_lower for word in ['create', 'build', 'implement', 'add']):
            return 'feature'
        elif any(word in task_lower for word in ['refactor', 'optimize', 'improve']):
            return 'refactor'
        elif any(word in task_lower for word in ['document', 'readme', 'docs']):
            return 'documentation'
        elif any(word in task_lower for word in ['deploy', 'release', 'publish']):
            return 'deployment'
        else:
            return 'general'
    
    def update_learning_patterns(self, agent_type: str, task: str, success: bool, execution_time: int):
        """Update learning patterns based on execution"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if this agent has learning patterns table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS learning_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        confidence REAL DEFAULT 0.5,
                        usage_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0.0
                    )
                """)
                
                # Update agent performance pattern
                pattern_type = f"agent_performance_{agent_type}"
                
                # Check if pattern exists
                existing = conn.execute("""
                    SELECT id, usage_count, success_rate
                    FROM learning_patterns
                    WHERE pattern_type = ?
                """, (pattern_type,)).fetchone()
                
                if existing:
                    # Update existing pattern
                    pattern_id, usage_count, old_success_rate = existing
                    new_success_rate = ((old_success_rate * usage_count) + (1 if success else 0)) / (usage_count + 1)
                    
                    conn.execute("""
                        UPDATE learning_patterns
                        SET usage_count = usage_count + 1,
                            success_rate = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (new_success_rate, pattern_id))
                else:
                    # Create new pattern
                    pattern_data = {
                        'agent_type': agent_type,
                        'avg_execution_time': execution_time,
                        'task_types': [self.classify_task(task)]
                    }
                    
                    conn.execute("""
                        INSERT INTO learning_patterns (pattern_type, pattern_data, usage_count, success_rate)
                        VALUES (?, ?, 1, ?)
                    """, (pattern_type, json.dumps(pattern_data), 1.0 if success else 0.0))
                    
        except Exception as e:
            print(f"[PRISM] Error updating learning patterns: {e}", file=sys.stderr)
    
    def create_alert(self, severity: str, message: str, details: Dict):
        """Create an alert for observable issues"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO alerts (severity, component, message, details)
                    VALUES (?, ?, ?, ?)
                """, (severity, 'prism', message, json.dumps(details)))
            
            # Also trigger notification if critical
            if severity in ['error', 'critical']:
                self.notify_user(severity, message)
        except Exception as e:
            print(f"[PRISM] Error creating alert: {e}", file=sys.stderr)
    
    def notify_user(self, severity: str, message: str):
        """Send notification to user (audio + terminal)"""
        # Terminal notification
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"🚨 PRISM {severity.upper()}: {message}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        
        # Audio alert (macOS specific)
        if sys.platform == 'darwin':
            try:
                subprocess.run(
                    ['say', f"PRISM Alert: {message}"], 
                    capture_output=True, 
                    timeout=5
                )
            except:
                pass  # Silent fail on audio
    
    def get_stats(self) -> Dict:
        """Get current collection statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get basic stats
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total_collections,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                        AVG(execution_time_ms) as avg_time,
                        AVG(context_size_kb) as avg_context
                    FROM context_usage
                    WHERE timestamp > datetime('now', '-24 hours')
                """).fetchone()
                
                if stats:
                    return {
                        'total': stats[0] or 0,
                        'successful': stats[1] or 0,
                        'avg_time_ms': round(stats[2] or 0, 2),
                        'avg_context_kb': round(stats[3] or 0, 2),
                        'success_rate': round((stats[1] or 0) / (stats[0] or 1) * 100, 1)
                    }
        except:
            pass
        
        return {
            'total': 0,
            'successful': 0,
            'avg_time_ms': 0,
            'avg_context_kb': 0,
            'success_rate': 0
        }

# Create global instance
collector = PRISMCollector()

if __name__ == "__main__":
    # Test the collector
    print("[PRISM] Auto-Collector initialized")
    stats = collector.get_stats()
    print(f"[PRISM] Current stats: {stats}")