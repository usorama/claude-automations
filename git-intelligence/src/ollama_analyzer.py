#!/usr/bin/env python3
"""
Ollama-Powered Intelligent Git Analyzer
Uses local LLM to understand code changes and make intelligent commit decisions.
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class OllamaGitAnalyzer:
    """Intelligent git analyzer using Ollama for decision making."""
    
    def __init__(self, model: str = "qwen2.5:3b"):  # Fast 1.9GB model
        self.model = model
        self.state_file = Path.home() / '.claude' / 'ollama-git-state.json'
        self.state = self.load_state()
        self.change_buffer = []
        self.last_analysis = None
        
    def load_state(self) -> Dict:
        """Load persistent state."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except:
                pass
        return {
            'last_commit': datetime.now().isoformat(),
            'file_hashes': {},
            'pattern_history': [],
            'commit_count': 0
        }
        
    def save_state(self):
        """Save persistent state."""
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
            
    def get_changed_files(self) -> List[Dict]:
        """Get detailed info about changed files."""
        try:
            # Get list of changed files
            result = subprocess.run(
                ['git', 'diff', '--name-status', 'HEAD'],
                capture_output=True, text=True
            )
            
            if not result.stdout:
                return []
                
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 2:
                    status, filepath = parts[0], parts[1]
                    
                    # Get file extension and type
                    path = Path(filepath)
                    extension = path.suffix
                    
                    # Classify file type
                    file_type = self.classify_file(filepath)
                    
                    # Get change size
                    change_size = self.get_change_size(filepath)
                    
                    changes.append({
                        'path': filepath,
                        'status': status,
                        'extension': extension,
                        'type': file_type,
                        'change_size': change_size,
                        'directory': str(path.parent)
                    })
                    
            return changes
        except:
            return []
            
    def classify_file(self, filepath: str) -> str:
        """Classify file into categories."""
        path = Path(filepath)
        name = path.name.lower()
        ext = path.suffix.lower()
        
        # Test files
        if 'test' in name or 'spec' in name or '__tests__' in str(path):
            return 'test'
            
        # Documentation
        if ext in ['.md', '.rst', '.txt', '.adoc'] or name in ['README', 'LICENSE', 'CHANGELOG']:
            return 'documentation'
            
        # Configuration
        if ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.env'] or 'config' in name:
            return 'configuration'
            
        # Source code by language
        if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.cpp', '.c']:
            return 'source_code'
            
        # Build/Dependencies
        if name in ['package.json', 'requirements.txt', 'Pipfile', 'Cargo.toml', 'go.mod']:
            return 'dependencies'
            
        # Infrastructure
        if 'docker' in name.lower() or ext in ['.dockerfile'] or name in ['Makefile']:
            return 'infrastructure'
            
        return 'other'
        
    def get_change_size(self, filepath: str) -> Dict:
        """Get size of changes in a file."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--numstat', 'HEAD', '--', filepath],
                capture_output=True, text=True
            )
            
            if result.stdout:
                parts = result.stdout.strip().split('\t')
                if len(parts) >= 2:
                    added = int(parts[0]) if parts[0] != '-' else 0
                    deleted = int(parts[1]) if parts[1] != '-' else 0
                    return {
                        'added': added,
                        'deleted': deleted,
                        'total': added + deleted
                    }
        except:
            pass
            
        return {'added': 0, 'deleted': 0, 'total': 0}
        
    def analyze_with_ollama(self, changes: List[Dict]) -> Dict:
        """Use Ollama to analyze changes and make decisions."""
        
        # Prepare context for Ollama
        context = self.prepare_ollama_context(changes)
        
        # Create prompt for analysis
        prompt = f"""Analyze these git changes and determine if an auto-commit should happen now.

Changed Files:
{json.dumps(changes, indent=2)}

Summary:
- Total files: {len(changes)}
- Source code files: {len([c for c in changes if c['type'] == 'source_code'])}
- Test files: {len([c for c in changes if c['type'] == 'test'])}
- Documentation: {len([c for c in changes if c['type'] == 'documentation'])}
- Configuration: {len([c for c in changes if c['type'] == 'configuration'])}
- Total lines changed: {sum(c['change_size']['total'] for c in changes)}

Respond with JSON only:
{{
  "should_commit": true/false,
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "detected_pattern": "feature|bugfix|refactor|test|docs|config|wip",
  "commit_message": "suggested commit message",
  "urgency": "high|medium|low"
}}"""

        try:
            # Call Ollama
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=10  # Fast model should respond quickly
            )
            
            if result.returncode == 0:
                # Extract JSON from response
                response = result.stdout.strip()
                
                # Try to parse JSON (might need to extract from text)
                try:
                    # Find JSON in response
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            print(f"Ollama error: {e}")
            
        # Fallback to rule-based decision
        return self.fallback_analysis(changes)
        
    def fallback_analysis(self, changes: List[Dict]) -> Dict:
        """Rule-based fallback when Ollama fails."""
        
        should_commit = False
        reason = ""
        pattern = "wip"
        urgency = "low"
        
        # Analyze patterns
        test_files = [c for c in changes if c['type'] == 'test']
        source_files = [c for c in changes if c['type'] == 'source_code']
        config_files = [c for c in changes if c['type'] == 'configuration']
        doc_files = [c for c in changes if c['type'] == 'documentation']
        
        total_changes = sum(c['change_size']['total'] for c in changes)
        
        # Decision rules
        if len(test_files) >= 2:
            should_commit = True
            reason = "Multiple test files added/modified - likely feature complete"
            pattern = "test"
            urgency = "high"
            
        elif len(changes) >= 10:
            should_commit = True
            reason = f"{len(changes)} files changed - significant work"
            pattern = "feature"
            urgency = "high"
            
        elif total_changes >= 500:
            should_commit = True
            reason = f"{total_changes} lines changed - substantial modifications"
            pattern = "refactor"
            urgency = "high"
            
        elif len(config_files) >= 3:
            should_commit = True
            reason = "Multiple configuration files changed"
            pattern = "config"
            urgency = "medium"
            
        elif len(doc_files) >= 3:
            should_commit = True
            reason = "Documentation update"
            pattern = "docs"
            urgency = "low"
            
        elif len(changes) >= 5:
            should_commit = True
            reason = "Threshold of 5 files reached"
            pattern = "wip"
            urgency = "medium"
            
        # Generate commit message
        if pattern == "test":
            commit_msg = f"test: Add tests for {', '.join(set(c['directory'] for c in test_files[:3]))}"
        elif pattern == "docs":
            commit_msg = f"docs: Update documentation"
        elif pattern == "config":
            commit_msg = f"chore: Update configuration"
        elif pattern == "feature":
            commit_msg = f"feat: Implement changes in {', '.join(set(c['directory'] for c in source_files[:3]))}"
        else:
            commit_msg = f"WIP: {len(changes)} files modified"
            
        return {
            "should_commit": should_commit,
            "confidence": 0.7,
            "reason": reason,
            "detected_pattern": pattern,
            "commit_message": commit_msg,
            "urgency": urgency
        }
        
    def prepare_ollama_context(self, changes: List[Dict]) -> str:
        """Prepare enriched context for Ollama."""
        
        # Get recent commit messages for context
        recent_commits = []
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '-5'],
                capture_output=True, text=True
            )
            if result.stdout:
                recent_commits = result.stdout.strip().split('\n')
        except:
            pass
            
        # Build context
        context = {
            'changes': changes,
            'recent_commits': recent_commits,
            'time_since_last_commit': self.get_time_since_last_commit(),
            'working_directory': os.getcwd(),
            'branch': self.get_current_branch()
        }
        
        return json.dumps(context, indent=2)
        
    def get_time_since_last_commit(self) -> str:
        """Get time since last commit."""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%cr'],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.stdout else "unknown"
        except:
            return "unknown"
            
    def get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.stdout else "unknown"
        except:
            return "unknown"
            
    def should_analyze(self) -> bool:
        """Determine if we should run analysis now."""
        
        # Don't analyze too frequently
        if self.last_analysis:
            time_since = datetime.now() - self.last_analysis
            if time_since.total_seconds() < 60:  # Wait at least 1 minute
                return False
                
        return True
        
    def run_analysis(self) -> Optional[Dict]:
        """Run the complete analysis pipeline."""
        
        if not self.should_analyze():
            return None
            
        # Get changed files
        changes = self.get_changed_files()
        
        if not changes:
            return None
            
        # Analyze with Ollama (or fallback)
        analysis = self.analyze_with_ollama(changes)
        
        # Update state
        self.last_analysis = datetime.now()
        analysis['timestamp'] = self.last_analysis.isoformat()
        analysis['file_count'] = len(changes)
        
        # Save to state
        if 'analyses' not in self.state:
            self.state['analyses'] = []
        self.state['analyses'].append(analysis)
        
        # Keep only last 100 analyses
        if len(self.state['analyses']) > 100:
            self.state['analyses'] = self.state['analyses'][-100:]
            
        self.save_state()
        
        return analysis


def main():
    """CLI interface for testing."""
    analyzer = OllamaGitAnalyzer()
    
    print("🤖 Ollama Git Analyzer")
    print("-" * 40)
    
    # Run analysis
    analysis = analyzer.run_analysis()
    
    if not analysis:
        print("No changes to analyze")
        return
        
    # Display results
    print(f"Should Commit: {'✅' if analysis['should_commit'] else '❌'}")
    print(f"Confidence: {analysis['confidence']:.1%}")
    print(f"Reason: {analysis['reason']}")
    print(f"Pattern: {analysis['detected_pattern']}")
    print(f"Urgency: {analysis['urgency']}")
    print(f"Suggested Message: {analysis['commit_message']}")
    
    if analysis['should_commit'] and analysis['urgency'] == 'high':
        print("\n⚠️  HIGH URGENCY - Commit recommended NOW")


if __name__ == "__main__":
    main()