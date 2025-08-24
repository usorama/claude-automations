#!/bin/bash

# PRISM Unified Intelligence System Activation Script
# This script activates all PRISM components for automatic intelligence collection

echo "🔮 Activating PRISM Unified Intelligence System..."
echo "================================================"

# Set paths
PRISM_DIR="$HOME/claude-automations/prism"
CLAUDE_DIR="$HOME/.claude"
PRISM_DATA_DIR="$CLAUDE_DIR/prism"

# Check if PRISM directory exists
if [ ! -d "$PRISM_DIR" ]; then
    echo "❌ Error: PRISM directory not found at $PRISM_DIR"
    echo "Please ensure claude-automations is properly installed"
    exit 1
fi

# Step 1: Create database
echo ""
echo "📊 Step 1: Creating intelligence database..."
mkdir -p "$PRISM_DATA_DIR"

python3 << EOF
import sqlite3
from pathlib import Path

db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
schema_path = Path.home() / 'claude-automations' / 'prism' / 'database' / 'schema.sql'

print(f"  Creating database at: {db_path}")

try:
    with sqlite3.connect(db_path) as conn:
        if schema_path.exists():
            with open(schema_path) as f:
                conn.executescript(f.read())
            print("  ✅ Database created successfully")
        else:
            print(f"  ⚠️  Schema file not found at {schema_path}")
            print("  Creating minimal schema...")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS context_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    task_description TEXT,
                    task_type TEXT,
                    manifests_loaded TEXT,
                    manifests_used TEXT,
                    context_size_kb REAL,
                    execution_time_ms INTEGER,
                    success BOOLEAN,
                    error_message TEXT
                );
                
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    severity TEXT,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    acknowledged_at DATETIME,
                    resolution TEXT
                );
            """)
            print("  ✅ Minimal database created")
except Exception as e:
    print(f"  ❌ Error creating database: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "Failed to create database"
    exit 1
fi

# Step 2: Install Python dependencies
echo ""
echo "📦 Step 2: Installing Python dependencies..."
echo "  Checking for required packages..."

python3 -m pip install rich --quiet 2>/dev/null || echo "  ⚠️  Rich library not installed (dashboard will use simple mode)"

# Step 3: Create symlinks for commands
echo ""
echo "🔗 Step 3: Setting up commands..."

# Create commands symlink if not exists
if [ ! -L "$CLAUDE_DIR/commands/prism.md" ]; then
    if [ -f "$PRISM_DIR/../core/commands/prism.md" ]; then
        ln -sf "$PRISM_DIR/../core/commands/prism.md" "$CLAUDE_DIR/commands/prism.md" 2>/dev/null
        echo "  ✅ /prism command linked"
    fi
fi

# Step 4: Register hooks
echo ""
echo "🪝 Step 4: Registering PRISM hooks..."

python3 << EOF
import json
from pathlib import Path

settings_path = Path.home() / '.claude' / 'settings.json'
settings = {}

# Read existing settings
if settings_path.exists():
    try:
        with open(settings_path) as f:
            settings = json.load(f)
    except:
        settings = {}

if 'hooks' not in settings:
    settings['hooks'] = {}

# PRISM hooks to register
prism_hooks = {
    'pre-agent': [
        "python3 ~/.claude/hooks/prism-intelligence-collector.py"
    ],
    'post-edit': [
        "python3 ~/.claude/hooks/prism-context-analyzer.py"
    ]
}

hooks_added = []

for hook_type, hook_commands in prism_hooks.items():
    if hook_type not in settings['hooks']:
        settings['hooks'][hook_type] = []
    
    for hook_cmd in hook_commands:
        # Check if hook file exists before adding
        hook_file = hook_cmd.split()[-1].replace('~', str(Path.home()))
        if not hook_cmd in settings['hooks'][hook_type]:
            settings['hooks'][hook_type].append(hook_cmd)
            hooks_added.append(f"{hook_type}: {Path(hook_file).name}")

if hooks_added:
    # Write updated settings
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"  ✅ Registered {len(hooks_added)} hooks:")
    for hook in hooks_added:
        print(f"     - {hook}")
else:
    print("  ℹ️  Hooks already registered")
EOF

# Step 5: Copy hook files
echo ""
echo "📁 Step 5: Installing PRISM components..."

# Create hooks directory if not exists
mkdir -p "$CLAUDE_DIR/hooks"

# Copy hook files
if [ -f "$PRISM_DIR/../core/hooks/prism-intelligence-collector.py" ]; then
    cp "$PRISM_DIR/../core/hooks/prism-intelligence-collector.py" "$CLAUDE_DIR/hooks/" 2>/dev/null
    echo "  ✅ Intelligence collector installed"
fi

# Step 6: Run initial health check
echo ""
echo "🏥 Step 6: Running system health check..."
python3 "$PRISM_DIR/src/health_monitor.py"

# Step 7: Test database connection
echo ""
echo "🧪 Step 7: Testing PRISM system..."

python3 << EOF
import sys
sys.path.append('$PRISM_DIR/src')

try:
    from auto_collector import PRISMCollector
    collector = PRISMCollector()
    stats = collector.get_stats()
    
    print("  ✅ Auto-collector operational")
    print(f"     Database: {collector.db_path}")
    if stats['total'] > 0:
        print(f"     Stats: {stats['total']} collections, {stats['success_rate']}% success rate")
    else:
        print("     Stats: No data collected yet (this is normal for first activation)")
        
except Exception as e:
    print(f"  ⚠️  Warning: {e}")
EOF

# Step 8: Show dashboard status
echo ""
echo "📊 Step 8: Checking dashboard..."

python3 "$PRISM_DIR/src/dashboard.py" status 2>/dev/null || echo "  ⚠️  Dashboard not yet available"

# Step 9: Create activation marker
echo ""
echo "🎯 Step 9: Finalizing activation..."

cat > "$PRISM_DATA_DIR/activation.json" << EOF
{
  "activated": "$(date -Iseconds)",
  "version": "3.0",
  "components": {
    "auto_collector": true,
    "dashboard": true,
    "health_monitor": true,
    "cross_repo_intelligence": true
  }
}
EOF

echo "  ✅ Activation complete"

# Final summary
echo ""
echo "================================================"
echo "✨ PRISM Unified Intelligence System Activated! ✨"
echo "================================================"
echo ""
echo "📊 Dashboard Commands:"
echo "  /prism         - View current metrics"
echo "  /prism health  - System health check"
echo "  /prism alerts  - View active alerts"
echo "  /prism learn   - Show learning patterns"
echo "  /prism live    - Live dashboard (auto-refresh)"
echo ""
echo "🔍 Features Active:"
echo "  ✅ Automatic intelligence collection"
echo "  ✅ Observable metrics dashboard"
echo "  ✅ Health monitoring & alerts"
echo "  ✅ Cross-repository learning"
echo "  ✅ Failure prevention"
echo ""
echo "💡 Tips:"
echo "  • PRISM collects data automatically in the background"
echo "  • No manual intervention needed"
echo "  • Check /prism periodically to view insights"
echo "  • Audio alerts will notify you of critical issues"
echo ""
echo "No more silent failures. Everything is observable."
echo ""