#!/bin/bash

# Code Intelligence & Silent Failure Prevention Deployment Script
# Deploys Claude Code enhancements to any project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script metadata
SCRIPT_VERSION="1.0.0"
SCRIPT_NAME="Claude Code Intelligence Deployment"

# Directories
CLAUDE_ROOT="$HOME/.claude"
TEMPLATES_DIR="$CLAUDE_ROOT/templates"
SCRIPTS_DIR="$CLAUDE_ROOT/scripts"

print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}║           🧠 ${SCRIPT_NAME}           ║${NC}"
    echo -e "${BLUE}║                     Version ${SCRIPT_VERSION}                       ║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check if we're in Claude Code ecosystem
    if [ ! -d "$CLAUDE_ROOT" ]; then
        print_error "Claude Code not found. Please install Claude Code first."
        exit 1
    fi
    
    # Check for required tools
    local missing_tools=()
    
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi
    
    if ! command -v node &> /dev/null && ! command -v bun &> /dev/null; then
        missing_tools+=("node or bun")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    print_success "All dependencies satisfied"
}

detect_project_path() {
    local project_path=""
    
    # Check if path provided as argument
    if [ $# -eq 1 ]; then
        project_path="$1"
        if [ ! -d "$project_path" ]; then
            print_error "Provided path does not exist: $project_path" >&2
            exit 1
        fi
    else
        # Check if we're in a project directory
        if [ -f "package.json" ] || [ -f "tsconfig.json" ] || [ -f "pyproject.toml" ] || [ -f "Cargo.toml" ]; then
            project_path="$(pwd)"
            print_info "Detected project in current directory: $project_path" >&2
        else
            # Interactive mode
            echo -e "${YELLOW}📁 Enter project path (or press Enter for current directory):${NC}" >&2
            read -r user_path
            
            if [ -z "$user_path" ]; then
                project_path="$(pwd)"
            else
                # Expand tilde
                project_path="${user_path/#\~/$HOME}"
                
                if [ ! -d "$project_path" ]; then
                    print_error "Directory does not exist: $project_path" >&2
                    exit 1
                fi
            fi
        fi
    fi
    
    # Convert to absolute path
    project_path="$(cd "$project_path" && pwd)"
    echo "$project_path"
}

backup_existing() {
    local project_path="$1"
    local claude_dir="$project_path/.claude"
    local github_dir="$project_path/.github"
    
    if [ -d "$claude_dir" ] || [ -d "$github_dir" ]; then
        local backup_dir="$project_path/.claude-backup-$(date +%Y%m%d-%H%M%S)"
        
        print_warning "Existing Claude/GitHub config found. Creating backup..."
        mkdir -p "$backup_dir"
        
        if [ -d "$claude_dir" ]; then
            cp -r "$claude_dir" "$backup_dir/claude-original"
        fi
        
        if [ -d "$github_dir" ]; then
            cp -r "$github_dir" "$backup_dir/github-original"
        fi
        
        print_success "Backup created at: $backup_dir"
    fi
}

detect_project_type() {
    local project_path="$1"
    local project_type="unknown"
    
    cd "$project_path"
    
    if [ -f "package.json" ]; then
        if grep -q "\"react\"" package.json 2>/dev/null; then
            project_type="react"
        elif grep -q "\"next\"" package.json 2>/dev/null; then
            project_type="nextjs"
        elif grep -q "\"vue\"" package.json 2>/dev/null; then
            project_type="vue"
        else
            project_type="nodejs"
        fi
    elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
        project_type="python"
    elif [ -f "Cargo.toml" ]; then
        project_type="rust"
    elif [ -f "go.mod" ]; then
        project_type="go"
    elif [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
        project_type="java"
    fi
    
    echo "$project_type"
}

deploy_github_workflows() {
    local project_path="$1"
    local project_type="$2"
    local workflows_dir="$project_path/.github/workflows"
    
    print_info "Deploying GitHub workflows..."
    mkdir -p "$workflows_dir"
    
    # Copy and customize workflow templates
    for template in "$TEMPLATES_DIR/github-workflows"/*.yml; do
        if [ -f "$template" ]; then
            local workflow_name=$(basename "$template")
            local target_file="$workflows_dir/$workflow_name"
            
            # Copy template
            cp "$template" "$target_file"
            
            # Customize based on project type
            case "$project_type" in
                "nodejs"|"react"|"nextjs"|"vue")
                    # Use bun if available, otherwise npm
                    if command -v bun &> /dev/null; then
                        sed -i '' 's/npm install/bun install/g' "$target_file" 2>/dev/null || \
                        sed -i 's/npm install/bun install/g' "$target_file"
                        sed -i '' 's/npx ts-node/bun run/g' "$target_file" 2>/dev/null || \
                        sed -i 's/npx ts-node/bun run/g' "$target_file"
                    fi
                    ;;
                "python")
                    # Add Python-specific setup
                    sed -i '' 's/Setup Bun/Setup Python/g' "$target_file" 2>/dev/null || \
                    sed -i 's/Setup Bun/Setup Python/g' "$target_file"
                    ;;
            esac
            
            print_success "Deployed workflow: $workflow_name"
        fi
    done
}

deploy_claude_config() {
    local project_path="$1"
    local project_type="$2"
    local claude_dir="$project_path/.claude"
    
    print_info "Setting up Claude configuration..."
    mkdir -p "$claude_dir/manifests"
    
    # Update or create CLAUDE.md
    local claude_md="$project_path/CLAUDE.md"
    local code_intelligence_section="
## Code Intelligence System

All agents MUST read these manifests before implementation:
@.claude/manifests/CODEBASE_MANIFEST.yaml
@.claude/manifests/FUNCTION_REGISTRY.md
@.claude/manifests/EXPORT_REGISTRY.json
@.claude/manifests/CODE_PATTERNS.md

## Silent Failure Prevention
@.claude/process-templates-n-prompts/silent-failures/INTEGRATION_PLAN.md

## Development Commands

**Code Intelligence:**
- \`python3 ~/.claude/hooks/pre-agent-context.py\` - Load manifests before agent work
- \`python3 ~/.claude/hooks/auto-checkpoint-hook.py --now\` - Create checkpoint commit
- \`python3 ~/.claude/hooks/pr-creation-hook.py\` - Create PR when todos complete
"

    if [ -f "$claude_md" ]; then
        # Check if Code Intelligence section already exists
        if ! grep -q "Code Intelligence System" "$claude_md"; then
            echo "$code_intelligence_section" >> "$claude_md"
            print_success "Updated existing CLAUDE.md with Code Intelligence"
        else
            print_warning "CLAUDE.md already contains Code Intelligence section"
        fi
    else
        # Create new CLAUDE.md
        cat > "$claude_md" << EOF
# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.
$code_intelligence_section
EOF
        print_success "Created new CLAUDE.md with Code Intelligence"
    fi
}

generate_initial_manifests() {
    local project_path="$1"
    
    print_info "Generating initial code intelligence manifests..."
    
    cd "$project_path"
    
    # Check which script runner to use
    if command -v bun &> /dev/null && [ -f "package.json" ]; then
        bun "$SCRIPTS_DIR/generate-manifests.ts" || {
            print_warning "Manifest generation failed, but setup continues"
            return 0
        }
    elif command -v npx &> /dev/null && [ -f "package.json" ]; then
        npx ts-node "$SCRIPTS_DIR/generate-manifests.ts" || {
            print_warning "Manifest generation failed, but setup continues"
            return 0
        }
    else
        print_warning "No TypeScript runner found. Manifests will be generated on first agent use"
        return 0
    fi
    
    print_success "Initial manifests generated"
}

deploy_git_branch_intelligence() {
    local project_path="$1"
    
    print_info "Deploying Git Branch Intelligence..."
    
    cd "$project_path"
    
    # Check if this is a git repository
    if [ ! -d ".git" ]; then
        print_warning "Not a Git repository. Skipping Git Branch Intelligence"
        return 0
    fi
    
    # Create local .claude/hooks directory for project-specific hooks
    mkdir -p "$project_path/.claude/hooks"
    
    # Deploy intelligent branch hook integration
    cat > "$project_path/.claude/hooks/branch-intelligence.py" << 'EOF'
#!/usr/bin/env python3
"""Project-specific Git Branch Intelligence Integration"""

import sys
import subprocess
from pathlib import Path

# Use global branch intelligence hook
global_hook = Path.home() / '.claude' / 'hooks' / 'git-branch' / 'intelligent-branch-hook.py'

if global_hook.exists():
    subprocess.run(['python3', str(global_hook)] + sys.argv[1:])
else:
    print("Git Branch Intelligence not installed globally")
    print("Run: ~/.claude/mcp-servers/git-branch-intelligence/install.sh")
EOF
    chmod +x "$project_path/.claude/hooks/branch-intelligence.py"
    
    # Create convenience scripts
    cat > "$project_path/.claude/hooks/suggest-branch.sh" << 'EOF'
#!/bin/bash
python3 "$(dirname "$0")/branch-intelligence.py" suggest
EOF
    chmod +x "$project_path/.claude/hooks/suggest-branch.sh"
    
    cat > "$project_path/.claude/hooks/create-smart-branch.sh" << 'EOF'
#!/bin/bash
python3 "$(dirname "$0")/branch-intelligence.py" create "$@"
EOF
    chmod +x "$project_path/.claude/hooks/create-smart-branch.sh"
    
    cat > "$project_path/.claude/hooks/switch-smart-branch.sh" << 'EOF'
#!/bin/bash
python3 "$(dirname "$0")/branch-intelligence.py" switch "$@"
EOF
    chmod +x "$project_path/.claude/hooks/switch-smart-branch.sh"
    
    # Add MCP server configuration if not present
    local mcp_config="$project_path/.mcp.json"
    if [ ! -f "$mcp_config" ]; then
        cat > "$mcp_config" << EOF
{
  "mcpServers": {
    "git-branch-intelligence": {
      "command": "node",
      "args": ["$HOME/.claude/mcp-servers/git-branch-intelligence/server.js"],
      "env": {
        "GIT_BRANCH_DEBUG": "false",
        "BRANCH_NAMING_STYLE": "semantic",
        "AUTO_BRANCH_CREATION": "true"
      }
    }
  }
}
EOF
        print_success "Created MCP configuration for Git Branch Intelligence"
    else
        # Check if git-branch-intelligence is already configured
        if ! grep -q "git-branch-intelligence" "$mcp_config"; then
            print_warning "MCP config exists. Manually add git-branch-intelligence server if needed"
        fi
    fi
    
    print_success "Git Branch Intelligence deployed"
}

setup_git_hooks() {
    local project_path="$1"
    
    print_info "Setting up Git hooks integration..."
    
    cd "$project_path"
    
    # Check if this is a git repository
    if [ ! -d ".git" ]; then
        print_warning "Not a Git repository. Skipping Git hooks setup"
        return 0
    fi
    
    # Create a simple integration script
    cat > ".claude/integrate-hooks.sh" << 'EOF'
#!/bin/bash
# Integration script for Claude Code hooks

# Pre-commit: Load manifests
python3 ~/.claude/hooks/pre-agent-context.py

# Post-work: Create checkpoint if needed
python3 ~/.claude/hooks/auto-checkpoint-hook.py
EOF
    
    chmod +x ".claude/integrate-hooks.sh"
    print_success "Hook integration script created"
}

run_validation() {
    local project_path="$1"
    
    print_info "Running validation checks..."
    
    cd "$project_path"
    
    # Check if manifests directory exists
    if [ -d ".claude/manifests" ]; then
        print_success "Manifests directory created"
    fi
    
    # Check if workflows exist
    if [ -d ".github/workflows" ] && [ "$(ls -A .github/workflows)" ]; then
        print_success "GitHub workflows deployed"
    fi
    
    # Check if CLAUDE.md is updated
    if grep -q "Code Intelligence System" "CLAUDE.md" 2>/dev/null; then
        print_success "CLAUDE.md updated with Code Intelligence"
    fi
    
    # Try to run pre-agent context hook
    if python3 ~/.claude/hooks/pre-agent-context.py --summary &>/dev/null; then
        print_success "Pre-agent context hook working"
    else
        print_warning "Pre-agent context hook needs manual testing"
    fi
}

print_completion_summary() {
    local project_path="$1"
    
    echo
    echo -e "${GREEN}🎉 Deployment Complete!${NC}"
    echo
    echo -e "${BLUE}📁 Project:${NC} $(basename "$project_path")"
    echo -e "${BLUE}📍 Location:${NC} $project_path"
    echo
    echo -e "${YELLOW}🚀 What's been deployed:${NC}"
    echo "   ✅ GitHub Actions for silent failure detection"
    echo "   ✅ Automated code intelligence manifests"
    echo "   ✅ PR creation and checkpoint automation"
    echo "   ✅ Agent templates with manifest context"
    echo "   ✅ Git Branch Intelligence with MCP integration"
    echo
    echo -e "${YELLOW}📖 Next steps:${NC}"
    echo "   1. Commit and push to trigger first workflow"
    echo "   2. Open a PR to see silent failure detection"
    echo "   3. Use '@claude fix-silent-failures' to auto-fix issues"
    echo "   4. Agents will now read manifests automatically"
    echo
    echo -e "${BLUE}🔧 Manual commands:${NC}"
    echo "   • Generate manifests: cd '$project_path' && bun ~/.claude/scripts/generate-manifests.ts"
    echo "   • Create checkpoint: python3 ~/.claude/hooks/auto-checkpoint-hook.py --now"
    echo "   • Load context: python3 ~/.claude/hooks/pre-agent-context.py"
    echo "   • Suggest branch: .claude/hooks/suggest-branch.sh"
    echo "   • Create smart branch: .claude/hooks/create-smart-branch.sh 'feature description'"
    echo
}

main() {
    print_header
    
    check_dependencies
    
    local project_path
    project_path=$(detect_project_path "$@")
    
    print_info "Deploying to project: $project_path"
    
    local project_type
    project_type=$(detect_project_type "$project_path")
    print_info "Detected project type: $project_type"
    
    backup_existing "$project_path"
    
    deploy_github_workflows "$project_path" "$project_type"
    deploy_claude_config "$project_path" "$project_type"
    generate_initial_manifests "$project_path"
    deploy_git_branch_intelligence "$project_path"
    setup_git_hooks "$project_path"
    
    run_validation "$project_path"
    
    print_completion_summary "$project_path"
}

# Handle help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [project_path]"
    echo
    echo "Deploys Claude Code Intelligence & Silent Failure Prevention to a project."
    echo
    echo "Arguments:"
    echo "  project_path    Path to project (optional, detects current directory)"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo
    echo "Examples:"
    echo "  $0                           # Deploy to current directory"
    echo "  $0 ~/Projects/my-app         # Deploy to specific project"
    echo
    exit 0
fi

# Run main function
main "$@"