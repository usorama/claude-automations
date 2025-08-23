#!/bin/bash

# Claude Code Init Command Wrapper
# Provides 'claude init' functionality with smart project detection

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if --help is requested
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    node "$SCRIPT_DIR/init-project.js" --help
    exit 0
fi

# Run the project initializer
echo "═══════════════════════════════════════════════════════════"
echo "         🚀 Claude Code Intelligent Project Init"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Execute with all passed arguments
node "$SCRIPT_DIR/init-project.js" "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "        ✨ Ready to build something amazing!"
    echo "═══════════════════════════════════════════════════════════"
else
    echo ""
    echo "❌ Initialization encountered an issue."
    echo "Run 'claude init --help' for usage information."
fi