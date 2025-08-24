#!/usr/bin/env python3
"""
Context DNA Loader Hook - Part of PRISM

Pre-agent hook that loads only the necessary context based on agent DNA profiles.
This dramatically reduces context size and improves agent performance.
"""

import os
import sys
import json
from pathlib import Path

# Add prism src to path
sys.path.append(str(Path.home() / 'claude-automations' / 'prism' / 'src'))

try:
    from context_dna import ContextDNAProfiler
except ImportError:
    print("[PRISM] Warning: Context DNA module not found, using standard context loading")
    sys.exit(0)


def detect_agent_type() -> str:
    """Detect which agent is being invoked"""
    # Check environment variables
    agent_type = os.environ.get('CLAUDE_AGENT_TYPE', '')
    
    if agent_type:
        return agent_type
    
    # Try to detect from task prompt
    task = os.environ.get('CLAUDE_USER_PROMPT', '').lower()
    
    # Pattern matching for common agent indicators
    if any(word in task for word in ['frontend', 'react', 'component', 'ui', 'interface']):
        return 'frontend-developer'
    elif any(word in task for word in ['backend', 'api', 'database', 'server', 'endpoint']):
        return 'backend-architect'
    elif any(word in task for word in ['test', 'spec', 'coverage', 'jest', 'pytest']):
        return 'test-writer-fixer'
    elif any(word in task for word in ['design', 'ux', 'user experience', 'wireframe']):
        return 'ui-designer'
    elif any(word in task for word in ['deploy', 'ci/cd', 'docker', 'kubernetes']):
        return 'devops-automator'
    else:
        return 'general'


def load_optimal_context():
    """Pre-agent hook to load only necessary context"""
    print("[PRISM] Context DNA Loader activated")
    
    # Detect agent type
    agent_type = detect_agent_type()
    
    # Get task description
    task = os.environ.get('CLAUDE_USER_PROMPT', '')
    
    if not task:
        print("[PRISM] No task detected, skipping context optimization")
        return
    
    # Initialize profiler
    profiler = ContextDNAProfiler()
    
    # Get optimal context
    print(f"[PRISM] Loading optimal context for {agent_type}")
    context_package = profiler.get_optimal_context(agent_type, task)
    
    # Create manifest directory
    manifest_dir = Path.home() / '.claude' / 'manifests'
    manifest_dir.mkdir(parents=True, exist_ok=True)
    
    # Write optimal context to manifest location
    optimal_context_file = manifest_dir / 'OPTIMAL_CONTEXT.json'
    optimal_context_file.write_text(json.dumps(context_package, indent=2))
    
    # Write individual manifests for backward compatibility
    for manifest_name, manifest_data in context_package.get('context', {}).items():
        manifest_file = manifest_dir / f'{manifest_name}.json'
        manifest_file.write_text(json.dumps(manifest_data, indent=2))
    
    # Print summary
    print(f"[PRISM] Agent Type: {agent_type}")
    print(f"[PRISM] Manifests Loaded: {', '.join(context_package['manifests_loaded'])}")
    print(f"[PRISM] Context Size: {context_package['context_size_kb']:.2f} KB")
    print(f"[PRISM] Max Allowed: {profiler.profiles[agent_type].max_context_kb} KB")
    
    # Check if we're under the limit
    if context_package['context_size_kb'] <= profiler.profiles[agent_type].max_context_kb:
        print(f"[PRISM] ✅ Context optimized successfully!")
    else:
        print(f"[PRISM] ⚠️ Context compressed to fit size limit")
    
    # Save usage statistics for learning
    profiler.save_profiles()


def main():
    """Main entry point"""
    try:
        load_optimal_context()
    except Exception as e:
        print(f"[PRISM] Error in context DNA loader: {e}")
        # Don't fail the entire operation
        sys.exit(0)


if __name__ == "__main__":
    main()