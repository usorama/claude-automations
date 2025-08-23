#!/bin/bash

# Git Intelligence System - Setup Script
# Sets up the development environment and project structure

set -e

echo "🚀 Setting up Git Intelligence System..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create directory structure
echo "📁 Creating project structure..."
mkdir -p src/{core,hooks,ui,learning}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p config
mkdir -p docs
mkdir -p logs

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
cat > requirements.txt << 'EOF'
GitPython>=3.1.0
click>=8.0.0
rich>=13.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
EOF

pip install --upgrade pip
pip install -r requirements.txt

# Create configuration files
echo "⚙️ Creating configuration files..."

# Default configuration
cat > config/defaults.json << 'EOF'
{
  "commit": {
    "conventional": true,
    "types": ["feat", "fix", "docs", "style", "refactor", "test", "chore"],
    "scope_required": false,
    "body_required": false,
    "breaking_change_prefix": "BREAKING CHANGE:"
  },
  "branch": {
    "prefix_separator": "/",
    "lowercase": true,
    "max_length": 50,
    "protected": ["main", "master", "develop", "staging", "production"]
  },
  "suggestions": {
    "auto_stage": false,
    "show_diff": true,
    "max_diff_lines": 50,
    "timeout_seconds": 30
  },
  "ui": {
    "color_scheme": "default",
    "show_emoji": true,
    "compact_mode": false
  },
  "learning": {
    "enabled": true,
    "min_samples": 10,
    "confidence_threshold": 0.7
  }
}
EOF

# Git patterns configuration
cat > config/patterns.json << 'EOF'
{
  "work_patterns": {
    "feature": {
      "indicators": ["add", "implement", "create", "new"],
      "file_patterns": ["src/", "components/", "features/"],
      "commit_prefix": "feat"
    },
    "bugfix": {
      "indicators": ["fix", "resolve", "repair", "correct"],
      "file_patterns": ["src/", "lib/"],
      "commit_prefix": "fix"
    },
    "documentation": {
      "indicators": ["update", "document", "readme"],
      "file_patterns": ["*.md", "docs/", "*.rst"],
      "commit_prefix": "docs"
    },
    "testing": {
      "indicators": ["test", "spec", "coverage"],
      "file_patterns": ["test/", "tests/", "*.test.*", "*.spec.*"],
      "commit_prefix": "test"
    },
    "refactoring": {
      "indicators": ["refactor", "optimize", "simplify", "clean"],
      "file_patterns": ["src/", "lib/"],
      "commit_prefix": "refactor"
    },
    "configuration": {
      "indicators": ["config", "setup", "settings"],
      "file_patterns": ["*.json", "*.yaml", "*.toml", ".env"],
      "commit_prefix": "chore"
    }
  },
  "file_categories": {
    "source": ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.go"],
    "test": ["*.test.*", "*.spec.*", "test_*.py"],
    "config": ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini"],
    "documentation": ["*.md", "*.rst", "*.txt", "README*"],
    "style": ["*.css", "*.scss", "*.less"],
    "asset": ["*.png", "*.jpg", "*.svg", "*.gif"],
    "data": ["*.csv", "*.sql", "*.db"]
  }
}
EOF

# Create .env template
cat > .env.template << 'EOF'
# Git Intelligence Configuration
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=logs/git-intelligence.log

# Claude Code Integration
CLAUDE_PROJECT_DIR=${CLAUDE_PROJECT_DIR}
CLAUDE_HOOK_TIMEOUT=60

# Feature Flags
ENABLE_LEARNING=true
ENABLE_BRANCH_INTELLIGENCE=false
ENABLE_PR_INTELLIGENCE=false

# GitHub Integration (Phase 3)
GITHUB_TOKEN=
GITHUB_API_URL=https://api.github.com
EOF

# Create initial source files
echo "📝 Creating initial source files..."

# Create __init__ files
touch src/__init__.py
touch src/core/__init__.py
touch src/hooks/__init__.py
touch src/ui/__init__.py
touch src/learning/__init__.py

# Create logger setup
cat > src/logger.py << 'EOF'
"""Logging configuration for Git Intelligence System"""
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "git-intelligence") -> logging.Logger:
    """Set up logger with console and file handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # File handler
    log_file = log_dir / f"{name}-{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create default logger
logger = setup_logger()
EOF

# Create main entry point
cat > src/main.py << 'EOF'
#!/usr/bin/env python3
"""
Git Intelligence System - Main Entry Point
"""
import click
from pathlib import Path
from logger import logger

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Git Intelligence System - Smart git operations for Claude Code"""
    pass

@cli.command()
@click.option('--path', default='.', help='Repository path')
def analyze(path):
    """Analyze repository state and suggest git operations"""
    logger.info(f"Analyzing repository at {path}")
    # TODO: Implement analyzer
    click.echo("Repository analysis not yet implemented")

@cli.command()
@click.option('--message', help='Commit message')
@click.option('--auto', is_flag=True, help='Auto-generate message')
def commit(message, auto):
    """Create intelligent commit"""
    if auto:
        logger.info("Auto-generating commit message")
        # TODO: Implement auto-generation
        click.echo("Auto-generation not yet implemented")
    else:
        logger.info(f"Creating commit with message: {message}")
        # TODO: Implement commit
        click.echo("Commit creation not yet implemented")

@cli.command()
def status():
    """Show git intelligence status"""
    logger.info("Checking system status")
    click.echo("Git Intelligence System v0.1.0")
    click.echo("Status: Ready for development")
    # TODO: Add actual status checks

if __name__ == '__main__':
    cli()
EOF

chmod +x src/main.py

# Create test structure
echo "🧪 Setting up test framework..."

cat > tests/__init__.py << 'EOF'
"""Test suite for Git Intelligence System"""
EOF

cat > tests/conftest.py << 'EOF'
"""Pytest configuration and fixtures"""
import pytest
from pathlib import Path
import tempfile
import git

@pytest.fixture
def temp_repo():
    """Create a temporary git repository for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = git.Repo.init(tmpdir)
        # Add initial commit
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Repository")
        repo.index.add([str(readme)])
        repo.index.commit("Initial commit")
        yield repo

@pytest.fixture
def sample_changes():
    """Sample file changes for testing"""
    return {
        "added": ["src/new_feature.py"],
        "modified": ["src/existing.py", "README.md"],
        "deleted": ["src/old_feature.py"]
    }
EOF

# Create development utilities
cat > dev.sh << 'EOF'
#!/bin/bash
# Development utilities

case "$1" in
    test)
        echo "Running tests..."
        source venv/bin/activate
        pytest tests/ -v --cov=src --cov-report=term-missing
        ;;
    lint)
        echo "Running linters..."
        source venv/bin/activate
        python -m flake8 src/ tests/
        python -m black src/ tests/ --check
        ;;
    format)
        echo "Formatting code..."
        source venv/bin/activate
        python -m black src/ tests/
        ;;
    run)
        echo "Running main program..."
        source venv/bin/activate
        python src/main.py "${@:2}"
        ;;
    *)
        echo "Usage: ./dev.sh {test|lint|format|run}"
        exit 1
        ;;
esac
EOF

chmod +x dev.sh

# Create hook integration template
cat > src/hooks/template.py << 'EOF'
#!/usr/bin/env python3
"""
Template for Claude Code hook integration
This will be customized for each hook type
"""
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main hook entry point"""
    # Read input from Claude Code
    input_data = json.loads(sys.stdin.read())
    
    # Process the hook event
    # TODO: Implement specific hook logic
    
    # Return success
    sys.exit(0)

if __name__ == '__main__':
    main()
EOF

# Create README for the git-intelligence system
cat > README.md << 'EOF'
# Git Intelligence System

Smart git operations for Claude Code sessions.

## Quick Start

1. Run setup: `./setup.sh`
2. Activate environment: `source venv/bin/activate`
3. Run tests: `./dev.sh test`
4. Check status: `./dev.sh run status`

## Development

- Run tests: `./dev.sh test`
- Format code: `./dev.sh format`
- Lint code: `./dev.sh lint`
- Run CLI: `./dev.sh run [command]`

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

## Implementation

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for development phases.
EOF

# Final setup steps
echo "🔧 Finalizing setup..."

# Initialize git if not already
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "feat: Initial Git Intelligence System setup"
fi

# Create initial log file
touch logs/setup.log
echo "Setup completed at $(date)" > logs/setup.log

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run tests: ./dev.sh test"
echo "3. Check status: ./dev.sh run status"
echo "4. Begin Day 2 implementation (Git State Analyzer)"
echo ""
echo "📚 Documentation:"
echo "- Architecture: ARCHITECTURE.md"
echo "- Implementation Plan: IMPLEMENTATION_PLAN.md"
echo "- README: README.md"
EOF

chmod +x setup.sh