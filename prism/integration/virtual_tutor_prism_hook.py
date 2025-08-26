#!/usr/bin/env python3
"""
Virtual-Tutor PRISM Integration Hook

This hook optimizes context delivery for all agents working on the virtual-tutor project.
It reduces context from 139.7KB (all manifests) to <20KB of relevant manifests per agent.

Usage: Place this file in ~/Projects/virtual-tutor/.claude/hooks/
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add PRISM modules to path
prism_paths = [
    Path.home() / 'claude-automations' / 'git-intelligence' / 'src',
    Path.home() / 'claude-automations' / 'prism' / 'src'
]

for path in prism_paths:
    if str(path) not in sys.path:
        sys.path.append(str(path))

def detect_agent_type_from_task(task: str) -> str:
    """Enhanced agent detection for virtual-tutor specific tasks"""
    task_lower = task.lower()
    
    # Virtual-tutor specific patterns
    if any(word in task_lower for word in ['course', 'lesson', 'curriculum', 'learning', 'student']):
        return 'course-builder'
    elif any(word in task_lower for word in ['payment', 'billing', 'subscription', 'checkout', 'stripe']):
        return 'payment-specialist'
    elif any(word in task_lower for word in ['component', 'react', 'ui', 'interface', 'frontend']):
        return 'frontend-developer'
    elif any(word in task_lower for word in ['api', 'endpoint', 'database', 'backend', 'server']):
        return 'backend-architect'
    elif any(word in task_lower for word in ['test', 'spec', 'coverage', 'jest', 'pytest']):
        return 'test-writer-fixer'
    else:
        return 'general'

def get_virtual_tutor_manifest_priorities():
    """Virtual-tutor specific manifest priorities"""
    return {
        'course-builder': {
            'core': ['component-manifest.json', 'project-manifest.json', 'CODEBASE_MANIFEST.yaml'],
            'extended': ['api-manifest.json', 'database-manifest.json', 'FUNCTION_REGISTRY.md'],
            'optional': ['test-manifest.json', 'deployment-manifest.json']
        },
        'payment-specialist': {
            'core': ['api-manifest.json', 'security-manifest.json', 'database-manifest.json'],
            'extended': ['backend-manifest.json', 'FUNCTION_REGISTRY.md'],
            'optional': ['test-manifest.json', 'component-manifest.json']
        },
        'frontend-developer': {
            'core': ['component-manifest.json', 'project-manifest.json', 'CODEBASE_MANIFEST.yaml'],
            'extended': ['api-manifest.json', 'TECH_STACK.json'],
            'optional': ['test-manifest.json', 'security-manifest.json']
        },
        'backend-architect': {
            'core': ['api-manifest.json', 'backend-manifest.json', 'database-manifest.json'],
            'extended': ['security-manifest.json', 'FUNCTION_REGISTRY.md'],
            'optional': ['component-manifest.json', 'deployment-manifest.json']
        },
        'test-writer-fixer': {
            'core': ['test-manifest.json', 'FUNCTION_REGISTRY.md'],
            'extended': ['api-manifest.json', 'component-manifest.json'],
            'optional': ['database-manifest.json', 'security-manifest.json']
        },
        'general': {
            'core': ['CODEBASE_MANIFEST.yaml', 'project-manifest.json'],
            'extended': ['FUNCTION_REGISTRY.md', 'api-manifest.json'],
            'optional': ['component-manifest.json', 'database-manifest.json']
        }
    }

def load_manifest(manifest_dir: Path, manifest_name: str):
    """Load a specific manifest file"""
    manifest_path = manifest_dir / manifest_name
    
    if manifest_path.exists():
        try:
            if manifest_path.suffix == '.json':
                with open(manifest_path) as f:
                    return json.load(f)
            elif manifest_path.suffix in ['.yaml', '.yml']:
                try:
                    import yaml
                    with open(manifest_path) as f:
                        return yaml.safe_load(f)
                except ImportError:
                    # Fallback to reading as text if yaml not available
                    with open(manifest_path) as f:
                        return {"content": f.read()}
            else:
                # Read as text for other formats
                with open(manifest_path) as f:
                    return {"content": f.read()}
        except Exception as e:
            print(f"[PRISM] Warning: Failed to load {manifest_name}: {e}")
            return None
    
    return None

def optimize_context_for_virtual_tutor():
    """Main optimization function for virtual-tutor project"""
    try:
        # Get task and agent info from environment or command line
        task = os.environ.get('CLAUDE_USER_PROMPT', '')
        agent_type = os.environ.get('CLAUDE_AGENT_TYPE', '')
        
        # If no explicit agent type, detect from task
        if not agent_type and task:
            agent_type = detect_agent_type_from_task(task)
        elif not agent_type:
            agent_type = 'general'
        
        print(f"[PRISM] 🧬 Optimizing context for virtual-tutor")
        print(f"[PRISM] 🤖 Agent: {agent_type}")
        if task:
            print(f"[PRISM] 📋 Task: {task[:80]}{'...' if len(task) > 80 else ''}")
        
        # Locate manifests
        project_root = Path.cwd()
        manifest_dir = project_root / '.claude' / 'manifests'
        
        if not manifest_dir.exists():
            print(f"[PRISM] ⚠️ No manifest directory found at {manifest_dir}")
            return
        
        # Get available manifests
        available_manifests = []
        total_size_kb = 0
        
        for manifest_file in manifest_dir.iterdir():
            if manifest_file.is_file() and not manifest_file.name.startswith('.'):
                available_manifests.append(manifest_file.name)
                total_size_kb += manifest_file.stat().st_size / 1024
        
        print(f"[PRISM] 📁 Found {len(available_manifests)} manifests ({total_size_kb:.1f}KB total)")
        
        # Get priorities for this agent type
        priorities = get_virtual_tutor_manifest_priorities()
        agent_priorities = priorities.get(agent_type, priorities['general'])
        
        # Select manifests to load
        selected_manifests = []
        context_data = {}
        selected_size_kb = 0
        
        # Load core manifests (always include)
        for manifest_name in agent_priorities['core']:
            if manifest_name in available_manifests:
                manifest_data = load_manifest(manifest_dir, manifest_name)
                if manifest_data:
                    context_data[manifest_name] = manifest_data
                    selected_manifests.append(manifest_name)
                    manifest_size = (manifest_dir / manifest_name).stat().st_size / 1024
                    selected_size_kb += manifest_size
        
        # Load extended manifests if under size limit
        size_limit_kb = 30.0  # Conservative limit for virtual-tutor
        
        for manifest_name in agent_priorities['extended']:
            if selected_size_kb < size_limit_kb and manifest_name in available_manifests:
                manifest_data = load_manifest(manifest_dir, manifest_name)
                if manifest_data:
                    manifest_size = (manifest_dir / manifest_name).stat().st_size / 1024
                    if selected_size_kb + manifest_size <= size_limit_kb:
                        context_data[manifest_name] = manifest_data
                        selected_manifests.append(manifest_name)
                        selected_size_kb += manifest_size
        
        # Load optional manifests if still under limit
        for manifest_name in agent_priorities['optional']:
            if selected_size_kb < size_limit_kb * 0.8 and manifest_name in available_manifests:
                manifest_data = load_manifest(manifest_dir, manifest_name)
                if manifest_data:
                    manifest_size = (manifest_dir / manifest_name).stat().st_size / 1024
                    if selected_size_kb + manifest_size <= size_limit_kb:
                        context_data[manifest_name] = manifest_data
                        selected_manifests.append(manifest_name)
                        selected_size_kb += manifest_size
        
        # Calculate optimization metrics
        reduction_percent = ((total_size_kb - selected_size_kb) / total_size_kb) * 100 if total_size_kb > 0 else 0
        
        # Create optimized context package
        context_package = {
            'project': 'virtual-tutor',
            'agent_type': agent_type,
            'task_summary': task[:100] if task else 'No task specified',
            'optimization_timestamp': datetime.now().isoformat(),
            'manifests_loaded': selected_manifests,
            'manifests_count': len(selected_manifests),
            'context_size_kb': selected_size_kb,
            'original_size_kb': total_size_kb,
            'size_reduction_percent': reduction_percent,
            'context': context_data
        }
        
        # Write optimized context
        optimized_context_file = manifest_dir / 'PRISM_OPTIMIZED_CONTEXT.json'
        with open(optimized_context_file, 'w') as f:
            json.dump(context_package, f, indent=2, default=str)
        
        # Report results
        print(f"[PRISM] ✅ Context optimized successfully!")
        print(f"[PRISM] 📊 Size: {selected_size_kb:.1f}KB (was {total_size_kb:.1f}KB)")
        print(f"[PRISM] 📉 Reduction: {reduction_percent:.1f}%")
        print(f"[PRISM] 📄 Manifests: {len(selected_manifests)}/{len(available_manifests)}")
        print(f"[PRISM] 🎯 Selected: {', '.join(selected_manifests[:3])}{'...' if len(selected_manifests) > 3 else ''}")
        
        # Log usage for learning (simple file-based approach)
        usage_log = manifest_dir.parent / 'prism_usage.log'
        with open(usage_log, 'a') as f:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'agent_type': agent_type,
                'manifests_used': selected_manifests,
                'context_size_kb': selected_size_kb,
                'reduction_percent': reduction_percent,
                'task_keywords': task.lower().split()[:10] if task else []
            }
            f.write(json.dumps(log_entry) + '\n')
        
        return context_package
        
    except ImportError as e:
        print(f"[PRISM] ⚠️ PRISM components not available: {e}")
        print(f"[PRISM] 💡 Using fallback context optimization...")
        return None
        
    except Exception as e:
        print(f"[PRISM] ❌ Context optimization failed: {e}")
        print(f"[PRISM] 💡 Agent will use standard context loading")
        return None

def main():
    """Main entry point"""
    result = optimize_context_for_virtual_tutor()
    
    if result:
        # Success
        exit_code = 0
    else:
        # Fallback - don't block agent execution
        print("[PRISM] 🔄 Falling back to standard context loading")
        exit_code = 0
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()