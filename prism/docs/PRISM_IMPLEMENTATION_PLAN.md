# 🔮 PRISM: Proactive Real-time Intelligence System for Manifests

**Version 1.0** | Implementation Ready | Day 5 Innovation

---

## 🎯 The Vision

Stop agents from drowning in context. Give them laser-focused intelligence based on what they're actually doing.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     PRISM CORE                          │
├──────────────┬─────────────┬──────────────┬────────────┤
│ Context DNA  │ Smart Cache │ Change Intel │ Auto Docs  │
├──────────────┼─────────────┼──────────────┼────────────┤
│   Profiler   │   Router    │   Watcher    │   Syncer   │
└──────────────┴─────────────┴──────────────┴────────────┘
```

## 🧬 Component 1: Context DNA Profiler

### **What It Does**
Creates unique "DNA profiles" for each agent type showing exactly what context they need.

### **Implementation: `git-intelligence/src/context_dna.py`**

```python
from dataclasses import dataclass
from typing import Dict, List, Set
import json
from pathlib import Path

@dataclass
class ContextDNA:
    """DNA profile for an agent type"""
    agent_type: str
    essential_manifests: List[str]  # Always load
    optional_manifests: List[str]   # Load if relevant
    never_manifests: List[str]       # Never load
    max_context_kb: int              # Size limit
    success_patterns: Dict[str, float]  # What worked

class ContextDNAProfiler:
    def __init__(self):
        self.profiles_path = Path.home() / '.claude' / 'manifests' / 'dna_profiles.json'
        self.profiles = self.load_profiles()
        
    def get_optimal_context(self, agent_type: str, task_description: str) -> Dict:
        """Get exactly what this agent needs for this task"""
        profile = self.profiles.get(agent_type, self.get_default_profile())
        
        # Start with essentials
        context = self.load_manifests(profile.essential_manifests)
        
        # Add optional based on task analysis
        if self.task_needs_api_context(task_description):
            context.update(self.load_manifest('API_SURFACE'))
            
        if self.task_needs_database_context(task_description):
            context.update(self.load_manifest('DATABASE_SCHEMA'))
            
        # Compress if over limit
        if self.get_size_kb(context) > profile.max_context_kb:
            context = self.compress_context(context, profile)
            
        return context
```

### **Hook Integration: `core/hooks/context-dna-loader.py`**

```python
#!/usr/bin/env python3
"""Load optimal context based on agent DNA profiles"""

import os
import sys
from pathlib import Path
sys.path.append(str(Path.home() / 'claude-automations' / 'git-intelligence' / 'src'))

from context_dna import ContextDNAProfiler

def load_optimal_context():
    """Pre-agent hook to load only necessary context"""
    agent_type = os.environ.get('CLAUDE_AGENT_TYPE', 'general')
    task = os.environ.get('CLAUDE_USER_PROMPT', '')
    
    profiler = ContextDNAProfiler()
    context = profiler.get_optimal_context(agent_type, task)
    
    # Write to manifest location
    manifest_dir = Path.home() / '.claude' / 'manifests'
    manifest_dir.mkdir(exist_ok=True)
    
    (manifest_dir / 'OPTIMAL_CONTEXT.json').write_text(
        json.dumps(context, indent=2)
    )
    
    print(f"[PRISM] Loaded {len(context)} context items for {agent_type}")
    print(f"[PRISM] Context size: {get_size_kb(context)}KB")

if __name__ == "__main__":
    load_optimal_context()
```

---

## ⚡ Component 2: Smart Manifest Cache

### **What It Does**
Maintains always-current manifests that update in real-time as code changes.

### **Implementation: `git-intelligence/src/manifest_cache.py`**

```python
import hashlib
from datetime import datetime
from typing import Dict, Optional
import json

class SmartManifestCache:
    """Intelligent caching with automatic invalidation"""
    
    def __init__(self):
        self.cache_dir = Path.home() / '.claude' / 'manifests' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.dependency_graph = {}
        
    def get_or_generate(self, manifest_type: str) -> Dict:
        """Get cached manifest or generate new one"""
        cache_file = self.cache_dir / f"{manifest_type}.json"
        
        # Check if cache is valid
        if self.is_cache_valid(manifest_type):
            return json.loads(cache_file.read_text())
            
        # Generate new manifest
        manifest = self.generate_manifest(manifest_type)
        
        # Cache with metadata
        cache_data = {
            'generated_at': datetime.now().isoformat(),
            'file_hashes': self.get_relevant_file_hashes(manifest_type),
            'data': manifest
        }
        
        cache_file.write_text(json.dumps(cache_data, indent=2))
        return manifest
        
    def is_cache_valid(self, manifest_type: str) -> bool:
        """Check if cached manifest is still valid"""
        cache_file = self.cache_dir / f"{manifest_type}.json"
        
        if not cache_file.exists():
            return False
            
        cache_data = json.loads(cache_file.read_text())
        current_hashes = self.get_relevant_file_hashes(manifest_type)
        
        # Invalid if any file changed
        return cache_data['file_hashes'] == current_hashes
```

---

## 🔄 Component 3: Change Intelligence Watcher

### **What It Does**
Watches for code changes and intelligently updates only affected manifests.

### **Implementation: `core/hooks/manifest-watcher.py`**

```python
#!/usr/bin/env python3
"""Watch for changes and update manifests intelligently"""

import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ManifestUpdateHandler(FileSystemEventHandler):
    def __init__(self):
        self.manifest_updater = ManifestUpdater()
        self.debounce_timer = {}
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Debounce rapid changes
        file_path = event.src_path
        current_time = time.time()
        
        if file_path in self.debounce_timer:
            if current_time - self.debounce_timer[file_path] < 2:
                return
                
        self.debounce_timer[file_path] = current_time
        
        # Determine which manifests need updating
        affected_manifests = self.get_affected_manifests(file_path)
        
        for manifest in affected_manifests:
            print(f"[PRISM] Updating {manifest} due to change in {file_path}")
            self.manifest_updater.update_manifest(manifest)
            
    def get_affected_manifests(self, file_path: str) -> List[str]:
        """Determine which manifests are affected by this file change"""
        affected = []
        
        if file_path.endswith('.tsx') or file_path.endswith('.jsx'):
            affected.append('COMPONENT_MANIFEST')
            affected.append('UI_PATTERNS')
            
        if file_path.endswith('.py'):
            affected.append('FUNCTION_REGISTRY')
            affected.append('API_SURFACE')
            
        if 'model' in file_path or 'schema' in file_path:
            affected.append('DATABASE_SCHEMA')
            affected.append('TYPE_DEFINITIONS')
            
        return affected

def start_watcher():
    """Start watching for file changes"""
    event_handler = ManifestUpdateHandler()
    observer = Observer()
    
    # Watch project directory
    project_root = os.getcwd()
    observer.schedule(event_handler, project_root, recursive=True)
    
    observer.start()
    print(f"[PRISM] Manifest watcher started for {project_root}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
```

---

## 📝 Component 4: Auto Documentation Syncer

### **What It Does**
Keeps documentation perfectly synchronized with code changes.

### **Implementation: `git-intelligence/src/doc_syncer.py`**

```python
class AutoDocSyncer:
    """Automatically sync documentation with code changes"""
    
    def __init__(self):
        self.doc_templates = self.load_templates()
        self.changelog = []
        
    def on_code_change(self, file_path: str, change_type: str):
        """Handle code change and update docs"""
        
        # Detect what changed
        change_analysis = self.analyze_change(file_path, change_type)
        
        # Update relevant documentation sections
        if change_analysis['api_changed']:
            self.update_api_docs(change_analysis)
            
        if change_analysis['component_added']:
            self.update_component_docs(change_analysis)
            
        if change_analysis['dependency_changed']:
            self.update_dependency_docs(change_analysis)
            
        # Add to changelog
        self.add_changelog_entry(change_analysis)
        
    def update_api_docs(self, change_analysis: Dict):
        """Update API documentation automatically"""
        api_doc_path = Path('docs/API.md')
        
        # Parse existing docs
        current_docs = api_doc_path.read_text()
        
        # Find and update relevant section
        updated_docs = self.smart_doc_update(
            current_docs,
            change_analysis['api_section'],
            change_analysis['new_api_spec']
        )
        
        api_doc_path.write_text(updated_docs)
        print(f"[PRISM] Updated API docs for {change_analysis['endpoint']}")
```

---

## 🎯 Integration Points

### **1. Hook Registration (`~/.claude/settings.json`)**

```json
{
  "hooks": {
    "pre-agent": [
      "python3 ~/.claude/hooks/context-dna-loader.py"
    ],
    "post-edit": [
      "python3 ~/.claude/hooks/manifest-updater.py"
    ],
    "on-startup": [
      "python3 ~/.claude/hooks/manifest-watcher.py &"
    ]
  }
}
```

### **2. Agent Integration**

Each agent gets a simple addition to their prompt:

```markdown
---
name: frontend-developer
tools: Read, Write, Edit
---

CONTEXT LOADING: Your optimal context has been pre-loaded at:
@.claude/manifests/OPTIMAL_CONTEXT.json

This contains only the manifests relevant to your task.
```

### **3. Command Integration**

New slash commands:

```markdown
/prism status     # Show context optimization stats
/prism profile    # View agent DNA profiles
/prism refresh    # Force manifest regeneration
/prism learn      # Update profiles from recent usage
```

---

## 📊 Expected Impact

### **Before PRISM:**
- Agents load 200KB+ of context (90% unused)
- Manifests go stale quickly
- Documentation drifts from code
- Context overload slows agents

### **After PRISM:**
- Agents load 20KB of laser-focused context
- Manifests auto-update in real-time
- Documentation stays perfectly synced
- Agents work 5x faster with better results

---

## 🚀 Implementation Timeline

### **Day 5 (Today):**
1. **Morning**: Build Context DNA Profiler
2. **Afternoon**: Implement Smart Manifest Cache
3. **Evening**: Test with frontend-developer agent

### **Day 6:**
1. **Morning**: Build Change Intelligence Watcher
2. **Afternoon**: Implement Auto Doc Syncer
3. **Evening**: Full system integration and testing

---

## 🎁 The Surprise Factor

**What makes PRISM magical:**

1. **It learns from you** - Every agent execution teaches it what context matters
2. **It's invisible** - Works entirely in the background
3. **It's predictive** - Knows what you'll need before you ask
4. **It's adaptive** - Gets smarter with every use

**The ultimate test:** After using PRISM for a week, agents will feel telepathic - they'll always have exactly what they need, never more, never less.

---

## 🔮 Future Vision

**PRISM 2.0** could include:
- Cross-project learning (learn from all your projects)
- Team intelligence sharing (learn from your team's patterns)
- Predictive context pre-loading (load tomorrow's context today)
- Natural language manifest queries ("show me all API endpoints that handle auth")

---

**Ready to build the future of codebase intelligence?**