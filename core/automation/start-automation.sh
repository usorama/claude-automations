#!/bin/bash

# Real-Time Development Automation Startup Script
# Starts all automation services for active development

set -e

echo "🚀 Starting Real-Time Development Automation"
echo "==========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
AUTOMATION_DIR="$HOME/.claude/automation"
PROJECT_PATH="${1:-$(pwd)}"
LOG_DIR="$HOME/.claude/logs"

# Create log directory
mkdir -p "$LOG_DIR"

# Function to check requirements
check_requirements() {
    echo "📋 Checking requirements..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required${NC}"
        exit 1
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git is required${NC}"
        exit 1
    fi
    
    # Check if in git repository
    if [[ ! -d "$PROJECT_PATH/.git" ]]; then
        echo -e "${RED}❌ Not a git repository: $PROJECT_PATH${NC}"
        exit 1
    fi
    
    # Check/install Python dependencies
    echo "📦 Installing Python dependencies..."
    pip3 install -q watchdog pyyaml 2>/dev/null || true
    
    echo -e "${GREEN}✅ All requirements met${NC}"
}

# Function to handle uncommitted changes
handle_uncommitted_changes() {
    cd "$PROJECT_PATH"
    
    # Check for uncommitted changes
    CHANGE_COUNT=$(git status --porcelain | wc -l | tr -d ' ')
    
    if [[ $CHANGE_COUNT -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  Found $CHANGE_COUNT uncommitted changes${NC}"
        echo "Would you like to:"
        echo "  1) Commit all changes now"
        echo "  2) Review changes first"
        echo "  3) Continue without committing"
        echo ""
        read -p "Choice (1/2/3): " choice
        
        case $choice in
            1)
                echo "📝 Creating checkpoint commit..."
                git add -A
                TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
                git commit -m "checkpoint: $CHANGE_COUNT changes - $TIMESTAMP" --no-verify
                echo -e "${GREEN}✅ Changes committed${NC}"
                ;;
            2)
                echo "📋 Current changes:"
                git status --short | head -20
                echo ""
                read -p "Commit these changes? (y/n): " confirm
                if [[ $confirm == "y" ]]; then
                    git add -A
                    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
                    git commit -m "checkpoint: $CHANGE_COUNT changes - $TIMESTAMP" --no-verify
                    echo -e "${GREEN}✅ Changes committed${NC}"
                fi
                ;;
            3)
                echo "⏭️  Continuing without commit..."
                ;;
        esac
    else
        echo -e "${GREEN}✅ Working directory clean${NC}"
    fi
}

# Function to start real-time automation
start_real_time_automation() {
    echo ""
    echo "🔄 Starting real-time automation..."
    
    # Kill any existing automation
    pkill -f "real-time-system.py" 2>/dev/null || true
    
    # Start the automation system in background
    nohup python3 "$AUTOMATION_DIR/real-time-system.py" "$PROJECT_PATH" \
        > "$LOG_DIR/automation.log" 2>&1 &
    
    AUTOMATION_PID=$!
    echo "Started automation with PID: $AUTOMATION_PID"
    
    # Save PID for later
    echo $AUTOMATION_PID > "$AUTOMATION_DIR/automation.pid"
    
    echo -e "${GREEN}✅ Real-time automation running${NC}"
}

# Function to update manifests
update_manifests() {
    echo ""
    echo "📊 Updating manifests..."
    
    cd "$PROJECT_PATH"
    python3 "$AUTOMATION_DIR/smart-manifest-update.py" \
        --incremental \
        --preserve-manual \
        --path "$PROJECT_PATH"
    
    echo -e "${GREEN}✅ Manifests updated${NC}"
}

# Function to show status
show_status() {
    echo ""
    echo "📈 Automation Status"
    echo "==================="
    echo "📍 Project: $PROJECT_PATH"
    echo "🔄 Real-time monitoring: Active"
    echo "📊 Manifest updates: On file changes"
    echo "⏰ Auto-commits: Every 30 minutes"
    echo "📦 Batch commits: Every 50 changes"
    echo "🚀 Auto-PR: After 10 commits"
    echo ""
    echo "📝 Logs: $LOG_DIR/automation.log"
    echo "🛑 To stop: $AUTOMATION_DIR/stop-automation.sh"
}

# Main execution
main() {
    echo "Project: $PROJECT_PATH"
    echo ""
    
    # Check requirements
    check_requirements
    
    # Handle uncommitted changes
    handle_uncommitted_changes
    
    # Update manifests
    update_manifests
    
    # Start real-time automation
    start_real_time_automation
    
    # Show status
    show_status
    
    echo ""
    echo "✨ Automation system is running!"
    echo "You can now work normally - all changes will be tracked."
    echo ""
    echo "Commands:"
    echo "  tail -f $LOG_DIR/automation.log  # View logs"
    echo "  $AUTOMATION_DIR/stop-automation.sh     # Stop automation"
    echo "  $AUTOMATION_DIR/status.sh              # Check status"
}

# Run main function
main