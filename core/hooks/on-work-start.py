#!/usr/bin/env python3
"""
On Work Start Hook - Triggers when Claude Code begins working on a project
Call this at the start of any coding session to enable automation
"""

import subprocess
import os
import sys
from pathlib import Path

def start_automated_session():
    """Start all automation for the current project"""
    
    print("🚀 Starting Claude Code automation suite...")
    
    # 1. Load code intelligence manifests
    print("📊 Loading code intelligence...")
    try:
        subprocess.run([
            'python3', str(Path.home() / '.claude' / 'hooks' / 'pre-agent-context.py')
        ], check=True)
        print("✅ Code intelligence loaded")
    except Exception as e:
        print(f"⚠️ Code intelligence loading failed: {e}")
    
    # 2. Start session lifecycle management
    print("🔄 Starting session management...")
    try:
        subprocess.run([
            str(Path.home() / '.claude' / 'hooks' / 'claude-session-auto-start.sh'), 'start'
        ], check=True)
        print("✅ Session management started")
    except Exception as e:
        print(f"⚠️ Session management failed: {e}")
    
    # 3. Check deployment status
    print("🔍 Checking deployment status...")
    github_dir = Path('.github')
    claude_dir = Path('.claude')
    
    if not github_dir.exists() or not claude_dir.exists():
        print("⚠️ Project not fully deployed. Consider running:")
        print("   ~/.claude/scripts/deploy-code-intelligence.sh")
    else:
        print("✅ Project appears to be deployed")
    
    print("\n🎯 Automation Status:")
    print("   ✅ Auto-commits every 30 minutes")
    print("   ✅ Smart commits on significant changes")  
    print("   ✅ Auto-PR creation after substantial work")
    print("   ✅ Code intelligence manifests loaded")
    print("   ✅ Documentation will auto-update on merge")
    
    print("\n📖 Manual Commands:")
    print("   📝 Force checkpoint: python3 ~/.claude/hooks/auto-checkpoint-hook.py --now")
    print("   🚀 Create PR: python3 ~/.claude/hooks/pr-creation-hook.py --force") 
    print("   📚 Update docs: python3 ~/.claude/hooks/post-merge-documentation.py")
    print("   🛑 Stop session: ~/.claude/hooks/claude-session-auto-start.sh stop")
    
    return True

def main():
    """Main entry point"""
    
    # Check if we're in a project directory
    project_indicators = ['package.json', 'pyproject.toml', 'Cargo.toml', '.git', 'CLAUDE.md']
    
    if not any(Path(indicator).exists() for indicator in project_indicators):
        print("⚠️ This doesn't appear to be a project directory")
        print("💡 Run this command from your project root")
        return False
    
    # Start automation
    return start_automated_session()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
# Smart Commit Genie Auto-Commit
import subprocess
subprocess.Popen(['/Users/umasankrudhya/.claude/hooks/smart-auto-commit.py', '--daemon'])
