#!/usr/bin/env python3
"""
PRISM Auto-Collector - Simplified for Claude Code Hook Integration
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys

class AutoCollector:
    """Collects intelligence from Claude Code tool usage"""
    
    def __init__(self):
        self.db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        """Initialize all necessary tables"""
        # File patterns table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                file_path TEXT,
                operation TEXT,
                extension TEXT,
                directory TEXT,
                context TEXT,
                session_id TEXT
            )
        ''')
        
        # Agent usage table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                agent_name TEXT,
                context TEXT,
                success BOOLEAN,
                session_id TEXT
            )
        ''')
        
        # Tool usage table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                tool_name TEXT,
                context TEXT,
                success BOOLEAN,
                session_id TEXT
            )
        ''')
        
        # Search patterns table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                query TEXT,
                tool TEXT,
                context TEXT,
                session_id TEXT
            )
        ''')
        
        # Command patterns table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                command TEXT,
                context TEXT,
                session_id TEXT
            )
        ''')
        
        self.conn.commit()
    
    def record_file_pattern(self, file_path: str, operation: str, context: dict = None):
        """Record file access patterns"""
        try:
            path = Path(file_path)
            extension = path.suffix
            directory = str(path.parent)
            
            self.cursor.execute('''
                INSERT INTO file_patterns (timestamp, file_path, operation, extension, directory, context, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                file_path,
                operation,
                extension,
                directory,
                json.dumps(context or {}),
                context.get('session_id', 'unknown') if context else 'unknown'
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self._log_error(f"Failed to record file pattern: {e}")
    
    def record_agent_usage(self, agent_name: str, context: dict = None, success: bool = True):
        """Record agent usage for pattern learning"""
        try:
            self.cursor.execute('''
                INSERT INTO agent_usage (timestamp, agent_name, context, success, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                agent_name,
                json.dumps(context or {}),
                success,
                context.get('session_id', 'unknown') if context else 'unknown'
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self._log_error(f"Failed to record agent usage: {e}")
    
    def record_tool_usage(self, tool_name: str, context: dict = None, success: bool = True):
        """Record tool usage for pattern learning"""
        try:
            self.cursor.execute('''
                INSERT INTO tool_usage (timestamp, tool_name, context, success, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                tool_name,
                json.dumps(context or {}),
                success,
                context.get('session_id', 'unknown') if context else 'unknown'
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self._log_error(f"Failed to record tool usage: {e}")
    
    def record_search_pattern(self, query: str, tool: str, context: dict = None):
        """Record search patterns for learning"""
        try:
            self.cursor.execute('''
                INSERT INTO search_patterns (timestamp, query, tool, context, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                query,
                tool,
                json.dumps(context or {}),
                context.get('session_id', 'unknown') if context else 'unknown'
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self._log_error(f"Failed to record search pattern: {e}")
    
    def record_command_pattern(self, command: str, context: dict = None):
        """Record command patterns for learning"""
        try:
            # Extract base command for pattern analysis
            base_command = command.split()[0] if command else ''
            
            self.cursor.execute('''
                INSERT INTO command_patterns (timestamp, command, context, session_id)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                base_command,  # Store base command for pattern analysis
                json.dumps({**context, 'full_command': command} if context else {'full_command': command}),
                context.get('session_id', 'unknown') if context else 'unknown'
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self._log_error(f"Failed to record command pattern: {e}")
    
    def get_agent_recommendations(self, task_description: str) -> list:
        """Get agent recommendations based on patterns"""
        try:
            # Analyze past successful agent usage
            self.cursor.execute('''
                SELECT agent_name, COUNT(*) as usage_count
                FROM agent_usage
                WHERE success = 1
                GROUP BY agent_name
                ORDER BY usage_count DESC
                LIMIT 5
            ''')
            
            recommendations = []
            for row in self.cursor.fetchall():
                recommendations.append({
                    'agent': row[0],
                    'confidence': min(row[1] / 10.0, 1.0)  # Simple confidence score
                })
            
            return recommendations
            
        except Exception as e:
            self._log_error(f"Failed to get recommendations: {e}")
            return []
    
    def get_file_patterns(self, directory: str = None) -> dict:
        """Get file access patterns for a directory"""
        try:
            if directory:
                self.cursor.execute('''
                    SELECT file_path, operation, COUNT(*) as count
                    FROM file_patterns
                    WHERE directory = ?
                    GROUP BY file_path, operation
                    ORDER BY count DESC
                    LIMIT 10
                ''', (directory,))
            else:
                self.cursor.execute('''
                    SELECT file_path, operation, COUNT(*) as count
                    FROM file_patterns
                    GROUP BY file_path, operation
                    ORDER BY count DESC
                    LIMIT 10
                ''')
            
            patterns = {}
            for row in self.cursor.fetchall():
                if row[0] not in patterns:
                    patterns[row[0]] = {}
                patterns[row[0]][row[1]] = row[2]
            
            return patterns
            
        except Exception as e:
            self._log_error(f"Failed to get file patterns: {e}")
            return {}
    
    def _log_error(self, message: str):
        """Log error to file"""
        error_log = Path.home() / 'claude-automations' / 'prism' / 'logs' / 'collector_errors.log'
        error_log.parent.mkdir(parents=True, exist_ok=True)
        with open(error_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    # Test the collector
    collector = AutoCollector()
    print("[PRISM] Auto-Collector initialized")
    
    # Test recording
    collector.record_agent_usage('test-agent', {'task': 'testing'})
    collector.record_file_pattern('/test/file.py', 'read', {'test': True})
    
    # Get recommendations
    recs = collector.get_agent_recommendations("test task")
    print(f"[PRISM] Recommendations: {recs}")
    
    # Get patterns
    patterns = collector.get_file_patterns()
    print(f"[PRISM] File patterns: {patterns}")