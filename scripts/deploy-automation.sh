#!/bin/bash
# Claude Automations Deployment Script
# Quickly deploy auto-commit to any project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CLAUDE_AUTO_HOME="$HOME/claude-automations"
AUTO_COMMIT_SCRIPT="$CLAUDE_AUTO_HOME/scripts/auto_commit.sh"
MONITOR_SCRIPT="$CLAUDE_AUTO_HOME/scripts/monitor.py"
LOG_DIR="$HOME/.claude/logs"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo "================================"
    echo "$1"
    echo "================================"
}

# Check if project path is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <project-path> [options]"
    echo ""
    echo "Options:"
    echo "  --interval MINUTES   Set auto-commit interval (default: 30)"
    echo "  --test              Test the setup without adding to cron"
    echo "  --remove            Remove auto-commit for this project"
    echo ""
    echo "Example:"
    echo "  $0 ~/Projects/my-app"
    echo "  $0 ~/Projects/my-app --interval 60"
    echo "  $0 ~/Projects/my-app --test"
    echo "  $0 ~/Projects/my-app --remove"
    exit 1
fi

PROJECT_PATH="$1"
INTERVAL=30
TEST_MODE=false
REMOVE_MODE=false

# Parse additional arguments
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --test)
            TEST_MODE=true
            shift
            ;;
        --remove)
            REMOVE_MODE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Convert to absolute path
PROJECT_PATH=$(cd "$PROJECT_PATH" 2>/dev/null && pwd) || {
    print_error "Project path does not exist: $1"
    exit 1
}

PROJECT_NAME=$(basename "$PROJECT_PATH")

print_header "Claude Automations Deployment"
echo "Project: $PROJECT_NAME"
echo "Path: $PROJECT_PATH"
echo ""

# Remove mode
if [ "$REMOVE_MODE" = true ]; then
    print_header "Removing Auto-Commit"
    
    # Remove from crontab
    crontab -l 2>/dev/null | grep -v "$PROJECT_PATH" | crontab - || true
    
    print_status "Removed from crontab"
    
    # Show current status
    echo ""
    print_header "Current Cron Jobs"
    crontab -l 2>/dev/null | grep auto_commit || echo "No auto-commit jobs configured"
    
    exit 0
fi

# Check prerequisites
print_header "Checking Prerequisites"

# Check if project is a git repository
if [ ! -d "$PROJECT_PATH/.git" ]; then
    print_error "$PROJECT_NAME is not a git repository"
    echo "  Initialize with: cd $PROJECT_PATH && git init"
    exit 1
fi
print_status "Git repository found"

# Check if auto_commit.sh exists
if [ ! -f "$AUTO_COMMIT_SCRIPT" ]; then
    print_error "Auto-commit script not found at $AUTO_COMMIT_SCRIPT"
    echo "  Please ensure claude-automations is properly installed"
    exit 1
fi
print_status "Auto-commit script found"

# Create log directory if needed
mkdir -p "$LOG_DIR"
print_status "Log directory ready: $LOG_DIR"

# Check current git status
cd "$PROJECT_PATH"
UNCOMMITTED=$(git status --porcelain | wc -l | tr -d ' ')
if [ "$UNCOMMITTED" -gt 0 ]; then
    print_warning "Found $UNCOMMITTED uncommitted files in $PROJECT_NAME"
    echo "  Consider committing them first or they'll be auto-committed soon"
fi

# Test mode
if [ "$TEST_MODE" = true ]; then
    print_header "Testing Auto-Commit (Dry Run)"
    
    echo "Would add to crontab:"
    echo "*/$INTERVAL * * * * $AUTO_COMMIT_SCRIPT $PROJECT_PATH >> $LOG_DIR/cron_auto_commit.log 2>&1"
    echo ""
    
    echo "Testing auto-commit script now..."
    "$AUTO_COMMIT_SCRIPT" "$PROJECT_PATH"
    
    print_status "Test complete - check logs at $LOG_DIR/auto_commit.log"
    exit 0
fi

# Add to crontab
print_header "Configuring Cron Job"

# Check if already exists
if crontab -l 2>/dev/null | grep -q "$PROJECT_PATH"; then
    print_warning "Auto-commit already configured for $PROJECT_NAME"
    echo "  Updating configuration..."
    # Remove old entry
    crontab -l 2>/dev/null | grep -v "$PROJECT_PATH" | crontab - || true
fi

# Add new entry
CRON_LINE="*/$INTERVAL * * * * $AUTO_COMMIT_SCRIPT $PROJECT_PATH >> $LOG_DIR/cron_auto_commit.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

print_status "Added cron job (runs every $INTERVAL minutes)"

# Verify installation
print_header "Verifying Installation"

# Check crontab
if crontab -l | grep -q "$PROJECT_PATH"; then
    print_status "Cron job verified"
else
    print_error "Failed to add cron job"
    exit 1
fi

# Run initial auto-commit
print_header "Running Initial Auto-Commit"
"$AUTO_COMMIT_SCRIPT" "$PROJECT_PATH"
print_status "Initial run complete"

# Show monitoring command
print_header "✨ Setup Complete!"

echo ""
echo "Auto-commit is now active for: $PROJECT_NAME"
echo "Commits will run every $INTERVAL minutes"
echo ""
echo "📊 Monitor with:"
echo "  python3 $MONITOR_SCRIPT"
echo ""
echo "📝 View logs:"
echo "  tail -f $LOG_DIR/auto_commit.log"
echo ""
echo "🔍 Check status:"
echo "  crontab -l | grep $PROJECT_NAME"
echo ""
echo "❌ To remove:"
echo "  $0 $PROJECT_PATH --remove"
echo ""

# Run monitor once to show current status
echo "Current System Status:"
echo "----------------------"
python3 "$MONITOR_SCRIPT" | grep -A 5 "REPOSITORY STATUS" | grep "$PROJECT_NAME" -A 3 || true

print_status "Automation deployed successfully! 🎉"