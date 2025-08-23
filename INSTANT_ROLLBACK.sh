#!/bin/bash

# ================================
# Claude Automations Instant Rollback
# ================================
# One-command rollback to restore original structure
# Usage: bash ~/claude-automations/INSTANT_ROLLBACK.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║           Claude Automations - INSTANT ROLLBACK             ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Function to rollback a directory
rollback_directory() {
    local dir_name=$1
    local backup_pattern="$HOME/.claude/${dir_name}.backup.*"
    
    echo -e "${YELLOW}Rolling back ${dir_name}...${NC}"
    
    # Remove symlink if it exists
    if [ -L "$HOME/.claude/${dir_name}" ]; then
        rm "$HOME/.claude/${dir_name}"
        echo -e "  Removed symlink: ~/.claude/${dir_name}"
    fi
    
    # Find most recent backup
    local latest_backup=$(ls -dt $backup_pattern 2>/dev/null | head -1)
    
    if [ -n "$latest_backup" ]; then
        # Restore from backup
        mv "$latest_backup" "$HOME/.claude/${dir_name}"
        echo -e "${GREEN}  ✅ Restored ${dir_name} from backup${NC}"
    else
        echo -e "${RED}  ⚠️  No backup found for ${dir_name}${NC}"
    fi
}

# Check what's currently symlinked
echo "Checking current state..."
echo

SYMLINKED_DIRS=()

for dir in hooks agents commands scripts knowledge-base process-templates-n-prompts automation templates; do
    if [ -L "$HOME/.claude/$dir" ]; then
        SYMLINKED_DIRS+=($dir)
        echo -e "  📎 $dir is symlinked to $(readlink $HOME/.claude/$dir)"
    fi
done

if [ -L "$HOME/.claude/settings.json" ]; then
    echo -e "  📎 settings.json is symlinked"
fi

if [ ${#SYMLINKED_DIRS[@]} -eq 0 ] && [ ! -L "$HOME/.claude/settings.json" ]; then
    echo -e "${GREEN}Nothing to rollback - no symlinks found${NC}"
    exit 0
fi

echo
echo -e "${YELLOW}This will rollback the following:${NC}"
for dir in "${SYMLINKED_DIRS[@]}"; do
    echo "  • $dir"
done
if [ -L "$HOME/.claude/settings.json" ]; then
    echo "  • settings.json"
fi

echo
read -p "Proceed with rollback? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Rollback cancelled${NC}"
    exit 0
fi

echo
echo "Starting rollback..."
echo

# Rollback each symlinked directory
for dir in "${SYMLINKED_DIRS[@]}"; do
    rollback_directory $dir
done

# Rollback settings.json if symlinked
if [ -L "$HOME/.claude/settings.json" ]; then
    echo -e "${YELLOW}Rolling back settings.json...${NC}"
    rm "$HOME/.claude/settings.json"
    
    # Find backup
    latest_settings_backup=$(ls -t $HOME/.claude/settings.json.backup.* 2>/dev/null | head -1)
    if [ -n "$latest_settings_backup" ]; then
        mv "$latest_settings_backup" "$HOME/.claude/settings.json"
        echo -e "${GREEN}  ✅ Restored settings.json from backup${NC}"
    else
        echo -e "${RED}  ⚠️  No backup found for settings.json${NC}"
    fi
fi

echo
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ROLLBACK COMPLETE!                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo
echo "Your Claude configuration has been restored to its original state."
echo
echo "The claude-automations directory is still intact at:"
echo "  ~/claude-automations"
echo
echo "You can safely delete it if you no longer need it:"
echo "  rm -rf ~/claude-automations"
echo