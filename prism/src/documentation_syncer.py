#!/usr/bin/env python3
"""
Documentation Syncer - Part of PRISM

Automatically updates README sections, generates changelogs, and keeps API docs synchronized
when code changes. This ensures documentation never becomes stale.
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import subprocess
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class DocumentationChange:
    """Represents a documentation change to be made"""
    file_path: str
    section: str
    old_content: str
    new_content: str
    change_type: str  # 'update', 'add', 'remove'
    priority: int     # 1 = high, 2 = medium, 3 = low

class DocumentationSyncer:
    """Keeps documentation synchronized with code changes"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the documentation syncer"""
        self.project_root = project_root or Path.cwd()
        self.manifest_dir = self.project_root / '.claude' / 'manifests'
        
        # Documentation patterns to watch
        self.doc_patterns = {
            'readme': self.project_root / 'README.md',
            'api_docs': self.project_root / 'docs' / 'api.md',
            'changelog': self.project_root / 'CHANGELOG.md',
            'architecture': self.project_root / 'docs' / 'architecture.md'
        }
        
        # Section patterns for README updates
        self.readme_sections = {
            'api_endpoints': r'## API Endpoints.*?(?=##|\Z)',
            'components': r'## Components.*?(?=##|\Z)',
            'functions': r'## Functions.*?(?=##|\Z)',
            'installation': r'## Installation.*?(?=##|\Z)',
            'usage': r'## Usage.*?(?=##|\Z)'
        }
        
    def sync_readme_api_section(self) -> bool:
        """Update README API section based on API surface manifest"""
        try:
            print("[PRISM] Syncing README API section...")
            
            # Load API surface manifest
            api_manifest_path = self.manifest_dir / 'API_SURFACE.json'
            if not api_manifest_path.exists():
                print("[PRISM] No API surface manifest found, skipping README sync")
                return True
            
            with open(api_manifest_path) as f:
                api_data = json.load(f)
            
            # Generate API documentation
            api_section = self._generate_api_documentation(api_data)
            
            # Update README
            readme_path = self.doc_patterns['readme']
            if not readme_path.exists():
                print("[PRISM] README.md not found, creating basic structure...")
                self._create_basic_readme(api_section)
                return True
            
            # Read current README
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # Update or add API section
            updated_content = self._update_readme_section(
                readme_content, 
                'API Endpoints', 
                api_section
            )
            
            # Write back to file
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("[PRISM] ✅ README API section updated")
            return True
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to sync README API section: {e}")
            return False
    
    def sync_readme_components_section(self) -> bool:
        """Update README components section based on component manifest"""
        try:
            print("[PRISM] Syncing README components section...")
            
            # Load component manifest
            component_manifest_path = self.manifest_dir / 'COMPONENT_MANIFEST.json'
            if not component_manifest_path.exists():
                print("[PRISM] No component manifest found, skipping components sync")
                return True
            
            with open(component_manifest_path) as f:
                component_data = json.load(f)
            
            # Generate components documentation
            components_section = self._generate_components_documentation(component_data)
            
            # Update README
            readme_path = self.doc_patterns['readme']
            if not readme_path.exists():
                return True  # Skip if no README
            
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # Update components section
            updated_content = self._update_readme_section(
                readme_content, 
                'Components', 
                components_section
            )
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("[PRISM] ✅ README components section updated")
            return True
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to sync README components section: {e}")
            return False
    
    def generate_changelog_entry(self, changes: List[str], version: Optional[str] = None) -> bool:
        """Generate a changelog entry based on recent changes"""
        try:
            print("[PRISM] Generating changelog entry...")
            
            if not changes:
                print("[PRISM] No changes to document")
                return True
            
            # Determine version
            if not version:
                version = self._get_next_version()
            
            # Generate changelog entry
            entry = self._create_changelog_entry(changes, version)
            
            # Update CHANGELOG.md
            changelog_path = self.doc_patterns['changelog']
            
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Insert new entry after header
                if '# Changelog' in existing_content:
                    parts = existing_content.split('# Changelog', 1)
                    updated_content = f"# Changelog{parts[1].rstrip()}\n\n{entry}\n"
                else:
                    updated_content = f"# Changelog\n\n{entry}\n\n{existing_content}"
            else:
                updated_content = f"# Changelog\n\n{entry}\n"
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"[PRISM] ✅ Changelog entry for {version} created")
            return True
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to generate changelog entry: {e}")
            return False
    
    def sync_api_documentation(self) -> bool:
        """Generate detailed API documentation"""
        try:
            print("[PRISM] Syncing API documentation...")
            
            # Load API surface manifest
            api_manifest_path = self.manifest_dir / 'API_SURFACE.json'
            if not api_manifest_path.exists():
                print("[PRISM] No API surface manifest found")
                return True
            
            with open(api_manifest_path) as f:
                api_data = json.load(f)
            
            # Generate comprehensive API docs
            api_docs = self._generate_comprehensive_api_docs(api_data)
            
            # Ensure docs directory exists
            docs_dir = self.project_root / 'docs'
            docs_dir.mkdir(exist_ok=True)
            
            # Write API documentation
            api_docs_path = docs_dir / 'api.md'
            with open(api_docs_path, 'w', encoding='utf-8') as f:
                f.write(api_docs)
            
            print("[PRISM] ✅ API documentation generated")
            return True
            
        except Exception as e:
            print(f"[PRISM] ❌ Failed to sync API documentation: {e}")
            return False
    
    def detect_changes_from_git(self) -> List[str]:
        """Detect changes from git history for changelog generation"""
        try:
            # Get recent commits
            result = subprocess.run([
                'git', 'log', '--oneline', '--since="24 hours ago"'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return []
            
            # Parse commit messages
            commits = result.stdout.strip().split('\n')
            changes = []
            
            for commit in commits:
                if commit.strip():
                    # Extract meaningful changes from commit messages
                    commit_msg = commit.split(' ', 1)[1] if ' ' in commit else commit
                    
                    # Categorize changes
                    if any(word in commit_msg.lower() for word in ['feat:', 'feature:', 'add:']):
                        changes.append(f"✨ {commit_msg}")
                    elif any(word in commit_msg.lower() for word in ['fix:', 'bug:', 'patch:']):
                        changes.append(f"🐛 {commit_msg}")
                    elif any(word in commit_msg.lower() for word in ['docs:', 'doc:', 'readme:']):
                        changes.append(f"📚 {commit_msg}")
                    elif any(word in commit_msg.lower() for word in ['test:', 'spec:']):
                        changes.append(f"🧪 {commit_msg}")
                    else:
                        changes.append(f"🔧 {commit_msg}")
            
            return changes
            
        except Exception as e:
            print(f"[PRISM] Error detecting git changes: {e}")
            return []
    
    def _generate_api_documentation(self, api_data: Dict) -> str:
        """Generate API documentation from manifest data"""
        doc = "### API Endpoints\n\n"
        
        endpoints = api_data.get('endpoints', [])
        if not endpoints:
            return doc + "_No API endpoints defined._\n"
        
        # Group by path for better organization
        grouped_endpoints = {}
        for endpoint in endpoints:
            path = endpoint.get('path', '/')
            if path not in grouped_endpoints:
                grouped_endpoints[path] = []
            grouped_endpoints[path].append(endpoint)
        
        for path, path_endpoints in sorted(grouped_endpoints.items()):
            doc += f"#### `{path}`\n\n"
            
            for endpoint in path_endpoints:
                method = endpoint.get('method', 'GET')
                file_info = f"*Defined in {endpoint.get('file', 'unknown')}*"
                
                doc += f"- **{method}** {path} - {file_info}\n"
            
            doc += "\n"
        
        return doc
    
    def _generate_components_documentation(self, component_data: Dict) -> str:
        """Generate components documentation from manifest data"""
        doc = "### Components\n\n"
        
        components = component_data.get('components', [])
        if not components:
            return doc + "_No components defined._\n"
        
        for component in sorted(components, key=lambda x: x.get('name', '')):
            name = component.get('name', 'Unknown')
            comp_type = component.get('type', 'functional')
            file_info = f"*{component.get('file', 'unknown')}*"
            
            doc += f"- **{name}** ({comp_type}) - {file_info}\n"
        
        # Add hooks if available
        hooks = component_data.get('hooks', [])
        if hooks:
            doc += "\n#### Custom Hooks\n\n"
            for hook in sorted(hooks, key=lambda x: x.get('name', '')):
                name = hook.get('name', 'Unknown')
                file_info = f"*{hook.get('file', 'unknown')}*"
                doc += f"- **{name}** - {file_info}\n"
        
        return doc + "\n"
    
    def _update_readme_section(self, readme_content: str, section_name: str, new_content: str) -> str:
        """Update or add a section in README"""
        section_pattern = rf'(## {section_name}.*?)(?=##|\Z)'
        
        if re.search(section_pattern, readme_content, re.DOTALL):
            # Section exists, update it
            replacement = f"## {section_name}\n\n{new_content}"
            updated_content = re.sub(
                section_pattern, 
                replacement, 
                readme_content, 
                flags=re.DOTALL
            )
        else:
            # Section doesn't exist, add it before any existing sections or at end
            new_section = f"\n## {section_name}\n\n{new_content}\n"
            
            # Find where to insert (before first ## section or at end)
            first_section_match = re.search(r'\n## ', readme_content)
            if first_section_match:
                insert_pos = first_section_match.start()
                updated_content = readme_content[:insert_pos] + new_section + readme_content[insert_pos:]
            else:
                updated_content = readme_content.rstrip() + new_section
        
        return updated_content
    
    def _create_basic_readme(self, api_section: str):
        """Create a basic README structure"""
        readme_content = f"""# {self.project_root.name}

## Overview

_Project description goes here._

## Installation

```bash
# Installation instructions
```

## Usage

```bash
# Usage examples
```

## {api_section}

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

_License information goes here._
"""
        
        with open(self.doc_patterns['readme'], 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_changelog_entry(self, changes: List[str], version: str) -> str:
        """Create a formatted changelog entry"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        entry = f"## [{version}] - {date_str}\n\n"
        
        # Group changes by type
        features = [c for c in changes if c.startswith('✨')]
        fixes = [c for c in changes if c.startswith('🐛')]
        docs = [c for c in changes if c.startswith('📚')]
        tests = [c for c in changes if c.startswith('🧪')]
        other = [c for c in changes if not any(c.startswith(prefix) for prefix in ['✨', '🐛', '📚', '🧪'])]
        
        if features:
            entry += "### ✨ Features\n"
            for change in features:
                entry += f"- {change[2:].strip()}\n"  # Remove emoji prefix
            entry += "\n"
        
        if fixes:
            entry += "### 🐛 Bug Fixes\n"
            for change in fixes:
                entry += f"- {change[2:].strip()}\n"
            entry += "\n"
        
        if docs:
            entry += "### 📚 Documentation\n"
            for change in docs:
                entry += f"- {change[2:].strip()}\n"
            entry += "\n"
        
        if tests:
            entry += "### 🧪 Tests\n"
            for change in tests:
                entry += f"- {change[2:].strip()}\n"
            entry += "\n"
        
        if other:
            entry += "### 🔧 Other Changes\n"
            for change in other:
                clean_change = change[2:].strip() if change.startswith('🔧') else change.strip()
                entry += f"- {clean_change}\n"
            entry += "\n"
        
        return entry.rstrip()
    
    def _get_next_version(self) -> str:
        """Determine the next version number"""
        try:
            # Try to get version from git tags
            result = subprocess.run([
                'git', 'describe', '--tags', '--abbrev=0'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                last_tag = result.stdout.strip()
                # Simple version increment (assumes semantic versioning)
                if re.match(r'^v?\d+\.\d+\.\d+$', last_tag):
                    version_part = last_tag.lstrip('v')
                    major, minor, patch = map(int, version_part.split('.'))
                    return f"v{major}.{minor}.{patch + 1}"
            
            # Fallback to package.json or default
            package_json = self.project_root / 'package.json'
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    return f"v{data.get('version', '0.1.0')}"
            
            return "v0.1.0"
            
        except Exception:
            return "v0.1.0"
    
    def _generate_comprehensive_api_docs(self, api_data: Dict) -> str:
        """Generate comprehensive API documentation"""
        doc = f"""# API Documentation

*Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

This document describes the API endpoints available in this application.

## Endpoints

"""
        
        endpoints = api_data.get('endpoints', [])
        if not endpoints:
            doc += "_No API endpoints are currently defined._\n"
            return doc
        
        # Sort endpoints by path and method
        sorted_endpoints = sorted(endpoints, key=lambda x: (x.get('path', '/'), x.get('method', 'GET')))
        
        for endpoint in sorted_endpoints:
            path = endpoint.get('path', '/')
            method = endpoint.get('method', 'GET')
            file_path = endpoint.get('file', 'unknown')
            line_num = endpoint.get('line', 0)
            
            doc += f"### {method} {path}\n\n"
            doc += f"**Source**: `{file_path}:{line_num}`\n\n"
            doc += "**Description**: _Add description here_\n\n"
            
            # Add example request/response if this were a full implementation
            doc += "**Example Request**:\n```bash\n"
            doc += f"curl -X {method} http://localhost:3000{path}\n```\n\n"
            doc += "**Example Response**:\n```json\n{\n  \"status\": \"success\"\n}\n```\n\n"
            doc += "---\n\n"
        
        # Add functions documentation
        functions = api_data.get('functions', [])
        if functions:
            doc += "## Functions\n\n"
            doc += "The following functions are available in the API:\n\n"
            
            for func in sorted(functions, key=lambda x: x.get('name', '')):
                name = func.get('name', 'unknown')
                file_path = func.get('file', 'unknown')
                line_num = func.get('line', 0)
                signature = func.get('signature', '')
                
                doc += f"### `{name}`\n\n"
                doc += f"**Source**: `{file_path}:{line_num}`\n\n"
                if signature:
                    doc += f"**Signature**:\n```python\n{signature}\n```\n\n"
                doc += "---\n\n"
        
        return doc

def main():
    """Main entry point for documentation syncer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PRISM Documentation Syncer')
    parser.add_argument('--sync-readme', action='store_true', help='Sync README sections')
    parser.add_argument('--sync-api-docs', action='store_true', help='Generate API documentation')
    parser.add_argument('--generate-changelog', action='store_true', help='Generate changelog entry from git')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    syncer = DocumentationSyncer(project_root)
    
    success = True
    
    if args.sync_readme:
        success &= syncer.sync_readme_api_section()
        success &= syncer.sync_readme_components_section()
    
    if args.sync_api_docs:
        success &= syncer.sync_api_documentation()
    
    if args.generate_changelog:
        changes = syncer.detect_changes_from_git()
        if changes:
            success &= syncer.generate_changelog_entry(changes)
        else:
            print("[PRISM] No recent changes found for changelog")
    
    if not any([args.sync_readme, args.sync_api_docs, args.generate_changelog]):
        print("Specify at least one sync option:")
        print("  --sync-readme      Update README sections")
        print("  --sync-api-docs    Generate API documentation")
        print("  --generate-changelog Generate changelog from git history")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()