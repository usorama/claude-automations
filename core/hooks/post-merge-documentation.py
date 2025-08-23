#!/usr/bin/env python3
"""
Post-Merge Documentation Automation Hook
Automatically updates project documentation after successful PR merges
"""

import subprocess
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import re

# Configuration
DOCS_CONFIG = {
    'roadmap_file': 'PROJECT_ROADMAP.md',
    'decisions_file': 'DECISIONS.md',
    'changelog_file': 'CHANGELOG.md',
    'readme_file': 'README.md',
    'api_docs_dir': 'docs/api',
    'user_docs_dir': 'docs/user',
    'dev_docs_dir': 'docs/dev'
}

class DocumentationAutomator:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path).resolve()
        self.claude_dir = self.project_path / '.claude'
        self.docs_dir = self.project_path / 'docs'
        self.template_dir = Path.home() / '.claude' / 'process-templates-n-prompts' / 'documentation'
        
    def get_recent_commits(self, since_hours=24):
        """Get recent commits that might need documentation updates"""
        try:
            # Get commits from the last 24 hours
            since_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            since_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
            
            result = subprocess.run([
                'git', 'log', 
                f'--since={since_str}',
                '--pretty=format:%H|%s|%an|%ad',
                '--date=iso'
            ], capture_output=True, text=True, cwd=self.project_path)
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1],
                            'author': parts[2],
                            'date': parts[3]
                        })
            return commits
            
        except Exception as e:
            print(f"Error getting recent commits: {e}")
            return []
    
    def analyze_commit_for_doc_needs(self, commit):
        """Analyze commit to determine what documentation needs updating"""
        message = commit['message'].lower()
        
        # Categorize commit types that need documentation
        doc_needs = {
            'roadmap': False,
            'api_docs': False,
            'user_guide': False,
            'changelog': False,
            'readme': False,
            'decisions': False,
            'deployment': False
        }
        
        # Feature commits need multiple documentation updates
        if re.search(r'\b(feat|feature|add|new)\b', message):
            doc_needs['roadmap'] = True
            doc_needs['changelog'] = True
            doc_needs['readme'] = True
            
            # API-related features
            if re.search(r'\b(api|endpoint|route|graphql)\b', message):
                doc_needs['api_docs'] = True
            
            # User-facing features
            if re.search(r'\b(ui|ux|user|interface|frontend)\b', message):
                doc_needs['user_guide'] = True
        
        # Breaking changes need special attention
        if re.search(r'\b(break|breaking|major)\b', message):
            doc_needs['api_docs'] = True
            doc_needs['changelog'] = True
            doc_needs['user_guide'] = True
        
        # Architecture/design decisions
        if re.search(r'\b(architect|design|refactor|restructure)\b', message):
            doc_needs['decisions'] = True
            doc_needs['roadmap'] = True
        
        # Deployment/infrastructure changes
        if re.search(r'\b(deploy|docker|ci|cd|infra|config)\b', message):
            doc_needs['deployment'] = True
        
        # Bug fixes might need changelog
        if re.search(r'\b(fix|bug|issue|patch)\b', message):
            doc_needs['changelog'] = True
        
        return doc_needs
    
    def update_roadmap(self, commits):
        """Update project roadmap based on recent progress"""
        roadmap_file = self.project_path / DOCS_CONFIG['roadmap_file']
        
        # Create roadmap if it doesn't exist
        if not roadmap_file.exists():
            self.create_initial_roadmap(roadmap_file)
        
        # Analyze completed work
        completed_features = []
        for commit in commits:
            if re.search(r'\b(feat|feature|complete|done|implement)\b', commit['message'].lower()):
                completed_features.append({
                    'title': commit['message'],
                    'date': commit['date'],
                    'hash': commit['hash'][:7]
                })
        
        if completed_features:
            self.append_to_roadmap(roadmap_file, completed_features)
            print(f"✅ Updated roadmap with {len(completed_features)} completed features")
    
    def create_initial_roadmap(self, roadmap_file):
        """Create initial project roadmap structure"""
        template = f"""# Project Roadmap

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview
This roadmap tracks the evolution of our project from inception to deployment and operation.

## Completed Milestones

### 🎯 Foundation Phase
- [x] Project initialization
- [x] Core architecture design
- [x] Development environment setup

## Current Sprint

### 🚀 In Progress
- [ ] Feature development
- [ ] Testing and quality assurance
- [ ] Documentation updates

## Upcoming Milestones

### 📋 Planned Features
- [ ] Feature A - Enhance user experience
- [ ] Feature B - Performance optimization
- [ ] Feature C - Security improvements

### 🔮 Future Vision
- [ ] Advanced analytics
- [ ] Mobile application
- [ ] API marketplace integration

## Recent Changes

*Automatically updated based on commit history*

"""
        roadmap_file.write_text(template)
    
    def append_to_roadmap(self, roadmap_file, completed_features):
        """Append completed features to roadmap"""
        content = roadmap_file.read_text()
        
        # Find the "Recent Changes" section
        recent_section = "## Recent Changes"
        if recent_section in content:
            # Insert new completed features
            new_entries = "\n"
            for feature in completed_features:
                new_entries += f"- [{feature['date'][:10]}] {feature['title']} (`{feature['hash']}`)\n"
            
            content = content.replace(
                recent_section + "\n\n*Automatically updated based on commit history*",
                recent_section + new_entries + "\n*Automatically updated based on commit history*"
            )
            
            roadmap_file.write_text(content)
    
    def update_decisions_log(self, commits):
        """Update architectural decisions log"""
        decisions_file = self.project_path / DOCS_CONFIG['decisions_file']
        
        # Find architecture/design related commits
        design_commits = []
        for commit in commits:
            if re.search(r'\b(architect|design|refactor|restructure|decision|pattern)\b', commit['message'].lower()):
                design_commits.append(commit)
        
        if not design_commits:
            return
        
        # Create decisions file if it doesn't exist
        if not decisions_file.exists():
            self.create_initial_decisions_log(decisions_file)
        
        # Add new decisions
        for commit in design_commits:
            self.add_decision_entry(decisions_file, commit)
        
        print(f"✅ Updated decisions log with {len(design_commits)} architectural changes")
    
    def create_initial_decisions_log(self, decisions_file):
        """Create initial architectural decisions log"""
        template = f"""# Architectural Decision Record (ADR)

*Automatically maintained based on development activity*

## Format
Each decision follows this structure:
- **Date**: When the decision was made
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: What circumstances led to this decision
- **Decision**: What we decided to do
- **Consequences**: What becomes easier or more difficult

---

## Decisions

*Decisions are automatically extracted from commit messages containing architectural keywords*

"""
        decisions_file.write_text(template)
    
    def add_decision_entry(self, decisions_file, commit):
        """Add a decision entry to the log"""
        content = decisions_file.read_text()
        
        # Create decision entry
        entry = f"""
### ADR-{commit['hash'][:7]}: {commit['message']}

- **Date**: {commit['date'][:10]}
- **Status**: Implemented
- **Context**: Development activity requiring architectural consideration
- **Decision**: {commit['message']}
- **Commit**: `{commit['hash'][:7]}`
- **Author**: {commit['author']}

*Note: This decision was automatically extracted. Consider expanding with more context.*

---
"""
        
        # Insert before the end of the file
        content = content.replace("*Decisions are automatically extracted from commit messages containing architectural keywords*", 
                                  "*Decisions are automatically extracted from commit messages containing architectural keywords*" + entry)
        
        decisions_file.write_text(content)
    
    def update_changelog(self, commits):
        """Update CHANGELOG.md with recent changes"""
        changelog_file = self.project_path / DOCS_CONFIG['changelog_file']
        
        if not changelog_file.exists():
            self.create_initial_changelog(changelog_file)
        
        # Group commits by type
        changes = {
            'features': [],
            'fixes': [],
            'breaking': [],
            'other': []
        }
        
        for commit in commits:
            msg = commit['message'].lower()
            if re.search(r'\b(break|breaking)\b', msg):
                changes['breaking'].append(commit)
            elif re.search(r'\b(feat|feature|add|new)\b', msg):
                changes['features'].append(commit)
            elif re.search(r'\b(fix|bug|patch)\b', msg):
                changes['fixes'].append(commit)
            else:
                changes['other'].append(commit)
        
        if any(changes.values()):
            self.add_changelog_entry(changelog_file, changes)
            print(f"✅ Updated changelog with recent changes")
    
    def create_initial_changelog(self, changelog_file):
        """Create initial changelog structure"""
        template = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup

---

*This changelog is automatically updated based on commit activity*
"""
        changelog_file.write_text(template)
    
    def add_changelog_entry(self, changelog_file, changes):
        """Add new entry to changelog"""
        content = changelog_file.read_text()
        
        today = datetime.now().strftime('%Y-%m-%d')
        entry = f"\n## [{today}] - Development Update\n"
        
        if changes['breaking']:
            entry += "\n### ⚠️ Breaking Changes\n"
            for commit in changes['breaking']:
                entry += f"- {commit['message']} (`{commit['hash'][:7]}`)\n"
        
        if changes['features']:
            entry += "\n### ✨ Added\n"
            for commit in changes['features']:
                entry += f"- {commit['message']} (`{commit['hash'][:7]}`)\n"
        
        if changes['fixes']:
            entry += "\n### 🐛 Fixed\n"
            for commit in changes['fixes']:
                entry += f"- {commit['message']} (`{commit['hash'][:7]}`)\n"
        
        if changes['other']:
            entry += "\n### 🔧 Other\n"
            for commit in changes['other']:
                entry += f"- {commit['message']} (`{commit['hash'][:7]}`)\n"
        
        entry += "\n"
        
        # Insert after [Unreleased] section
        content = content.replace(
            "## [Unreleased]\n\n### Added\n- Initial project setup\n\n---",
            "## [Unreleased]\n\n### Added\n- Initial project setup\n" + entry + "---"
        )
        
        changelog_file.write_text(content)
    
    def update_readme_metrics(self):
        """Update README with current project metrics"""
        readme_file = self.project_path / DOCS_CONFIG['readme_file']
        
        if not readme_file.exists():
            print("⚠️ README.md not found - skipping metrics update")
            return
        
        try:
            # Get project statistics
            stats = self.gather_project_stats()
            
            # Load manifests if available
            manifest_file = self.project_path / '.claude' / 'manifests' / 'CODEBASE_MANIFEST.yaml'
            if manifest_file.exists():
                import yaml
                with open(manifest_file) as f:
                    manifest_data = yaml.safe_load(f)
                    if 'statistics' in manifest_data:
                        stats.update(manifest_data['statistics'])
            
            # Update README badges/metrics section
            self.update_readme_stats_section(readme_file, stats)
            print("✅ Updated README metrics")
            
        except Exception as e:
            print(f"⚠️ Error updating README metrics: {e}")
    
    def gather_project_stats(self):
        """Gather current project statistics"""
        stats = {}
        
        try:
            # Count commits
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True, text=True, cwd=self.project_path
            )
            if result.returncode == 0:
                stats['total_commits'] = int(result.stdout.strip())
            
            # Count contributors
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--all'],
                capture_output=True, text=True, cwd=self.project_path
            )
            if result.returncode == 0:
                stats['contributors'] = len(result.stdout.strip().split('\n'))
            
            # Count files
            result = subprocess.run(
                ['git', 'ls-files'],
                capture_output=True, text=True, cwd=self.project_path
            )
            if result.returncode == 0:
                stats['total_files'] = len(result.stdout.strip().split('\n'))
                
        except Exception as e:
            print(f"Error gathering stats: {e}")
        
        return stats
    
    def update_readme_stats_section(self, readme_file, stats):
        """Update or add stats section to README"""
        content = readme_file.read_text()
        
        stats_section = f"""
## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Total Commits | {stats.get('total_commits', 'N/A')} |
| Contributors | {stats.get('contributors', 'N/A')} |
| Total Files | {stats.get('total_files', 'N/A')} |
| Functions | {stats.get('total_functions', 'N/A')} |
| Exports | {stats.get('total_exports', 'N/A')} |

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

"""
        
        # Check if stats section exists
        if "## 📊 Project Statistics" in content:
            # Replace existing section
            pattern = r'## 📊 Project Statistics.*?(?=\n##|\n# |\Z)'
            content = re.sub(pattern, stats_section.strip(), content, flags=re.DOTALL)
        else:
            # Append stats section
            content += stats_section
        
        readme_file.write_text(content)
    
    def trigger_documentation_generation(self):
        """Trigger automated documentation generation"""
        print("📚 Triggering documentation generation...")
        
        # Regenerate manifests
        try:
            subprocess.run([
                'python3', str(Path.home() / '.claude' / 'hooks' / 'pre-agent-context.py'), '--refresh'
            ], cwd=self.project_path)
            print("✅ Refreshed code intelligence manifests")
        except Exception as e:
            print(f"⚠️ Error refreshing manifests: {e}")
        
        # Check for API documentation generation
        if (self.project_path / 'package.json').exists():
            try:
                # Look for API doc generation scripts
                package_json = json.loads((self.project_path / 'package.json').read_text())
                scripts = package_json.get('scripts', {})
                
                if 'docs:api' in scripts:
                    subprocess.run(['npm', 'run', 'docs:api'], cwd=self.project_path)
                    print("✅ Generated API documentation")
                elif 'docs' in scripts:
                    subprocess.run(['npm', 'run', 'docs'], cwd=self.project_path)
                    print("✅ Generated documentation")
                    
            except Exception as e:
                print(f"⚠️ Error generating API docs: {e}")
    
    def run_full_automation(self):
        """Run complete documentation automation"""
        print("🤖 Running post-merge documentation automation...")
        
        # Get recent commits
        commits = self.get_recent_commits()
        if not commits:
            print("ℹ️ No recent commits found - skipping automation")
            return
        
        print(f"📝 Processing {len(commits)} recent commits...")
        
        # Analyze what documentation needs updating
        doc_needs = {'roadmap': False, 'decisions': False, 'changelog': False, 'readme': False}
        
        for commit in commits:
            needs = self.analyze_commit_for_doc_needs(commit)
            for key in doc_needs:
                if needs.get(key):
                    doc_needs[key] = True
        
        # Update documentation based on needs
        if doc_needs['roadmap']:
            self.update_roadmap(commits)
        
        if doc_needs['decisions']:
            self.update_decisions_log(commits)
        
        if doc_needs['changelog']:
            self.update_changelog(commits)
        
        if doc_needs['readme']:
            self.update_readme_metrics()
        
        # Always trigger documentation generation
        self.trigger_documentation_generation()
        
        print("✅ Documentation automation complete!")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.getcwd()
    
    automator = DocumentationAutomator(project_path)
    automator.run_full_automation()

if __name__ == '__main__':
    main()