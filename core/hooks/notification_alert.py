#!/usr/bin/env python3
"""
Claude Code Completion Alert System
Provides audible alerts for important Claude Code events
"""

import json
import sys
import os
import subprocess
import platform
import re
from datetime import datetime
from pathlib import Path

def should_notify(data):
    """Determine if this event should trigger an alert"""
    message = data.get("message", "").lower()
    hook_event = data.get("hook_event_name", "")
    
    # Always notify for:
    # 1. Task completion
    # 2. Waiting for input
    # 3. Tool execution blocked
    # 4. Errors
    # 5. Stop events
    if any(phrase in message for phrase in [
        'task complete',
        'session complete', 
        'waiting for input',
        'awaiting input',
        'user input required',
        'ready for next command',
        'finished processing',
        'operation complete',
        'claude code stopped',
        'claude needs attention',
        'completed successfully',
        'finished',
        'done',
        'ready'
    ]):
        return True
    
    # Notification and Stop hook events
    if hook_event in ["Notification", "Stop"]:
        return True
    
    # Block/error events
    if any(word in message for word in ['blocked', 'error', 'failed', 'critical', 'warning']):
        return True
    
    return False

def get_project_context():
    """Get current project folder and context"""
    try:
        cwd = os.getcwd()
        project_folder = Path(cwd).name
        
        # Clean up common folder name patterns
        if project_folder.startswith('.'):
            project_folder = project_folder[1:]
        
        return project_folder
    except:
        return "unknown"

def extract_task_summary(message):
    """Extract key information from Claude's message for audio summary"""
    if not message:
        return ""
    
    # Look for common completion patterns and extract key info
    patterns = [
        # File operations - more specific patterns
        r'created\s+([^.]+?)(?:\s+(?:file|component|function|system)|$)',
        r'updated\s+([^.]+?)(?:\s+(?:file|files|with|to)|$)',
        r'fixed\s+([^.]+?)(?:\s+(?:bug|issue|problem|in)|$)',
        r'implemented\s+([^.]+?)(?:\s+(?:feature|functionality|using|with)|$)',
        r'added\s+([^.]+?)(?:\s+(?:to|for|in)|$)',
        r'configured\s+([^.]+?)(?:\s+(?:with|for|in)|$)',
        r'installed\s+([^.]+?)(?:\s+(?:successfully|with|for)|$)',
        r'optimized\s+([^.]+?)(?:\s+(?:for|performance|queries)|$)',
        r'analyzed\s+([^.]+?)(?:\s+(?:and|performance|data)|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            summary = match.group(1).strip()
            # Clean up and limit to key words
            summary = re.sub(r'\s+', ' ', summary)  # normalize whitespace
            words = summary.split()[:3]  # Take first 3 words for brevity
            result = ' '.join(words)
            return result if len(result) > 2 else ""
    
    # Fallback: look for key action words
    key_actions = ['created', 'updated', 'fixed', 'implemented', 'installed', 'configured', 'optimized', 'analyzed']
    message_lower = message.lower()
    for action in key_actions:
        if action in message_lower:
            return action
    
    return ""

def get_voice_message(data):
    """Generate contextual voice message with project and task info"""
    message = data.get("message", "Claude needs attention")
    hook_event = data.get("hook_event_name", "")
    
    project_folder = get_project_context()
    task_summary = extract_task_summary(message)
    
    # Build contextual message
    base_message = f"Claude Code done in {project_folder}"
    
    # Add task summary if available
    if task_summary:
        base_message += f", {task_summary}"
    
    # Customize for different event types
    message_lower = message.lower()
    
    if "waiting for input" in message_lower or "awaiting input" in message_lower:
        return f"Claude Code waiting for input in {project_folder}"
    elif "blocked" in message_lower:
        return f"Command blocked in {project_folder} for safety"
    elif "error" in message_lower and "handling" not in message_lower:
        return f"Error in {project_folder} project"
    elif any(word in message_lower for word in ['task complete', 'finished', 'done', 'successfully']) or task_summary:
        return base_message
    else:
        # Default alert
        return f"Claude Code alert in {project_folder}"

def play_alert_sound(voice_message, priority="normal"):
    """Play alert using system sound commands"""
    try:
        if platform.system() == "Darwin":  # macOS
            # First play a system sound to get attention
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], capture_output=True, check=False)
            
            # Use different voices for different priorities
            if priority == "high":
                voice = "Victoria"
                rate = "160"
            else:
                voice = "Alex" 
                rate = "180"
            
            # Use say command with voice and rate
            subprocess.run([
                "say", "-v", voice, "-r", rate, voice_message
            ], capture_output=True, check=False)
            
        elif platform.system() == "Linux":
            # Try different Linux TTS options
            if subprocess.run(["which", "pico2wave"], capture_output=True).returncode == 0:
                temp_file = "/tmp/claude_alert.wav"
                subprocess.run(["pico2wave", "-w", temp_file, voice_message], capture_output=True)
                subprocess.run(["aplay", temp_file], capture_output=True)
                try:
                    os.unlink(temp_file)
                except:
                    pass
            elif subprocess.run(["which", "espeak"], capture_output=True).returncode == 0:
                speed = "150" if priority == "high" else "175"
                subprocess.run(["espeak", "-s", speed, voice_message], capture_output=True)
        
    except Exception as e:
        # Fallback to system bell if voice fails
        try:
            print("\a")  # Terminal bell
        except:
            pass

def main():
    """Main entry point for notification hook"""
    try:
        # Read hook input data
        data = json.load(sys.stdin)
        
        # Check if we should alert for this event
        if should_notify(data):
            voice_message = get_voice_message(data)
            
            # Determine priority
            message = data.get("message", "").lower()
            priority = "high" if any(word in message for word in ['blocked', 'error', 'critical']) else "normal"
            
            # Play the alert
            play_alert_sound(voice_message, priority)
        
    except Exception as e:
        # Don't fail the hook on errors, just log if debug mode
        if os.environ.get("CLAUDE_DEBUG"):
            print(f"Notification alert error: {e}", file=sys.stderr)
    
    # Always exit successfully to avoid blocking Claude
    sys.exit(0)

if __name__ == "__main__":
    main()