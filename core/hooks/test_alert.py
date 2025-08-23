#!/usr/bin/env python3
"""
Test script for Claude Code notification alerts
"""

import json
import sys
import os

# Add the hooks directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from notification_alert import play_alert_sound, should_notify, get_voice_message

def test_voice_alert():
    """Test the voice alert system"""
    print("Testing Claude Code voice alert system...")
    
    # Test notification data
    test_cases = [
        {
            "message": "Task completed successfully",
            "hook_event_name": "Stop",
            "expected": True
        },
        {
            "message": "Claude is waiting for your input",
            "hook_event_name": "Notification", 
            "expected": True
        },
        {
            "message": "Command blocked for safety",
            "hook_event_name": "Notification",
            "expected": True
        },
        {
            "message": "Processing file...",
            "hook_event_name": "PreToolUse",
            "expected": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['message']}")
        
        should_alert = should_notify(test_case)
        print(f"Should alert: {should_alert} (expected: {test_case['expected']})")
        
        if should_alert:
            voice_msg = get_voice_message(test_case)
            print(f"Voice message: '{voice_msg}'")
            
            # Play the alert
            print("Playing alert...")
            play_alert_sound(voice_msg, "normal")
            
            # Brief pause between tests
            import time
            time.sleep(1)

if __name__ == "__main__":
    test_voice_alert()
    print("\nTest completed. Did you hear the alerts?")