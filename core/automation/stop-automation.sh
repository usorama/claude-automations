#!/bin/bash

# Stop automation services

echo "🛑 Stopping automation services..."

# Read PID if exists
PID_FILE="$HOME/.claude/automation/automation.pid"

if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "✅ Stopped automation process (PID: $PID)"
        rm "$PID_FILE"
    else
        echo "⚠️ Process not running (stale PID file)"
        rm "$PID_FILE"
    fi
else
    # Try to find by process name
    pkill -f "real-time-system.py" 2>/dev/null && echo "✅ Stopped automation process" || echo "ℹ️ No automation process running"
fi

echo "🛑 Automation stopped"