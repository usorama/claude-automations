#!/bin/bash

# Smart Commit & PR using existing MCP and agents
# Uses Claude Code's GitHub MCP and agents for intelligent operations

echo "🤖 Smart Commit & PR System"
echo "=========================="

PROJECT_DIR="${1:-$(pwd)}"
cd "$PROJECT_DIR"

# Function to trigger github-expert agent for smart commits
smart_commit() {
    echo "📝 Using github-expert agent for intelligent commit..."
    
    # Create checkpoint using existing hook
    python3 ~/.claude/hooks/auto-checkpoint-hook.py --now
    
    # The hook already creates semantic commits!
}

# Function to create PR using MCP
create_pr_via_mcp() {
    echo "🚀 Creating PR via GitHub MCP..."
    
    # Use Claude Code to trigger the GitHub MCP
    # This leverages the already configured github server
    cat > /tmp/pr-request.md << 'EOF'
Use the GitHub MCP server to:
1. Push current branch to origin
2. Create a pull request with:
   - Title: "Feature: [analyze commits and summarize]"
   - Body: List the key changes from recent commits
   - Base: main
EOF
    
    # This would be triggered through Claude Code
    echo "Request saved to /tmp/pr-request.md"
    echo "Use this with Claude Code to create PR via MCP"
}

# Function to use agent for complex operations
use_github_agent() {
    echo "🎯 Triggering github-expert agent..."
    
    # Create task for the agent
    cat > /tmp/github-task.md << 'EOF'
Task for github-expert agent:

1. Analyze uncommitted changes
2. Create logical commit groups
3. Generate semantic commit messages
4. Push to appropriate branch
5. Create PR with comprehensive description

Project: $(pwd)
Changes: $(git status --porcelain | wc -l) files
EOF
    
    echo "Task created at /tmp/github-task.md"
    echo "Trigger with: /Task github-expert < /tmp/github-task.md"
}

# Main logic
main() {
    CHANGES=$(git status --porcelain | wc -l | tr -d ' ')
    
    if [[ $CHANGES -eq 0 ]]; then
        echo "✅ No changes to commit"
        exit 0
    fi
    
    echo "📊 Found $CHANGES changes"
    echo ""
    echo "Options:"
    echo "1) Smart commit (uses existing checkpoint hook)"
    echo "2) Create PR via GitHub MCP"
    echo "3) Use github-expert agent (full automation)"
    echo "4) Traditional git commands"
    echo ""
    read -p "Choice (1/2/3/4): " choice
    
    case $choice in
        1)
            smart_commit
            ;;
        2)
            create_pr_via_mcp
            ;;
        3)
            use_github_agent
            ;;
        4)
            echo "Manual mode - use git commands directly"
            ;;
    esac
}

main