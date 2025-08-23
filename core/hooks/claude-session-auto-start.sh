#!/bin/bash

# Claude Code Session Auto-Start
# Automatically starts session management when Claude Code begins work

CLAUDE_DIR="$HOME/.claude"
SESSION_MANAGER="$CLAUDE_DIR/hooks/session-lifecycle-manager.py"
LOCK_FILE="$CLAUDE_DIR/.session-lock"

start_session_management() {
    local project_path="$1"
    
    # Check if session already running
    if [ -f "$LOCK_FILE" ]; then
        local existing_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if kill -0 "$existing_pid" 2>/dev/null; then
            echo "✅ Session management already running (PID: $existing_pid)"
            return 0
        else
            # Clean up stale lock file
            rm -f "$LOCK_FILE"
        fi
    fi
    
    # Auto-detect project if not specified
    if [ -z "$project_path" ]; then
        # Check current directory for project indicators
        if [ -f "package.json" ] || [ -f "pyproject.toml" ] || [ -f "Cargo.toml" ] || [ -d ".git" ]; then
            project_path="$(pwd)"
        else
            # Look for git root
            project_path="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
        fi
    fi
    
    echo "🚀 Auto-starting Claude Code session management"
    echo "📁 Project: $project_path"
    
    # Start session manager in background
    nohup python3 "$SESSION_MANAGER" start "$project_path" > "$CLAUDE_DIR/session.log" 2>&1 &
    local session_pid=$!
    
    # Save PID for cleanup
    echo "$session_pid" > "$LOCK_FILE"
    
    echo "✅ Session management started (PID: $session_pid)"
    echo "📝 Log: $CLAUDE_DIR/session.log"
    echo "🛑 Stop with: python3 $SESSION_MANAGER stop"
    
    return 0
}

stop_session_management() {
    if [ -f "$LOCK_FILE" ]; then
        local session_pid=$(cat "$LOCK_FILE")
        
        if kill -0 "$session_pid" 2>/dev/null; then
            echo "🛑 Stopping session management (PID: $session_pid)"
            python3 "$SESSION_MANAGER" stop
            kill "$session_pid" 2>/dev/null
            rm -f "$LOCK_FILE"
            echo "✅ Session management stopped"
        else
            echo "⚠️ Session management not running"
            rm -f "$LOCK_FILE"
        fi
    else
        echo "❌ No active session found"
    fi
}

check_session_status() {
    if [ -f "$LOCK_FILE" ]; then
        local session_pid=$(cat "$LOCK_FILE")
        
        if kill -0 "$session_pid" 2>/dev/null; then
            echo "✅ Session management active (PID: $session_pid)"
            python3 "$SESSION_MANAGER" status
        else
            echo "❌ Session management not running (stale lock file)"
            rm -f "$LOCK_FILE"
        fi
    else
        echo "❌ No active session"
    fi
}

# Auto-detect and start if in a project directory
auto_start_if_needed() {
    # Only auto-start if we're in what looks like a project
    if [ -f "package.json" ] || [ -f "pyproject.toml" ] || [ -f "Cargo.toml" ] || [ -f "CLAUDE.md" ]; then
        # Check if session not already running
        if [ ! -f "$LOCK_FILE" ] || ! kill -0 "$(cat "$LOCK_FILE" 2>/dev/null)" 2>/dev/null; then
            echo "🔍 Detected project directory - auto-starting session management"
            start_session_management "$(pwd)"
        fi
    fi
}

# Main command handler
case "${1:-auto}" in
    "start")
        start_session_management "$2"
        ;;
    "stop")
        stop_session_management
        ;;
    "status")
        check_session_status
        ;;
    "restart")
        stop_session_management
        sleep 2
        start_session_management "$2"
        ;;
    "auto")
        auto_start_if_needed
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart|auto} [project_path]"
        echo ""
        echo "Commands:"
        echo "  start [path]   - Start session management for project"
        echo "  stop           - Stop current session management"
        echo "  status         - Show current session status"
        echo "  restart [path] - Restart session management"
        echo "  auto           - Auto-start if in project directory (default)"
        echo ""
        echo "Features:"
        echo "  🔄 Auto-commits every 30 minutes"
        echo "  📝 Smart commits on significant changes"
        echo "  🚀 Auto-PR creation after substantial work"
        echo "  📤 Auto-push for backup"
        exit 1
        ;;
esac