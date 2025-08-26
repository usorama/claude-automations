#!/usr/bin/env python3
"""
Centralized logging system for all Claude Code hooks.
Provides observability into what's running, when, and if it fails.
"""

import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Any, Callable, Dict, Optional

# Configuration
LOG_DIR = Path.home() / ".claude" / "logs"
LOG_FILE = LOG_DIR / "hooks.log"
JSON_LOG_FILE = LOG_DIR / "hooks.json"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# Create log directory if it doesn't exist
LOG_DIR.mkdir(parents=True, exist_ok=True)


class HookLogger:
    """Centralized logger for Claude Code hooks."""
    
    def __init__(self, hook_name: str):
        """Initialize logger for a specific hook."""
        self.hook_name = hook_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = None
        
    def log(self, level: str, message: str, **kwargs):
        """Log a message with additional metadata."""
        timestamp = datetime.now().isoformat()
        
        # Human-readable log
        log_entry = f"[{timestamp}] [{level}] [{self.hook_name}] {message}"
        if kwargs:
            log_entry += f" | {json.dumps(kwargs)}"
        
        # Write to text log
        self._write_log(LOG_FILE, log_entry + "\n")
        
        # Structured JSON log
        json_entry = {
            "timestamp": timestamp,
            "level": level,
            "hook": self.hook_name,
            "session_id": self.session_id,
            "message": message,
            **kwargs
        }
        
        # Write to JSON log
        self._write_json_log(json_entry)
        
    def _write_log(self, file_path: Path, content: str):
        """Write to log file with rotation."""
        try:
            # Check file size and rotate if needed
            if file_path.exists() and file_path.stat().st_size > MAX_LOG_SIZE:
                # Rotate log
                backup = file_path.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
                file_path.rename(backup)
                
            # Append to log
            with open(file_path, "a") as f:
                f.write(content)
        except Exception as e:
            # Silent failure - don't break the hook
            pass
            
    def _write_json_log(self, entry: Dict[str, Any]):
        """Write structured JSON log."""
        try:
            # Read existing logs
            logs = []
            if JSON_LOG_FILE.exists():
                try:
                    with open(JSON_LOG_FILE, "r") as f:
                        logs = json.load(f)
                except:
                    logs = []
                    
            # Add new entry
            logs.append(entry)
            
            # Keep only last 1000 entries
            if len(logs) > 1000:
                logs = logs[-1000:]
                
            # Write back
            with open(JSON_LOG_FILE, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            # Silent failure
            pass
            
    def start(self, context: Optional[Dict[str, Any]] = None):
        """Log hook start."""
        self.start_time = datetime.now()
        self.log("INFO", f"Hook started", context=context or {})
        
    def success(self, message: str = "Hook completed successfully", **kwargs):
        """Log successful completion."""
        duration = None
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
        self.log("SUCCESS", message, duration_seconds=duration, **kwargs)
        
    def error(self, error: Exception, message: str = "Hook failed"):
        """Log error with traceback."""
        duration = None
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            
        self.log(
            "ERROR",
            message,
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=traceback.format_exc(),
            duration_seconds=duration
        )
        
    def warning(self, message: str, **kwargs):
        """Log warning."""
        self.log("WARNING", message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log info."""
        self.log("INFO", message, **kwargs)


def logged_hook(hook_name: Optional[str] = None):
    """Decorator to add logging to any hook function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name if hook_name not provided
            name = hook_name or func.__name__
            logger = HookLogger(name)
            
            try:
                # Log start with context
                context = {
                    "args": str(args)[:200],  # Truncate long args
                    "kwargs": str(kwargs)[:200],
                    "cwd": os.getcwd(),
                    "env_vars": {
                        k: v for k, v in os.environ.items()
                        if "CLAUDE" in k or "HOOK" in k
                    }
                }
                logger.start(context)
                
                # Execute hook
                result = func(*args, **kwargs)
                
                # Log success
                logger.success()
                return result
                
            except Exception as e:
                # Log error
                logger.error(e)
                # Re-raise to maintain hook behavior
                raise
                
        return wrapper
    return decorator


def get_recent_logs(hours: int = 24, hook_filter: Optional[str] = None) -> list:
    """Get recent log entries."""
    try:
        if not JSON_LOG_FILE.exists():
            return []
            
        with open(JSON_LOG_FILE, "r") as f:
            logs = json.load(f)
            
        # Filter by time
        cutoff = datetime.now().timestamp() - (hours * 3600)
        recent = []
        
        for log in logs:
            try:
                log_time = datetime.fromisoformat(log["timestamp"]).timestamp()
                if log_time >= cutoff:
                    if not hook_filter or hook_filter in log["hook"]:
                        recent.append(log)
            except:
                continue
                
        return recent
    except:
        return []


def print_summary():
    """Print a summary of recent hook activity."""
    logs = get_recent_logs(24)
    
    if not logs:
        print("No hook activity in the last 24 hours")
        return
        
    # Count by hook and status
    summary = {}
    for log in logs:
        hook = log.get("hook", "unknown")
        level = log.get("level", "INFO")
        
        if hook not in summary:
            summary[hook] = {"SUCCESS": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
        summary[hook][level] = summary[hook].get(level, 0) + 1
        
    # Print summary
    print(f"\n📊 Hook Activity Summary (Last 24 Hours)")
    print("=" * 50)
    
    for hook, counts in summary.items():
        total = sum(counts.values())
        success_rate = (counts["SUCCESS"] / total * 100) if total > 0 else 0
        
        print(f"\n{hook}:")
        print(f"  Total runs: {total}")
        print(f"  Success: {counts['SUCCESS']} ({success_rate:.1f}%)")
        if counts["ERROR"]:
            print(f"  ❌ Errors: {counts['ERROR']}")
        if counts["WARNING"]:
            print(f"  ⚠️  Warnings: {counts['WARNING']}")
            
    # Recent errors
    errors = [l for l in logs if l.get("level") == "ERROR"]
    if errors:
        print(f"\n\n❌ Recent Errors:")
        print("-" * 50)
        for error in errors[-5:]:  # Last 5 errors
            print(f"  [{error['timestamp']}] {error['hook']}: {error.get('error_message', 'Unknown error')}")


if __name__ == "__main__":
    # If run directly, show summary
    print_summary()