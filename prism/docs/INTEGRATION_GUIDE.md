# PRISM Integration Guide for Virtual-Tutor

This guide shows how to integrate PRISM into the virtual-tutor project for immediate context optimization benefits.

## 🎯 Integration Overview

PRISM will optimize virtual-tutor's context delivery by:
- Reducing context from 139.7KB (current manifests) to <20KB per agent
- Providing agent-specific context based on task intent
- Auto-updating manifests when code changes
- Learning from usage patterns to improve over time

## 📋 Step-by-Step Integration

### Step 1: Install PRISM Hook

Create the PRISM integration hook in virtual-tutor:

```bash
# Create virtual-tutor specific hook
mkdir -p ~/Projects/virtual-tutor/.claude/hooks
```

Create hook file:
```python
#!/usr/bin/env python3
"""
Virtual-Tutor PRISM Integration Hook
Optimizes context delivery for all agents working on virtual-tutor
"""

import sys
import os
from pathlib import Path

# Add PRISM to path
sys.path.append(str(Path.home() / 'claude-automations' / 'git-intelligence' / 'src'))
sys.path.append(str(Path.home() / 'claude-automations' / 'prism' / 'src'))

def optimize_context_for_agent():
    """Main hook - called before any agent execution"""
    try:
        from context_router import ContextRouter
        
        # Get agent type and task from environment
        agent_type = os.environ.get('CLAUDE_AGENT_TYPE', 'general')
        task = os.environ.get('CLAUDE_USER_PROMPT', '')
        
        if not task:
            return  # No optimization possible without task
        
        print(f"[PRISM] Optimizing context for {agent_type}...")
        
        # Initialize router with virtual-tutor manifests
        project_root = Path.cwd()
        manifest_dir = project_root / '.claude' / 'manifests'
        router = ContextRouter(manifest_dir)
        
        # Route optimal context
        route = router.route_context(task, agent_type)
        context_package = router.create_context_package(route)
        
        # Report optimization
        size_kb = context_package['context_size_kb']
        manifests = context_package['manifests_loaded']
        reduction = ((139.7 - size_kb) / 139.7) * 100
        
        print(f"[PRISM] ✅ Context optimized: {size_kb:.2f}KB ({reduction:.1f}% reduction)")
        print(f"[PRISM] 📄 Loaded {len(manifests)} relevant manifests")
        
        # Write optimized context for agent
        optimal_context_file = manifest_dir / 'PRISM_OPTIMIZED_CONTEXT.json'
        with open(optimal_context_file, 'w') as f:
            import json
            json.dump(context_package, f, indent=2)
            
    except Exception as e:
        print(f"[PRISM] Warning: Context optimization failed: {e}")
        # Don't block agent execution on PRISM failure

if __name__ == '__main__':
    optimize_context_for_agent()
```

### Step 2: Configure Hook in Claude Code

Add to virtual-tutor's hook configuration:

```bash
# Create hook config if it doesn't exist
echo '[hooks.pre_agent]
path = ".claude/hooks/prism_optimize_context.py"
description = "PRISM context optimization"' >> ~/Projects/virtual-tutor/.claude/hooks.toml
```

### Step 3: Start PRISM Orchestrator

Start the orchestrator for virtual-tutor:

```bash
cd ~/Projects/virtual-tutor
python3 ~/claude-automations/prism/src/prism_orchestrator.py --start --daemon
```

### Step 4: Enable Real-time Monitoring

Start the dashboard to observe PRISM performance:

```bash
# Live dashboard (in separate terminal)
cd ~/Projects/virtual-tutor
python3 ~/claude-automations/prism/src/prism_dashboard.py --live

# Or static snapshot
python3 ~/claude-automations/prism/src/prism_dashboard.py --static
```

## 📊 Usage Examples

### Example 1: Frontend Development
```
User: "Create a new React component for the course progress tracker"

Without PRISM: Loads all 18 manifests (139.7KB)
With PRISM: Loads only COMPONENT_MANIFEST, UI_PATTERNS, TYPE_DEFINITIONS (~5KB)
Result: 96% size reduction, faster response
```

### Example 2: Backend API Work  
```
User: "Add authentication to the course enrollment API endpoint"

Without PRISM: Loads all 18 manifests (139.7KB)  
With PRISM: Loads only API_SURFACE, SECURITY_MANIFEST, DATABASE_SCHEMA (~15KB)
Result: 89% size reduction, focused context
```

### Example 3: Testing
```
User: "Write unit tests for the payment processing module"

Without PRISM: Loads all 18 manifests (139.7KB)
With PRISM: Loads only TEST_MANIFEST, FUNCTION_REGISTRY (~8KB)  
Result: 94% size reduction, relevant test context
```

## 🔍 Observing PRISM Performance

### Real-time Dashboard
The dashboard shows:
- **Context Size Reduction**: Track % reduction from 139.7KB baseline
- **Agent Performance**: See which agents benefit most  
- **Manifest Usage**: Which manifests are actually used
- **System Health**: Monitor all components
- **Learning Progress**: How profiles improve over time

### Key Metrics to Watch
1. **Average Context Size**: Should drop from 139.7KB to <20KB
2. **Reduction Percentage**: Target 85%+ reduction
3. **Routing Accuracy**: Should be >95%
4. **Agent Response Time**: Should improve 3-5x
5. **Manifest Freshness**: Should stay >80% fresh

### Log Analysis
```bash
# View PRISM logs
tail -f ~/.claude/prism/logs/prism_$(date +%Y%m%d).log

# View optimization events
grep "Context optimized" ~/.claude/prism/logs/prism_$(date +%Y%m%d).log
```

## 🔧 Refinement Process

### Phase 1: Baseline Measurement (Week 1)
1. **Collect baseline metrics** without PRISM
2. **Enable PRISM** and measure improvement
3. **Document pain points** and edge cases

### Phase 2: Profile Optimization (Week 2)
1. **Analyze agent usage patterns** from logs
2. **Adjust Context DNA profiles** for virtual-tutor specific needs
3. **Fine-tune routing rules** based on common tasks

### Phase 3: Advanced Features (Week 3)
1. **Enable real-time manifest updates** (requires `pip install watchdog`)
2. **Set up documentation syncing** for README updates
3. **Configure learning feedback loops**

## 🛠️ Customization for Virtual-Tutor

### Add Virtual-Tutor Specific Domains
```python
# Add to context_router.py domain_keywords
'education': [
    'course', 'lesson', 'student', 'instructor', 'curriculum', 
    'assignment', 'grade', 'enrollment', 'learning', 'tutor',
    'quiz', 'exam', 'progress', 'achievement', 'certificate'
],
'ecommerce': [
    'payment', 'billing', 'subscription', 'checkout', 'cart',
    'pricing', 'discount', 'refund', 'transaction', 'invoice'
]
```

### Create Virtual-Tutor Agent Profiles
```python
# Add to context_dna.py DEFAULT_PROFILES
'course-builder': {
    'essential_manifests': ['COURSE_MANIFEST', 'CONTENT_PATTERNS', 'LEARNING_OBJECTIVES'],
    'optional_manifests': ['USER_MANIFEST', 'ASSESSMENT_PATTERNS'],
    'max_context_kb': 25
},
'payment-specialist': {
    'essential_manifests': ['PAYMENT_MANIFEST', 'SECURITY_PATTERNS', 'API_SURFACE'],
    'optional_manifests': ['DATABASE_SCHEMA', 'ERROR_HANDLING'],
    'max_context_kb': 20
}
```

## ⚡ Quick Start Commands

```bash
# 1. Integrate PRISM into virtual-tutor
cd ~/Projects/virtual-tutor
curl -s https://raw.githubusercontent.com/your-repo/prism-integration.py > .claude/hooks/prism_optimize_context.py
chmod +x .claude/hooks/prism_optimize_context.py

# 2. Start PRISM orchestrator
python3 ~/claude-automations/prism/src/prism_orchestrator.py --start --project-root ~/Projects/virtual-tutor &

# 3. Test the integration
python3 ~/claude-automations/prism/test_prism.py --project-root ~/Projects/virtual-tutor

# 4. Monitor performance
python3 ~/claude-automations/prism/src/prism_dashboard.py --project-root ~/Projects/virtual-tutor --live
```

## 🎯 Success Criteria for Virtual-Tutor

After integration, you should see:

✅ **Context Size**: Drop from 139.7KB to <20KB average  
✅ **Agent Speed**: 3-5x faster responses  
✅ **Relevance**: Agents get exactly what they need  
✅ **Learning**: System improves with usage  
✅ **Automation**: No manual manifest management  

## 🔄 Feedback Loop

1. **Use agents normally** in virtual-tutor development
2. **Monitor dashboard** for optimization opportunities  
3. **Review logs** for common patterns
4. **Adjust profiles** based on actual usage
5. **Measure improvements** in agent effectiveness

PRISM will learn your development patterns and continuously optimize context delivery for maximum agent performance on virtual-tutor!