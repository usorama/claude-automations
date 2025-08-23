#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def update_project_intelligence():
    """Gather and update project intelligence after each session."""
    
    claude_dir = Path(".claude")
    analytics_dir = claude_dir / "analytics"
    analytics_dir.mkdir(exist_ok=True)
    
    # Track session metrics
    session_file = analytics_dir / "sessions.json"
    sessions = {}
    if session_file.exists():
        with open(session_file) as f:
            sessions = json.load(f)
    
    session_id = datetime.now().isoformat()
    sessions[session_id] = {
        "timestamp": session_id,
        "files_modified": len(list(claude_dir.glob("logs/changes.log"))),
        "commands_run": len(list(claude_dir.glob("logs/command-history.log"))),
    }
    
    with open(session_file, 'w') as f:
        json.dump(sessions, f, indent=2)
    
    print(f"[Intelligence] Session {session_id} recorded")

if __name__ == "__main__":
    update_project_intelligence()
