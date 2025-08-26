#!/bin/bash
# Wrapper script to run PRISM MCP server with correct environment

# Add PRISM modules to path
export PYTHONPATH="/Users/umasankrudhya/claude-automations/prism/src:/Users/umasankrudhya/claude-automations/git-intelligence/src:/opt/homebrew/lib/python3.12/site-packages:/Users/umasankrudhya/Library/Python/3.12/lib/python/site-packages"

# Run the MCP server using system Python
exec /opt/homebrew/opt/python@3.12/bin/python3.12 /Users/umasankrudhya/claude-automations/prism/src/prism_mcp_server_correct.py "$@"