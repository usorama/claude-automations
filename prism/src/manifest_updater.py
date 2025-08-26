#!/usr/bin/env python3
"""
Real-time Manifest Updater - Part of PRISM

Monitors file changes in the project and updates affected manifests incrementally.
This ensures manifests stay fresh as code changes without regenerating everything.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
import hashlib
import subprocess
from dataclasses import dataclass
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

@dataclass
class ManifestDependency:
    """Represents a dependency between a file and manifests that need updating"""
    file_path: str
    manifest_types: List[str]
    update_priority: int  # 1 = high, 2 = medium, 3 = low
    analysis_depth: str   # 'shallow', 'medium', 'deep'

class ManifestUpdater:
    """Real-time manifest updater that keeps manifests synchronized with code changes"""
    
    def __init__(self, project_root: Optional[Path] = None, manifest_dir: Optional[Path] = None):
        """Initialize the manifest updater"""
        self.project_root = project_root or Path.cwd()
        self.manifest_dir = manifest_dir or (self.project_root / '.claude' / 'manifests')
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        
        # Dependency mappings: file patterns -> manifest types
        self.dependency_map = self._build_dependency_map()
        
        # Cache for avoiding unnecessary updates
        self.file_hashes = {}
        self.last_update_times = {}
        
        # Update queue for batching changes
        self.update_queue: Set[str] = set()
        self.batch_timeout = 2  # seconds to wait before processing batch
        
    def _build_dependency_map(self) -> Dict[str, ManifestDependency]:
        """Build the mapping between file patterns and manifest types"""
        return {
            # API-related files
            '**/*api*.py': ManifestDependency('api', ['API_SURFACE', 'FUNCTION_REGISTRY'], 1, 'deep'),
            '**/*route*.py': ManifestDependency('routes', ['API_SURFACE', 'FUNCTION_REGISTRY'], 1, 'deep'),
            '**/*endpoint*.py': ManifestDependency('endpoints', ['API_SURFACE', 'FUNCTION_REGISTRY'], 1, 'deep'),
            '**/routes/**/*.py': ManifestDependency('routes', ['API_SURFACE', 'FUNCTION_REGISTRY'], 1, 'deep'),
            
            # Frontend/Component files
            '**/*.tsx': ManifestDependency('components', ['COMPONENT_MANIFEST', 'UI_PATTERNS'], 1, 'medium'),
            '**/*.jsx': ManifestDependency('components', ['COMPONENT_MANIFEST', 'UI_PATTERNS'], 1, 'medium'),
            '**/components/**/*': ManifestDependency('components', ['COMPONENT_MANIFEST', 'UI_PATTERNS'], 1, 'medium'),
            
            # Database files
            '**/*model*.py': ManifestDependency('models', ['DATABASE_SCHEMA', 'FUNCTION_REGISTRY'], 1, 'deep'),
            '**/*migration*.py': ManifestDependency('migrations', ['DATABASE_SCHEMA'], 1, 'shallow'),
            '**/migrations/**/*': ManifestDependency('migrations', ['DATABASE_SCHEMA'], 1, 'shallow'),
            '**/models/**/*.py': ManifestDependency('models', ['DATABASE_SCHEMA', 'FUNCTION_REGISTRY'], 1, 'deep'),
            
            # Configuration files
            'package.json': ManifestDependency('config', ['TECH_STACK', 'DEPENDENCIES'], 1, 'deep'),
            'pyproject.toml': ManifestDependency('config', ['TECH_STACK', 'DEPENDENCIES'], 1, 'deep'),
            'requirements.txt': ManifestDependency('config', ['DEPENDENCIES'], 2, 'shallow'),
            'Dockerfile': ManifestDependency('config', ['DEPLOYMENT_CONFIG'], 2, 'medium'),
            
            # Test files
            '**/*test*.py': ManifestDependency('tests', ['TEST_MANIFEST'], 2, 'medium'),
            '**/*spec*.py': ManifestDependency('tests', ['TEST_MANIFEST'], 2, 'medium'),
            '**/tests/**/*': ManifestDependency('tests', ['TEST_MANIFEST'], 2, 'medium'),
            
            # Documentation
            '**/*.md': ManifestDependency('docs', ['PROJECT_CONTEXT'], 3, 'shallow'),
            'README.md': ManifestDependency('readme', ['PROJECT_CONTEXT', 'CODEBASE_MANIFEST'], 2, 'medium'),
            
            # General Python files
            '**/*.py': ManifestDependency('python', ['FUNCTION_REGISTRY', 'CODEBASE_MANIFEST'], 2, 'medium'),
        }
    
    def get_affected_manifests(self, file_path: str) -> List[ManifestDependency]:
        """Determine which manifests need updating for a given file"""
        file_path = str(Path(file_path).relative_to(self.project_root))
        affected = []
        
        for pattern, dependency in self.dependency_map.items():
            if Path(file_path).match(pattern):
                affected.append(dependency)
        
        # Sort by priority (lower number = higher priority)
        affected.sort(key=lambda x: x.update_priority)
        return affected
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content for change detection"""
        try:
            if not file_path.exists():
                return ""
            
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def has_file_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last update"""
        current_hash = self.get_file_hash(file_path)
        previous_hash = self.file_hashes.get(str(file_path), "")
        
        if current_hash != previous_hash:
            self.file_hashes[str(file_path)] = current_hash
            return True
        return False
    
    def update_api_surface_manifest(self, changed_files: List[str]) -> bool:
        """Update API surface manifest based on changed files"""
        try:
            print(f"[PRISM] Updating API surface manifest...")
            
            # Extract API information from changed files
            api_data = {
                'endpoints': [],
                'functions': [],
                'classes': [],
                'last_updated': datetime.now().isoformat()
            }
            
            for file_path in changed_files:
                if file_path.endswith('.py'):
                    # Parse Python files for API information
                    api_info = self._extract_python_api_info(file_path)
                    api_data['endpoints'].extend(api_info.get('endpoints', []))
                    api_data['functions'].extend(api_info.get('functions', []))
                    api_data['classes'].extend(api_info.get('classes', []))
            
            # Write updated manifest
            manifest_path = self.manifest_dir / 'API_SURFACE.json'
            
            # Merge with existing data if it exists
            if manifest_path.exists():
                try:
                    existing_data = json.loads(manifest_path.read_text())
                    # Keep existing entries, add new ones
                    existing_endpoints = {ep.get('path', ep.get('name', '')): ep for ep in existing_data.get('endpoints', [])}
                    existing_functions = {fn.get('name', ''): fn for fn in existing_data.get('functions', [])}
                    existing_classes = {cls.get('name', ''): cls for cls in existing_data.get('classes', [])}
                    
                    # Update with new data
                    for ep in api_data['endpoints']:
                        key = ep.get('path', ep.get('name', ''))
                        existing_endpoints[key] = ep
                    
                    for fn in api_data['functions']:
                        key = fn.get('name', '')
                        existing_functions[key] = fn
                    
                    for cls in api_data['classes']:
                        key = cls.get('name', '')
                        existing_classes[key] = cls
                    
                    api_data['endpoints'] = list(existing_endpoints.values())
                    api_data['functions'] = list(existing_functions.values())
                    api_data['classes'] = list(existing_classes.values())
                except Exception:
                    pass  # Use new data if merging fails
            
            manifest_path.write_text(json.dumps(api_data, indent=2))
            print(f"[PRISM] ✅ API surface manifest updated")
            return True
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to update API surface manifest: {e}")
            return False
    
    def update_component_manifest(self, changed_files: List[str]) -> bool:
        """Update component manifest based on changed frontend files"""
        try:
            print(f"[PRISM] Updating component manifest...")
            
            component_data = {
                'components': [],
                'hooks': [],
                'utilities': [],
                'last_updated': datetime.now().isoformat()
            }
            
            for file_path in changed_files:
                if file_path.endswith(('.tsx', '.jsx', '.ts', '.js')):
                    # Parse React/JS files for component information
                    component_info = self._extract_component_info(file_path)
                    component_data['components'].extend(component_info.get('components', []))
                    component_data['hooks'].extend(component_info.get('hooks', []))
                    component_data['utilities'].extend(component_info.get('utilities', []))
            
            # Write updated manifest
            manifest_path = self.manifest_dir / 'COMPONENT_MANIFEST.json'
            
            # Merge with existing data
            if manifest_path.exists():
                try:
                    existing_data = json.loads(manifest_path.read_text())
                    
                    # Create maps for merging
                    existing_components = {comp.get('name', ''): comp for comp in existing_data.get('components', [])}
                    existing_hooks = {hook.get('name', ''): hook for hook in existing_data.get('hooks', [])}
                    existing_utils = {util.get('name', ''): util for util in existing_data.get('utilities', [])}
                    
                    # Update with new data
                    for comp in component_data['components']:
                        key = comp.get('name', '')
                        existing_components[key] = comp
                    
                    for hook in component_data['hooks']:
                        key = hook.get('name', '')
                        existing_hooks[key] = hook
                    
                    for util in component_data['utilities']:
                        key = util.get('name', '')
                        existing_utils[key] = util
                    
                    component_data['components'] = list(existing_components.values())
                    component_data['hooks'] = list(existing_hooks.values())
                    component_data['utilities'] = list(existing_utils.values())
                except Exception:
                    pass
            
            manifest_path.write_text(json.dumps(component_data, indent=2))
            print(f"[PRISM] ✅ Component manifest updated")
            return True
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to update component manifest: {e}")
            return False
    
    def update_function_registry(self, changed_files: List[str]) -> bool:
        """Update function registry based on changed files"""
        try:
            print(f"[PRISM] Updating function registry...")
            
            functions_data = []
            
            for file_path in changed_files:
                if file_path.endswith('.py'):
                    # Parse Python files for functions
                    functions_info = self._extract_python_functions(file_path)
                    functions_data.extend(functions_info)
            
            if not functions_data:
                return True  # No functions to update
            
            # Write updated manifest
            manifest_path = self.manifest_dir / 'FUNCTION_REGISTRY.md'
            
            # Create markdown content
            md_content = f"""# Function Registry
Last updated: {datetime.now().isoformat()}

## Recently Updated Functions

"""
            
            for func in functions_data:
                md_content += f"""### {func.get('name', 'Unknown')}
**File**: `{func.get('file', 'Unknown')}`  
**Line**: {func.get('line', 0)}  
**Args**: {func.get('args', [])}  
**Description**: {func.get('description', 'No description')}

```python
{func.get('signature', '')}
```

---

"""
            
            # Merge with existing content if needed
            if manifest_path.exists():
                # For simplicity, just append new functions
                existing_content = manifest_path.read_text()
                if "## Recently Updated Functions" in existing_content:
                    # Replace the recent section
                    parts = existing_content.split("## Recently Updated Functions")
                    md_content = parts[0] + md_content[md_content.find("## Recently Updated Functions"):]
            
            manifest_path.write_text(md_content)
            print(f"[PRISM] ✅ Function registry updated")
            return True
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to update function registry: {e}")
            return False
    
    def _extract_python_api_info(self, file_path: str) -> Dict[str, List[Dict]]:
        """Extract API information from Python files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            api_info = {
                'endpoints': [],
                'functions': [],
                'classes': []
            }
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                # Look for Flask/FastAPI route decorators
                if '@app.route' in line or '@router.' in line or '@api.' in line:
                    endpoint_info = {
                        'path': self._extract_route_path(line),
                        'method': self._extract_route_method(line),
                        'file': file_path,
                        'line': i + 1
                    }
                    api_info['endpoints'].append(endpoint_info)
                
                # Look for function definitions
                elif line.strip().startswith('def '):
                    func_name = line.split('def ')[1].split('(')[0]
                    func_info = {
                        'name': func_name,
                        'file': file_path,
                        'line': i + 1,
                        'signature': line.strip()
                    }
                    api_info['functions'].append(func_info)
                
                # Look for class definitions
                elif line.strip().startswith('class '):
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0]
                    class_info = {
                        'name': class_name,
                        'file': file_path,
                        'line': i + 1
                    }
                    api_info['classes'].append(class_info)
            
            return api_info
            
        except Exception as e:
            print(f"[PRISM] Error parsing {file_path}: {e}")
            return {'endpoints': [], 'functions': [], 'classes': []}
    
    def _extract_component_info(self, file_path: str) -> Dict[str, List[Dict]]:
        """Extract component information from React/JS files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            component_info = {
                'components': [],
                'hooks': [],
                'utilities': []
            }
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                # Look for React components
                if 'export const ' in line and ('= () =>' in line or '= (props)' in line):
                    comp_name = line.split('export const ')[1].split(' =')[0]
                    component_info['components'].append({
                        'name': comp_name,
                        'type': 'functional',
                        'file': file_path,
                        'line': i + 1
                    })
                
                # Look for custom hooks
                elif line.strip().startswith('const use') and '= (' in line:
                    hook_name = line.split('const ')[1].split(' =')[0]
                    component_info['hooks'].append({
                        'name': hook_name,
                        'file': file_path,
                        'line': i + 1
                    })
            
            return component_info
            
        except Exception as e:
            print(f"[PRISM] Error parsing {file_path}: {e}")
            return {'components': [], 'hooks': [], 'utilities': []}
    
    def _extract_python_functions(self, file_path: str) -> List[Dict]:
        """Extract function information from Python files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    func_line = line.strip()
                    func_name = func_line.split('def ')[1].split('(')[0]
                    
                    # Extract arguments
                    args_part = func_line[func_line.find('(') + 1:func_line.rfind(')')]
                    args = [arg.strip().split(':')[0].split('=')[0] for arg in args_part.split(',') if arg.strip()]
                    
                    # Look for docstring
                    description = "No description"
                    if i + 1 < len(lines) and '"""' in lines[i + 1]:
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if '"""' in lines[j]:
                                desc_line = lines[j].replace('"""', '').strip()
                                if desc_line:
                                    description = desc_line
                                break
                    
                    functions.append({
                        'name': func_name,
                        'file': file_path,
                        'line': i + 1,
                        'args': args,
                        'signature': func_line,
                        'description': description
                    })
            
            return functions
            
        except Exception as e:
            print(f"[PRISM] Error extracting functions from {file_path}: {e}")
            return []
    
    def _extract_route_path(self, line: str) -> str:
        """Extract route path from decorator line"""
        if "'" in line:
            return line.split("'")[1]
        elif '"' in line:
            return line.split('"')[1]
        return "/"
    
    def _extract_route_method(self, line: str) -> str:
        """Extract HTTP method from route decorator"""
        if 'methods=' in line:
            methods_part = line.split('methods=')[1].split(']')[0]
            return methods_part.replace('[', '').replace("'", '').replace('"', '').strip()
        elif 'POST' in line.upper():
            return 'POST'
        elif 'PUT' in line.upper():
            return 'PUT'
        elif 'DELETE' in line.upper():
            return 'DELETE'
        else:
            return 'GET'
    
    def process_file_change(self, file_path: str) -> bool:
        """Process a single file change"""
        try:
            file_path_obj = Path(file_path)
            
            # Skip non-relevant files
            if (file_path_obj.suffix in ['.pyc', '.log', '.tmp'] or 
                '.git' in file_path or 
                '__pycache__' in file_path or
                'node_modules' in file_path):
                return True
            
            # Check if file actually changed
            if not self.has_file_changed(file_path_obj):
                return True
            
            print(f"[PRISM] Processing file change: {file_path}")
            
            # Get affected manifests
            affected_manifests = self.get_affected_manifests(file_path)
            
            if not affected_manifests:
                return True  # No manifests affected
            
            # Update each affected manifest type
            success = True
            
            for dependency in affected_manifests:
                for manifest_type in dependency.manifest_types:
                    if manifest_type == 'API_SURFACE':
                        success &= self.update_api_surface_manifest([file_path])
                    elif manifest_type == 'COMPONENT_MANIFEST':
                        success &= self.update_component_manifest([file_path])
                    elif manifest_type == 'FUNCTION_REGISTRY':
                        success &= self.update_function_registry([file_path])
                    # Add more manifest types as needed
            
            # Update last update time
            self.last_update_times[file_path] = datetime.now().isoformat()
            
            return success
            
        except Exception as e:
            print(f"[PRISM] Error processing file change {file_path}: {e}")
            return False
    
    def start_watching(self):
        """Start watching for file changes"""
        print(f"[PRISM] Starting file watcher for {self.project_root}")
        
        class ChangeHandler(FileSystemEventHandler):
            def __init__(self, updater):
                self.updater = updater
            
            def on_modified(self, event):
                if not event.is_directory:
                    self.updater.add_to_queue(event.src_path)
            
            def on_created(self, event):
                if not event.is_directory:
                    self.updater.add_to_queue(event.src_path)
        
        event_handler = ChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.project_root), recursive=True)
        observer.start()
        
        print(f"[PRISM] File watcher started. Manifest updates will happen within {self.batch_timeout} seconds of changes.")
        
        try:
            while True:
                time.sleep(1)
                self.process_queue()
        except KeyboardInterrupt:
            observer.stop()
            print("[PRISM] File watcher stopped")
        
        observer.join()
    
    def add_to_queue(self, file_path: str):
        """Add file to update queue"""
        self.update_queue.add(file_path)
    
    def process_queue(self):
        """Process queued file updates"""
        if not self.update_queue:
            return
        
        # Wait for batch timeout to collect more changes
        time.sleep(self.batch_timeout)
        
        if self.update_queue:
            files_to_process = list(self.update_queue)
            self.update_queue.clear()
            
            print(f"[PRISM] Processing batch of {len(files_to_process)} file changes")
            
            for file_path in files_to_process:
                self.process_file_change(file_path)

def main():
    """Main entry point for manifest updater"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PRISM Real-time Manifest Updater')
    parser.add_argument('--watch', action='store_true', help='Start file watcher mode')
    parser.add_argument('--update', help='Update manifests for specific file')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    updater = ManifestUpdater(project_root)
    
    if args.watch:
        updater.start_watching()
    elif args.update:
        success = updater.process_file_change(args.update)
        sys.exit(0 if success else 1)
    else:
        print("Use --watch to start file watcher or --update <file> to update specific file")
        print("Example: python manifest_updater.py --watch")

if __name__ == '__main__':
    main()