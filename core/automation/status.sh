#!/bin/bash

# Check automation status

echo "📊 Automation Status Check"
echo "========================="

# Check if automation is running
PID_FILE="$HOME/.claude/automation/automation.pid"

if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "✅ Automation running (PID: $PID)"
        
        # Show process details
        ps -fp $PID | tail -1
        
        # Check log file
        LOG_FILE="$HOME/.claude/logs/automation.log"
        if [[ -f "$LOG_FILE" ]]; then
            echo ""
            echo "📝 Recent activity:"
            tail -5 "$LOG_FILE"
        fi
    else
        echo "❌ Automation not running (stale PID file)"
    fi
else
    echo "❌ Automation not running"
fi

# Check last checkpoint
STATE_FILE="$HOME/.claude/automation/state.json"
if [[ -f "$STATE_FILE" ]]; then
    echo ""
    echo "📅 Last checkpoint:"
    cat "$STATE_FILE" | python3 -m json.tool | grep -E "(last_checkpoint|change_count)"
fi

# Check current git status
echo ""
echo "📊 Current git status:"
CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "  Uncommitted changes: $CHANGES"

# Check manifests
MANIFEST_DIR=".claude/manifests"
if [[ -d "$MANIFEST_DIR" ]]; then
    echo ""
    echo "📚 Manifest status:"
    for manifest in "$MANIFEST_DIR"/*.json; do
        if [[ -f "$manifest" ]]; then
            NAME=$(basename "$manifest")
            MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$manifest" 2>/dev/null || stat -c "%y" "$manifest" 2>/dev/null | cut -d' ' -f1,2)
            echo "  $NAME: $MODIFIED"
        fi
    done
fi