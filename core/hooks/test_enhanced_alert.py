#!/usr/bin/env python3
"""
Test script for enhanced Claude Code audio alerts
"""

import json
import subprocess
import sys
import os

# Add the hooks directory to path so we can import the alert module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification_alert import get_voice_message, extract_task_summary, get_project_context

def test_scenarios():
    """Test different notification scenarios"""
    
    print("🔊 Testing Enhanced Audio Alert System")
    print("=" * 50)
    
    # Test project context detection
    print(f"📁 Current project: {get_project_context()}")
    print()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Task Completion with File Creation",
            "data": {
                "message": "Task completed successfully. Created user-dashboard.tsx component with authentication features.",
                "hook_event_name": "Notification"
            }
        },
        {
            "name": "Implementation Completion",
            "data": {
                "message": "Implementation finished. Successfully implemented OAuth2 authentication system with JWT tokens.",
                "hook_event_name": "Stop"
            }
        },
        {
            "name": "Bug Fix Completion", 
            "data": {
                "message": "Fixed memory leak issue in React component lifecycle. Updated 3 files.",
                "hook_event_name": "Notification"
            }
        },
        {
            "name": "Configuration Update",
            "data": {
                "message": "Updated environment configuration files with new Railway database URLs and API endpoints.",
                "hook_event_name": "Notification"
            }
        },
        {
            "name": "Waiting for Input",
            "data": {
                "message": "Claude Code is waiting for your input to continue the deployment process.",
                "hook_event_name": "Notification"
            }
        },
        {
            "name": "Error Alert",
            "data": {
                "message": "Error occurred during build process. TypeScript compilation failed with 3 errors.",
                "hook_event_name": "Notification"
            }
        },
        {
            "name": "Simple Completion",
            "data": {
                "message": "Task completed successfully.",
                "hook_event_name": "Stop"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Original: {scenario['data']['message'][:80]}...")
        
        # Test task summary extraction
        summary = extract_task_summary(scenario['data']['message'])
        print(f"   Summary: '{summary}'")
        
        # Test voice message generation
        voice_msg = get_voice_message(scenario['data'])
        print(f"   🔊 Audio: \"{voice_msg}\"")
        
        # Ask if user wants to hear it
        response = input(f"   Play audio alert? (y/n): ").strip().lower()
        if response == 'y':
            # Create test data and pipe to notification script
            test_data = json.dumps(scenario['data'])
            try:
                process = subprocess.Popen(
                    ['python3', '/Users/umasankrudhya/.claude/hooks/notification_alert.py'],
                    stdin=subprocess.PIPE,
                    text=True
                )
                process.communicate(input=test_data)
            except Exception as e:
                print(f"   ❌ Error playing alert: {e}")
        
        print()

def test_extraction_patterns():
    """Test the task summary extraction patterns"""
    print("🧪 Testing Task Summary Extraction")
    print("=" * 40)
    
    test_messages = [
        "Created user authentication system with JWT tokens",
        "Updated package.json with new dependencies for React components",
        "Fixed race condition bug in payment processing service",
        "Implemented real-time chat functionality using WebSockets",
        "Configured production environment with SSL certificates",
        "Analyzed database performance and optimized slow queries",
        "Added error handling to file upload component",
        "Successfully deployed application to production servers",
    ]
    
    for msg in test_messages:
        summary = extract_task_summary(msg)
        print(f"Original: {msg}")
        print(f"Summary:  {summary}")
        print()

if __name__ == "__main__":
    print("Enhanced Claude Code Audio Alert Tester")
    print("=" * 50)
    
    choice = input("Test scenarios (1) or extraction patterns (2)? [1]: ").strip()
    
    if choice == "2":
        test_extraction_patterns()
    else:
        test_scenarios()
    
    print("\n✅ Testing complete!")