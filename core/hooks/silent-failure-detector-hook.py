#!/usr/bin/env python3
"""
Silent Failure Detection Hook

This hook automatically triggers silent failure detection on code operations
that could introduce silent failures into the codebase.

Integrates with the Claude Code hooks system to provide automatic quality gates.
"""

import sys
import os
import subprocess
import json
import re
from pathlib import Path

def should_run_detection(tool_name, args):
    """
    Determine if silent failure detection should run based on the tool and operation.
    
    Args:
        tool_name: The name of the tool being used (Write, Edit, MultiEdit)
        args: Arguments passed to the tool
    
    Returns:
        bool: True if detection should run
    """
    # Always run on these tools when they modify production code
    trigger_tools = ['Write', 'Edit', 'MultiEdit']
    
    if tool_name not in trigger_tools:
        return False
    
    # Extract file path from args
    file_path = None
    if isinstance(args, dict) and 'file_path' in args:
        file_path = args['file_path']
    elif isinstance(args, list) and len(args) > 0:
        file_path = args[0]
    
    if not file_path:
        return False
    
    # Skip test files and configuration files
    skip_patterns = [
        r'.*\.test\.',
        r'.*\.spec\.',
        r'.*/test/',
        r'.*/tests/',
        r'.*/__tests__/',
        r'.*/mock',
        r'.*/fixture',
        r'.*\.config\.',
        r'.*\.md$',
        r'.*\.json$',
        r'.*\.yaml$',
        r'.*\.yml$'
    ]
    
    for pattern in skip_patterns:
        if re.match(pattern, file_path, re.IGNORECASE):
            return False
    
    # Run detection on production code files
    production_patterns = [
        r'.*\.ts$',
        r'.*\.tsx$',
        r'.*\.js$',
        r'.*\.jsx$',
        r'.*\.py$'
    ]
    
    for pattern in production_patterns:
        if re.match(pattern, file_path, re.IGNORECASE):
            return True
    
    return False

def run_silent_failure_detection(target_dir=None):
    """
    Run the silent failure detector script.
    
    Args:
        target_dir: Directory to scan, defaults to current working directory
    
    Returns:
        tuple: (success: bool, critical_count: int, report: dict)
    """
    if not target_dir:
        target_dir = os.getcwd()
    
    detector_script = Path.home() / '.claude/process-templates-n-prompts/silent-failures/silent-failure-detector.ts'
    
    if not detector_script.exists():
        print(f"⚠️  Silent failure detector script not found at {detector_script}")
        return True, 0, {}
    
    try:
        # Run the detector script
        result = subprocess.run([
            'npx', 'ts-node', str(detector_script), target_dir
        ], capture_output=True, text=True, cwd=target_dir)
        
        # Check for generated report
        report_path = Path(target_dir) / 'silent-failures-report.json'
        if report_path.exists():
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            critical_count = report.get('summary', {}).get('critical', 0)
            high_count = report.get('summary', {}).get('high', 0)
            
            if critical_count > 0:
                print(f"🚨 CRITICAL: {critical_count} critical silent failures detected!")
                print("❌ Code changes blocked until issues are resolved.")
                return False, critical_count, report
            elif high_count > 0:
                print(f"⚠️  WARNING: {high_count} high-priority silent failure patterns detected.")
                print("✅ Changes allowed, but please review these issues.")
                return True, 0, report
            else:
                print("✅ Silent failure detection passed")
                return True, 0, report
        else:
            # No report generated, assume success
            return True, 0, {}
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running silent failure detection: {e}")
        # In case of detection errors, allow the operation to continue
        # but log the issue for investigation
        return True, 0, {}
    except Exception as e:
        print(f"❌ Unexpected error in silent failure detection: {e}")
        return True, 0, {}

def handle_pre_tool_use(tool_name, args):
    """
    Handle PreToolUse hook for Write, Edit, and MultiEdit operations.
    
    Args:
        tool_name: Name of the tool being used
        args: Arguments passed to the tool
    
    Returns:
        bool: True to allow operation, False to block
    """
    if not should_run_detection(tool_name, args):
        return True
    
    print(f"🔍 Running silent failure detection before {tool_name}...")
    
    success, critical_count, report = run_silent_failure_detection()
    
    if not success:
        print("\n" + "="*60)
        print("🚨 SILENT FAILURE DETECTION BLOCKED OPERATION")
        print("="*60)
        print(f"Critical issues found: {critical_count}")
        print("\nFix these issues before proceeding:")
        
        if report and 'issues' in report:
            critical_issues = [issue for issue in report['issues'] if issue['severity'] == 'critical']
            for i, issue in enumerate(critical_issues[:5], 1):  # Show first 5
                print(f"{i}. {issue['file']}:{issue['line']} - {issue['message']}")
            if len(critical_issues) > 5:
                print(f"... and {len(critical_issues) - 5} more")
        
        print("\nRun '/silent-check' to see detailed report.")
        print("="*60)
        return False
    
    return True

def handle_pre_commit():
    """
    Handle pre-commit hook to scan staged files.
    
    Returns:
        bool: True to allow commit, False to block
    """
    print("🔍 Running silent failure detection on staged files...")
    
    try:
        # Get staged files
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️  Could not get staged files, skipping silent failure check")
            return True
        
        staged_files = result.stdout.strip().split('\n')
        if not staged_files or staged_files == ['']:
            print("✅ No staged files to check")
            return True
        
        # Filter for relevant files
        relevant_files = []
        for file_path in staged_files:
            if should_run_detection('Write', {'file_path': file_path}):
                relevant_files.append(file_path)
        
        if not relevant_files:
            print("✅ No production code files in staged changes")
            return True
        
        success, critical_count, report = run_silent_failure_detection()
        
        if not success:
            print("\n" + "="*60)
            print("🚨 COMMIT BLOCKED BY SILENT FAILURE DETECTION")
            print("="*60)
            print(f"Critical issues found: {critical_count}")
            print("\nFix these issues before committing:")
            print("Run '/silent-check' for detailed report")
            print("="*60)
            return False
        
        return True
    
    except Exception as e:
        print(f"⚠️  Error in pre-commit silent failure check: {e}")
        return True  # Allow commit if check fails

def handle_pre_deploy():
    """
    Handle pre-deploy hook for production readiness check.
    
    Returns:
        bool: True to allow deploy, False to block
    """
    print("🔍 Running production readiness silent failure check...")
    
    success, critical_count, report = run_silent_failure_detection()
    
    if not success:
        print("\n" + "="*60)
        print("🚨 DEPLOYMENT BLOCKED BY SILENT FAILURE DETECTION")
        print("="*60)
        print("❌ CRITICAL: Production deployment cannot proceed")
        print(f"Critical silent failures detected: {critical_count}")
        print("\nThis deployment would introduce silent failures that:")
        print("- Hide real errors from users and developers")
        print("- Create 'zombie' application states")
        print("- Make debugging and monitoring impossible")
        print("\nFix ALL critical issues before deploying to production.")
        print("Run '/silent-check' for detailed analysis.")
        print("="*60)
        return False
    
    # Check for high priority issues as warnings
    if report and report.get('summary', {}).get('high', 0) > 0:
        high_count = report['summary']['high']
        print(f"\n⚠️  WARNING: {high_count} high-priority silent failure patterns detected")
        print("Consider fixing these before production deployment.")
    
    print("✅ Silent failure production readiness check passed")
    return True

def main():
    """
    Main entry point for the hook script.
    
    Expected arguments:
    - hook_type: 'pre_tool_use', 'pre_commit', or 'pre_deploy'
    - tool_name: (for pre_tool_use only) name of the tool
    - args: (for pre_tool_use only) JSON string of tool arguments
    """
    if len(sys.argv) < 2:
        print("❌ Usage: silent-failure-detector-hook.py <hook_type> [tool_name] [args]")
        sys.exit(1)
    
    hook_type = sys.argv[1]
    
    if hook_type == 'pre_tool_use':
        if len(sys.argv) < 4:
            print("❌ Usage: silent-failure-detector-hook.py pre_tool_use <tool_name> <args_json>")
            sys.exit(1)
        
        tool_name = sys.argv[2]
        try:
            args = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            args = sys.argv[3]  # Fallback to string
        
        success = handle_pre_tool_use(tool_name, args)
        sys.exit(0 if success else 1)
    
    elif hook_type == 'pre_commit':
        success = handle_pre_commit()
        sys.exit(0 if success else 1)
    
    elif hook_type == 'pre_deploy':
        success = handle_pre_deploy()
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ Unknown hook type: {hook_type}")
        sys.exit(1)

if __name__ == '__main__':
    main()