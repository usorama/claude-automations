#!/bin/bash
# Start Intelligent Git Watcher with Ollama
# This replaces the dumb 30-minute cron job with real intelligence

set -e

# Configuration
WATCHER_SCRIPT="$HOME/claude-automations/git-intelligence/src/intelligent_watcher.py"
PID_FILE="$HOME/.claude/intelligent-watcher.pid"
LOG_FILE="$HOME/.claude/logs/intelligent-watcher.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Functions
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        print_warning "Intelligent watcher already running (PID: $OLD_PID)"
        echo "Use '$0 stop' to stop it first"
        exit 1
    fi
fi

# Parse command
COMMAND="${1:-start}"
PROJECT_PATH="${2:-$(pwd)}"

case "$COMMAND" in
    start)
        echo "🤖 Starting Intelligent Git Watcher"
        echo "================================"
        
        # Check Ollama
        if ! command -v ollama &> /dev/null; then
            print_error "Ollama not found. Please install Ollama first."
            exit 1
        fi
        print_status "Ollama found"
        
        # Check for models
        MODEL_COUNT=$(ollama list | tail -n +2 | wc -l)
        if [ "$MODEL_COUNT" -eq 0 ]; then
            print_error "No Ollama models installed"
            echo "  Install a fast model with: ollama pull qwen2.5:3b"
            exit 1
        fi
        print_status "Ollama models available: $MODEL_COUNT"
        
        # Check Python
        if ! command -v python3 &> /dev/null; then
            print_error "Python3 not found"
            exit 1
        fi
        print_status "Python3 found"
        
        # Check git repo
        if [ ! -d "$PROJECT_PATH/.git" ]; then
            print_error "$PROJECT_PATH is not a git repository"
            exit 1
        fi
        print_status "Git repository: $PROJECT_PATH"
        
        # Create log directory
        mkdir -p "$(dirname "$LOG_FILE")"
        
        # Start watcher in background
        echo ""
        echo "Starting watcher..."
        nohup python3 "$WATCHER_SCRIPT" "$PROJECT_PATH" >> "$LOG_FILE" 2>&1 &
        WATCHER_PID=$!
        
        # Save PID
        echo "$WATCHER_PID" > "$PID_FILE"
        
        # Wait a moment to check if it started
        sleep 2
        
        if ps -p "$WATCHER_PID" > /dev/null; then
            print_status "Watcher started successfully (PID: $WATCHER_PID)"
            echo ""
            echo "📊 Status:"
            echo "  Project: $PROJECT_PATH"
            echo "  PID: $WATCHER_PID"
            echo "  Log: $LOG_FILE"
            echo ""
            echo "🎯 Intelligent Triggers:"
            echo "  • 5+ files changed"
            echo "  • 2+ test files modified"
            echo "  • 300+ lines changed"
            echo "  • Critical files updated"
            echo "  • AI pattern detection"
            echo "  • 30 minutes maximum"
            echo ""
            echo "📝 Commands:"
            echo "  View logs: tail -f $LOG_FILE"
            echo "  Stop: $0 stop"
            echo "  Status: $0 status"
        else
            print_error "Failed to start watcher"
            rm -f "$PID_FILE"
            exit 1
        fi
        ;;
        
    stop)
        if [ ! -f "$PID_FILE" ]; then
            print_warning "Watcher not running (no PID file)"
            exit 0
        fi
        
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            rm -f "$PID_FILE"
            print_status "Watcher stopped (PID: $PID)"
        else
            print_warning "Process not found (PID: $PID)"
            rm -f "$PID_FILE"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                print_status "Watcher is running (PID: $PID)"
                
                # Show recent activity from log
                if [ -f "$LOG_FILE" ]; then
                    echo ""
                    echo "Recent activity:"
                    tail -5 "$LOG_FILE" | sed 's/^/  /'
                fi
            else
                print_warning "Watcher not running (stale PID file)"
                rm -f "$PID_FILE"
            fi
        else
            print_warning "Watcher not running"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 1
        $0 start "$PROJECT_PATH"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|status|restart} [project-path]"
        echo ""
        echo "Examples:"
        echo "  $0 start                    # Start watching current directory"
        echo "  $0 start ~/Projects/myapp   # Start watching specific project"
        echo "  $0 stop                     # Stop the watcher"
        echo "  $0 status                   # Check watcher status"
        exit 1
        ;;
esac