#!/usr/bin/env python3
"""
Test PRISM hooks with simulated Claude Code events
"""

import json
import subprocess
import sys
from pathlib import Path

def test_collector_hook():
    """Test the PostToolUse collector hook"""
    print("Testing PRISM Collector Hook...")
    
    # Simulate a Task tool event
    task_event = {
        "event": "PostToolUse",
        "tool_name": "Task",
        "tool_input": {
            "subagent_type": "bmad-developer",
            "description": "Fix authentication bug",
            "prompt": "The login system is broken, fix it"
        },
        "tool_response": {"success": True},
        "session_id": "test-session-123",
        "transcript_path": "/tmp/transcript.json"
    }
    
    # Run the hook
    hook_path = Path.home() / "claude-automations" / "core" / "hooks" / "prism-collector.py"
    result = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(task_event),
        capture_output=True,
        text=True
    )
    
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("✅ Collector hook succeeded")
    else:
        print(f"❌ Collector hook failed: {result.stderr}")
    
    # Test with Read tool event
    read_event = {
        "event": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {
            "file_path": "/Users/test/project/main.py"
        },
        "session_id": "test-session-123"
    }
    
    result = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(read_event),
        capture_output=True,
        text=True
    )
    
    print(f"Read event exit code: {result.returncode}")
    
    # Test with Grep tool event
    grep_event = {
        "event": "PostToolUse",
        "tool_name": "Grep",
        "tool_input": {
            "pattern": "TODO|FIXME",
            "path": "/Users/test/project"
        },
        "session_id": "test-session-123"
    }
    
    result = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(grep_event),
        capture_output=True,
        text=True
    )
    
    print(f"Grep event exit code: {result.returncode}")

def test_injector_hook():
    """Test the UserPromptSubmit injector hook"""
    print("\nTesting PRISM Injector Hook...")
    
    # Simulate a user prompt event
    prompt_event = {
        "event": "UserPromptSubmit",
        "prompt": "Help me fix the authentication system",
        "session_id": "test-session-123"
    }
    
    # Run the hook
    hook_path = Path.home() / "claude-automations" / "core" / "hooks" / "prism-injector.py"
    result = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(prompt_event),
        capture_output=True,
        text=True
    )
    
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("✅ Injector hook succeeded")
        if result.stdout:
            print(f"Injected context: {result.stdout}")
    else:
        print(f"❌ Injector hook failed: {result.stderr}")

def check_database():
    """Check if data was recorded in database"""
    print("\nChecking PRISM database...")
    
    import sqlite3
    db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
    
    if not db_path.exists():
        print("❌ Database not found")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check agent usage
        cursor.execute("SELECT COUNT(*) FROM agent_usage")
        agent_count = cursor.fetchone()[0]
        print(f"Agent usage records: {agent_count}")
        
        # Check tool usage
        cursor.execute("SELECT COUNT(*) FROM tool_usage")
        tool_count = cursor.fetchone()[0]
        print(f"Tool usage records: {tool_count}")
        
        # Check file patterns
        cursor.execute("SELECT COUNT(*) FROM file_patterns")
        file_count = cursor.fetchone()[0]
        print(f"File pattern records: {file_count}")
        
        # Check search patterns
        cursor.execute("SELECT COUNT(*) FROM search_patterns")
        search_count = cursor.fetchone()[0]
        print(f"Search pattern records: {search_count}")
        
        # Show recent agent usage
        cursor.execute("""
            SELECT agent_name, timestamp 
            FROM agent_usage 
            ORDER BY timestamp DESC 
            LIMIT 3
        """)
        recent = cursor.fetchall()
        if recent:
            print("\nRecent agent usage:")
            for agent, timestamp in recent:
                print(f"  - {agent} at {timestamp}")

if __name__ == "__main__":
    test_collector_hook()
    test_injector_hook()
    check_database()