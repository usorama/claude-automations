---
description: PRISM Intelligence Dashboard - View real-time metrics and alerts
---

# PRISM Intelligence Dashboard

View real-time intelligence metrics, failures, and alerts from the PRISM system.

## Usage

```
/prism [command]
```

## Commands

- `status` - Show current metrics and statistics (default)
- `health` - System health check
- `alerts` - View unacknowledged alerts
- `learn` - Show learning patterns
- `live` - Run live dashboard with auto-refresh

## Examples

```bash
# Show current status
/prism

# Check system health
/prism health

# View alerts
/prism alerts

# Run live dashboard
/prism live
```

## Implementation

```bash
#!/bin/bash

# Parse command argument
COMMAND="${1:-status}"

# Python script paths
SIMPLE_DASHBOARD="$HOME/claude-automations/prism/src/simple_dashboard.py"
DASHBOARD_SCRIPT="$HOME/claude-automations/prism/src/dashboard.py"

# Check if PRISM is installed
if [ ! -f "$SIMPLE_DASHBOARD" ] && [ ! -f "$DASHBOARD_SCRIPT" ]; then
    echo "❌ PRISM Dashboard not installed"
    echo "Run: /prism-activate to install PRISM"
    exit 1
fi

# Execute appropriate command
case "$COMMAND" in
    status)
        # Use simple dashboard (always works)
        if [ -f "$SIMPLE_DASHBOARD" ]; then
            python3 "$SIMPLE_DASHBOARD"
        else
            python3 "$DASHBOARD_SCRIPT" status
        fi
        ;;
    health)
        python3 "$HOME/claude-automations/prism/src/health_monitor.py"
        ;;
    alerts)
        # Show only alerts
        python3 -c "
import sqlite3
from pathlib import Path

db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
if db_path.exists():
    with sqlite3.connect(db_path) as conn:
        alerts = conn.execute('''
            SELECT severity, message, timestamp
            FROM alerts
            WHERE acknowledged = 0
            ORDER BY timestamp DESC
        ''').fetchall()
        
        if alerts:
            print('🚨 Active Alerts:')
            for severity, message, timestamp in alerts:
                time_str = timestamp[11:19] if timestamp else 'N/A'
                print(f'  [{time_str}] {severity.upper()}: {message}')
        else:
            print('✅ No active alerts')
else:
    print('PRISM database not initialized')
"
        ;;
    learn)
        # Show learning patterns
        python3 -c "
import sqlite3
from pathlib import Path

db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
if db_path.exists():
    with sqlite3.connect(db_path) as conn:
        # Check if table exists
        tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='learning_patterns'\").fetchall()
        if tables:
            patterns = conn.execute('''
                SELECT pattern_type, confidence, usage_count, success_rate
                FROM learning_patterns
                ORDER BY usage_count DESC
                LIMIT 10
            ''').fetchall()
            if patterns:
                print('🧠 Learning Patterns:')
                for p in patterns:
                    print(f'  {p[0]}: {p[2]} uses, {p[3]*100:.1f}% success, {p[1]:.2f} confidence')
            else:
                print('No learning patterns yet')
        else:
            print('Learning patterns table not created yet')
else:
    print('PRISM database not initialized')
"
        ;;
    live)
        python3 "$DASHBOARD_SCRIPT" live
        ;;
    *)
        echo "Usage: /prism [status|health|alerts|learn|live]"
        exit 1
        ;;
esac
```

$ARGUMENTS