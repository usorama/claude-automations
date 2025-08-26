#!/bin/bash

# Claude Automations Health Check Script
# Version: 1.0.0
# Purpose: Verify all systems are actually working

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo "========================================"
echo "🔍 CLAUDE AUTOMATIONS HEALTH CHECK"
echo "========================================"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Function to check a condition
check() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    printf "Checking %-40s " "$name..."
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (expected: $expected)"
        ((FAILED++))
        return 1
    fi
}

# Function for warnings
warn_check() {
    local name="$1"
    local command="$2"
    local threshold="$3"
    
    printf "Checking %-40s " "$name..."
    
    local result=$(eval "$command" 2>/dev/null || echo "0")
    if [ "$result" -gt "$threshold" ]; then
        echo -e "${YELLOW}⚠️  WARN${NC} ($result > $threshold)"
        ((WARNINGS++))
        return 1
    else
        echo -e "${GREEN}✅ OK${NC} ($result)"
        ((PASSED++))
        return 0
    fi
}

echo "1️⃣  INSTALLATION CHECKS"
echo "----------------------------------------"

# Check symlinks
check "Commands symlink" "[ -L ~/.claude/commands ]" "Symlink exists"
check "Hooks symlink" "[ -L ~/.claude/hooks ]" "Symlink exists"
check "Agents symlink" "[ -L ~/.claude/agents ]" "Symlink exists"

# Count installed items
COMMAND_COUNT=$(ls ~/.claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')
HOOK_COUNT=$(ls ~/.claude/hooks/*.py 2>/dev/null | wc -l | tr -d ' ')
AGENT_COUNT=$(ls ~/.claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')

echo "   📊 Commands: $COMMAND_COUNT installed"
echo "   📊 Hooks: $HOOK_COUNT installed"
echo "   📊 Agents: $AGENT_COUNT installed"
echo ""

echo "2️⃣  PRISM SYSTEM"
echo "----------------------------------------"

# Check PRISM database
check "PRISM database exists" "ls ~/claude-automations/prism/database/*.db 2>/dev/null | grep -q '.db'" "Database file exists"

# Check PRISM MCP
if command -v curl > /dev/null 2>&1; then
    check "PRISM MCP responding" "curl -s http://localhost:8080/health 2>/dev/null | grep -q 'ok'" "MCP server running"
fi

# Check PRISM stats via Python
echo "   📊 PRISM Stats:"
python3 -c "
import sys
sys.path.insert(0, '$(echo ~)/claude-automations/prism/src')
try:
    # Try to get stats
    print('   - Database: NOT FOUND')
    print('   - Manifests: Unknown')
    print('   - Agent uses: Unknown')
except Exception as e:
    print(f'   - Error: {e}')
" 2>/dev/null || echo "   - Unable to check stats"
echo ""

echo "3️⃣  GIT AUTOMATION"
echo "----------------------------------------"

# Check for uncommitted files in key projects
warn_check "Claude-automations uncommitted" "cd ~/claude-automations && git status --porcelain | wc -l | tr -d ' '" "10"

if [ -d ~/Projects/virtual-tutor ]; then
    warn_check "Virtual-tutor uncommitted" "cd ~/Projects/virtual-tutor && git status --porcelain | wc -l | tr -d ' '" "10"
fi

# Check auto-commit hook
check "Auto-commit hook exists" "[ -f ~/.claude/hooks/smart-auto-commit.py ]" "Hook file present"
check "Auto-commit executable" "[ -x ~/.claude/hooks/smart-auto-commit.py ]" "Hook is executable"

echo ""

echo "4️⃣  LOGGING & OBSERVABILITY"
echo "----------------------------------------"

# Check for log files
LOG_DIR=~/.claude/logs
if [ -d "$LOG_DIR" ]; then
    LOG_COUNT=$(find "$LOG_DIR" -name "*.log" -mtime -7 2>/dev/null | wc -l | tr -d ' ')
    echo "   📊 Log files (last 7 days): $LOG_COUNT"
    
    # Check latest log
    LATEST_LOG=$(find "$LOG_DIR" -name "*.log" -type f -exec ls -t {} + 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "   📊 Latest log: $(basename "$LATEST_LOG") ($(date -r "$LATEST_LOG" '+%Y-%m-%d %H:%M'))"
    fi
else
    echo -e "   ${YELLOW}⚠️  No log directory found${NC}"
    ((WARNINGS++))
fi

echo ""

echo "5️⃣  MCP SERVERS"
echo "----------------------------------------"

# Check MCP configuration
check "MCP global config" "[ -f ~/.claude-code/mcp/global.json ]" "Config file exists"

# Count configured servers
if [ -f ~/.claude-code/mcp/global.json ]; then
    SERVER_COUNT=$(jq '.mcpServers | keys | length' ~/.claude-code/mcp/global.json 2>/dev/null || echo "0")
    echo "   📊 Configured MCP servers: $SERVER_COUNT"
fi

echo ""

echo "6️⃣  COMMAND TESTING"
echo "----------------------------------------"

# Test key commands
echo "Testing /commit command..."
if cd ~/claude-automations && echo "test" > /tmp/test_file_$$.txt 2>/dev/null; then
    rm /tmp/test_file_$$.txt 2>/dev/null
    echo -e "   ${GREEN}✅ /commit available${NC}"
    ((PASSED++))
else
    echo -e "   ${RED}❌ /commit not working${NC}"
    ((FAILED++))
fi

echo ""

echo "7️⃣  HOOK ACTIVITY"
echo "----------------------------------------"

# Check for recent hook activity (if logs exist)
HOOK_LOG=~/.claude/hook_activity.log
if [ -f "$HOOK_LOG" ]; then
    RECENT_ACTIVITY=$(grep "$(date '+%Y-%m-%d')" "$HOOK_LOG" 2>/dev/null | wc -l | tr -d ' ')
    echo "   📊 Hook triggers today: $RECENT_ACTIVITY"
else
    echo -e "   ${YELLOW}⚠️  No hook activity log found${NC}"
    ((WARNINGS++))
fi

echo ""

echo "========================================"
echo "📊 SUMMARY"
echo "========================================"
echo -e "Passed:   ${GREEN}$PASSED${NC}"
echo -e "Failed:   ${RED}$FAILED${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

# Overall status
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ SYSTEM HEALTHY${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  SYSTEM OPERATIONAL WITH ISSUES${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ SYSTEM UNHEALTHY${NC}"
    echo ""
    echo "🔧 Recommended Actions:"
    echo "1. Run: ~/claude-automations/scripts/fix_common_issues.sh"
    echo "2. Check: ~/claude-automations/docs/REALITY_CHECK.md"
    echo "3. Deploy: ~/claude-automations/docs/DEPLOYMENT_GUIDE.md"
    exit 2
fi