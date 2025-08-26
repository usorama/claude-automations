#!/bin/bash
# PRISM Integration Deployment Script for Virtual-Tutor
# This script integrates PRISM into the virtual-tutor project

set -e  # Exit on any error

echo "🚀 PRISM Integration for Virtual-Tutor"
echo "====================================="

VIRTUAL_TUTOR_ROOT="$HOME/Projects/virtual-tutor"
PRISM_ROOT="$HOME/claude-automations/prism"

# Check if virtual-tutor project exists
if [ ! -d "$VIRTUAL_TUTOR_ROOT" ]; then
    echo "❌ Virtual-tutor project not found at $VIRTUAL_TUTOR_ROOT"
    echo "💡 Please ensure the virtual-tutor project exists at this location"
    exit 1
fi

echo "✅ Found virtual-tutor project at $VIRTUAL_TUTOR_ROOT"

# Check if PRISM exists
if [ ! -d "$PRISM_ROOT" ]; then
    echo "❌ PRISM not found at $PRISM_ROOT"
    echo "💡 Please ensure PRISM is installed in claude-automations"
    exit 1
fi

echo "✅ Found PRISM at $PRISM_ROOT"

# Create hooks directory
echo "📁 Creating hooks directory..."
mkdir -p "$VIRTUAL_TUTOR_ROOT/.claude/hooks"

# Copy PRISM hook
echo "🔗 Installing PRISM optimization hook..."
cp "$PRISM_ROOT/integration/virtual_tutor_prism_hook.py" "$VIRTUAL_TUTOR_ROOT/.claude/hooks/prism_optimize_context.py"
chmod +x "$VIRTUAL_TUTOR_ROOT/.claude/hooks/prism_optimize_context.py"

# Create hook configuration
echo "⚙️ Configuring hooks..."
cat > "$VIRTUAL_TUTOR_ROOT/.claude/hooks.toml" << EOF
# PRISM Context Optimization Hook for Virtual-Tutor
[hooks.pre_agent]
path = ".claude/hooks/prism_optimize_context.py"
description = "PRISM context optimization for virtual-tutor agents"
enabled = true

# Optional: Post-agent learning hook (for future enhancement)
# [hooks.post_agent]
# path = ".claude/hooks/prism_learn_from_usage.py"
# description = "PRISM learning from agent usage patterns"
# enabled = false
EOF

# Test the integration
echo "🧪 Testing PRISM integration..."
cd "$VIRTUAL_TUTOR_ROOT"

# Set test environment variables
export CLAUDE_AGENT_TYPE="frontend-developer"
export CLAUDE_USER_PROMPT="Create a new React component for the course dashboard"

# Run the test
python3 .claude/hooks/prism_optimize_context.py

# Check if optimization file was created
if [ -f "$VIRTUAL_TUTOR_ROOT/.claude/manifests/PRISM_OPTIMIZED_CONTEXT.json" ]; then
    echo "✅ PRISM integration test successful!"
    
    # Show optimization results
    echo ""
    echo "📊 Optimization Results:"
    python3 -c "
import json
with open('.claude/manifests/PRISM_OPTIMIZED_CONTEXT.json') as f:
    data = json.load(f)
print(f'Agent Type: {data[\"agent_type\"]}')
print(f'Manifests: {data[\"manifests_count\"]}/{len([f for f in __import__(\"os\").listdir(\".claude/manifests\") if not f.startswith(\".\")])}')
print(f'Size: {data[\"context_size_kb\"]:.1f}KB (was {data[\"original_size_kb\"]:.1f}KB)')
print(f'Reduction: {data[\"size_reduction_percent\"]:.1f}%')
print(f'Selected: {data[\"manifests_loaded\"][:3]}...')
"
else
    echo "⚠️ Integration test completed but no optimization file found"
    echo "💡 This may be normal if no manifests directory exists yet"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Use agents normally in virtual-tutor development"
echo "2. Monitor PRISM performance with the dashboard:"
echo "   cd $VIRTUAL_TUTOR_ROOT"
echo "   python3 $PRISM_ROOT/src/prism_dashboard.py --static"
echo ""
echo "3. Start PRISM orchestrator for advanced features:"
echo "   python3 $PRISM_ROOT/src/prism_orchestrator.py --start --project-root $VIRTUAL_TUTOR_ROOT --daemon"
echo ""
echo "4. View optimization logs:"
echo "   tail -f $VIRTUAL_TUTOR_ROOT/.claude/prism_usage.log"
echo ""
echo "🎉 PRISM is now integrated with virtual-tutor!"
echo "   Context will be automatically optimized for all agent interactions."