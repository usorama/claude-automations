#!/usr/bin/env python3
"""
Git State Analyzer
Analyzes repository state, detects changes, and identifies work patterns.

Using Framework: Problem Decomposition
- Breaking down git analysis into discrete, testable components
- Each method has single responsibility
- Clear data structures for state representation
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import git
from git import Repo, DiffIndex
import json
import re
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from logger import logger


class WorkPattern(Enum):
    """Work pattern types detected from changes"""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REFACTORING = "refactoring"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


@dataclass
class FileChange:
    """Represents a single file change"""
    path: str
    change_type: str  # 'added', 'modified', 'deleted', 'renamed'
    diff_stats: Optional[Dict] = None
    category: Optional[str] = None
    
    def __repr__(self):
        return f"FileChange({self.change_type}: {self.path})"


@dataclass
class RepositoryState:
    """
    Complete repository state snapshot
    
    Using Framework: Data Modeling
    - Clear, structured representation of state
    - Immutable dataclass for consistency
    - Type hints for clarity
    """
    branch: str
    has_uncommitted: bool
    has_untracked: bool
    total_changes: int
    ahead_of_remote: int
    behind_remote: int
    last_commit_hash: Optional[str] = None
    last_commit_message: Optional[str] = None
    last_commit_time: Optional[datetime] = None
    
    def is_clean(self) -> bool:
        """Check if repository is in clean state"""
        return not self.has_uncommitted and not self.has_untracked
    
    def needs_sync(self) -> bool:
        """Check if needs sync with remote"""
        return self.ahead_of_remote > 0 or self.behind_remote > 0


@dataclass
class ChangesSummary:
    """Summary of all repository changes"""
    total_files: int = 0
    added_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)
    renamed_files: List[Tuple[str, str]] = field(default_factory=list)
    categories: Dict[str, List[str]] = field(default_factory=dict)
    work_pattern: WorkPattern = WorkPattern.UNKNOWN
    lines_added: int = 0
    lines_deleted: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'total_files': self.total_files,
            'added': len(self.added_files),
            'modified': len(self.modified_files),
            'deleted': len(self.deleted_files),
            'renamed': len(self.renamed_files),
            'work_pattern': self.work_pattern.value,
            'lines_added': self.lines_added,
            'lines_deleted': self.lines_deleted
        }


class GitStateAnalyzer:
    """
    Analyzes git repository state and changes
    
    Using Framework: Testing Strategy
    - Each method is independently testable
    - Clear inputs and outputs
    - No hidden dependencies
    """
    
    def __init__(self, repo_path: str = "."):
        """Initialize analyzer with repository path"""
        self.repo_path = Path(repo_path).resolve()
        
        # Validate git repository
        try:
            self.repo = Repo(self.repo_path)
            if self.repo.bare:
                raise ValueError("Cannot analyze bare repository")
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Not a git repository: {self.repo_path}")
        
        # Load patterns configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "patterns.json"
        with open(config_path, 'r') as f:
            self.patterns = json.load(f)
        
        logger.info(f"Initialized GitStateAnalyzer for {self.repo_path}")
    
    def get_repository_state(self) -> RepositoryState:
        """
        Get current repository state
        
        Using Framework: Single Responsibility
        - This method only gathers state, doesn't analyze
        """
        try:
            # Get current branch
            branch = self.repo.active_branch.name
        except TypeError:
            # Detached HEAD state
            branch = f"detached@{self.repo.head.commit.hexsha[:7]}"
        
        # Check for changes
        has_uncommitted = self.repo.is_dirty(untracked_files=True)
        has_untracked = len(self.repo.untracked_files) > 0
        
        # Count total changes
        changed_files = self.get_uncommitted_changes()
        total_changes = len(changed_files)
        
        # Get remote tracking info
        ahead, behind = self._get_remote_tracking_counts()
        
        # Get last commit info
        last_commit = None
        last_message = None
        last_time = None
        
        if self.repo.head.is_valid():
            commit = self.repo.head.commit
            last_commit = commit.hexsha[:7]
            last_message = commit.message.strip()
            last_time = datetime.fromtimestamp(commit.committed_date)
        
        state = RepositoryState(
            branch=branch,
            has_uncommitted=has_uncommitted,
            has_untracked=has_untracked,
            total_changes=total_changes,
            ahead_of_remote=ahead,
            behind_remote=behind,
            last_commit_hash=last_commit,
            last_commit_message=last_message,
            last_commit_time=last_time
        )
        
        logger.debug(f"Repository state: {state}")
        return state
    
    def get_uncommitted_changes(self) -> List[FileChange]:
        """
        Get all uncommitted changes
        
        Using Framework: Error Handling
        - Graceful handling of edge cases
        - Clear error messages
        """
        changes = []
        
        # Get staged changes
        for item in self.repo.index.diff("HEAD"):
            change_type = self._get_change_type(item)
            changes.append(FileChange(
                path=item.a_path or item.b_path,
                change_type=change_type,
                diff_stats=self._get_diff_stats(item)
            ))
        
        # Get unstaged changes
        for item in self.repo.index.diff(None):
            change_type = self._get_change_type(item)
            changes.append(FileChange(
                path=item.a_path or item.b_path,
                change_type=change_type,
                diff_stats=self._get_diff_stats(item)
            ))
        
        # Get untracked files
        for path in self.repo.untracked_files:
            changes.append(FileChange(
                path=path,
                change_type='added',
                diff_stats=None
            ))
        
        # Categorize each change
        for change in changes:
            change.category = self._categorize_file(change.path)
        
        logger.info(f"Found {len(changes)} uncommitted changes")
        return changes
    
    def categorize_changes(self, changes: List[FileChange]) -> Dict[str, List[FileChange]]:
        """
        Categorize changes by file type
        
        Using Framework: Data Organization
        - Clear categorization logic
        - Extensible through configuration
        """
        categories = {}
        
        for change in changes:
            category = change.category or self._categorize_file(change.path)
            if category not in categories:
                categories[category] = []
            categories[category].append(change)
        
        logger.debug(f"Categorized into {len(categories)} categories")
        return categories
    
    def generate_change_summary(self, changes: Optional[List[FileChange]] = None) -> ChangesSummary:
        """
        Generate comprehensive change summary
        
        Using Framework: Information Architecture
        - Structured summary for easy consumption
        - All relevant metrics in one place
        """
        if changes is None:
            changes = self.get_uncommitted_changes()
        
        summary = ChangesSummary()
        summary.total_files = len(changes)
        
        # Categorize by change type
        for change in changes:
            if change.change_type == 'added':
                summary.added_files.append(change.path)
            elif change.change_type == 'modified':
                summary.modified_files.append(change.path)
            elif change.change_type == 'deleted':
                summary.deleted_files.append(change.path)
            elif change.change_type == 'renamed':
                # Handle renames specially
                parts = change.path.split(' -> ')
                if len(parts) == 2:
                    summary.renamed_files.append((parts[0], parts[1]))
            
            # Add to categories
            category = change.category or 'other'
            if category not in summary.categories:
                summary.categories[category] = []
            summary.categories[category].append(change.path)
            
            # Sum line changes
            if change.diff_stats:
                summary.lines_added += change.diff_stats.get('insertions', 0)
                summary.lines_deleted += change.diff_stats.get('deletions', 0)
        
        # Detect work pattern
        summary.work_pattern = self.detect_work_pattern(changes)
        
        logger.info(f"Generated summary: {summary.total_files} files, pattern: {summary.work_pattern.value}")
        return summary
    
    def detect_work_pattern(self, changes: List[FileChange]) -> WorkPattern:
        """
        Detect the type of work from changes
        
        Using Framework: Pattern Recognition
        - Rule-based pattern matching
        - Configurable through patterns.json
        """
        if not changes:
            return WorkPattern.UNKNOWN
        
        # Count indicators
        pattern_scores = {pattern: 0 for pattern in WorkPattern}
        
        for change in changes:
            path_lower = change.path.lower()
            
            # Check each pattern's indicators
            for pattern_name, pattern_config in self.patterns['work_patterns'].items():
                # Check file path patterns
                for file_pattern in pattern_config.get('file_patterns', []):
                    if file_pattern in path_lower:
                        pattern_scores[WorkPattern(pattern_name)] += 2
                
                # Check indicators in path
                for indicator in pattern_config.get('indicators', []):
                    if indicator in path_lower:
                        pattern_scores[WorkPattern(pattern_name)] += 1
        
        # Check file extensions
        for change in changes:
            ext = Path(change.path).suffix
            if ext in ['.test.js', '.spec.js', '.test.py', '_test.py']:
                pattern_scores[WorkPattern.TESTING] += 3
            elif ext in ['.md', '.rst', '.txt']:
                pattern_scores[WorkPattern.DOCUMENTATION] += 3
            elif ext in ['.json', '.yaml', '.yml', '.toml', '.env']:
                pattern_scores[WorkPattern.CONFIGURATION] += 2
        
        # Find highest scoring pattern
        max_score = 0
        detected_pattern = WorkPattern.UNKNOWN
        
        for pattern, score in pattern_scores.items():
            if score > max_score:
                max_score = score
                detected_pattern = pattern
        
        logger.debug(f"Pattern scores: {pattern_scores}")
        logger.info(f"Detected work pattern: {detected_pattern.value}")
        
        return detected_pattern
    
    def _get_change_type(self, diff_item) -> str:
        """Determine change type from diff item"""
        if diff_item.new_file:
            return 'added'
        elif diff_item.deleted_file:
            return 'deleted'
        elif diff_item.renamed:
            return 'renamed'
        else:
            return 'modified'
    
    def _get_diff_stats(self, diff_item) -> Optional[Dict]:
        """Get diff statistics if available"""
        try:
            # This might not always be available
            return {
                'insertions': getattr(diff_item, 'insertions', 0),
                'deletions': getattr(diff_item, 'deletions', 0)
            }
        except:
            return None
    
    def _categorize_file(self, file_path: str) -> str:
        """
        Categorize file based on path and extension
        
        Using Framework: Configuration-Driven
        - Categories defined in config, not hardcoded
        """
        path_lower = file_path.lower()
        
        # Check each category
        for category, patterns in self.patterns['file_categories'].items():
            for pattern in patterns:
                if pattern.startswith('*'):
                    # Extension pattern
                    if path_lower.endswith(pattern[1:]):
                        return category
                elif '*' in pattern:
                    # Glob pattern
                    import fnmatch
                    if fnmatch.fnmatch(path_lower, pattern):
                        return category
                else:
                    # Simple contains
                    if pattern in path_lower:
                        return category
        
        return 'other'
    
    def _get_remote_tracking_counts(self) -> Tuple[int, int]:
        """Get ahead/behind counts for remote tracking branch"""
        try:
            # Get tracking branch
            tracking = self.repo.active_branch.tracking_branch()
            if not tracking:
                return 0, 0
            
            # Count commits ahead and behind
            ahead = len(list(self.repo.iter_commits(f'{tracking}..HEAD')))
            behind = len(list(self.repo.iter_commits(f'HEAD..{tracking}')))
            
            return ahead, behind
        except:
            return 0, 0
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict]:
        """
        Get recent commits for context
        
        Using Framework: Context Gathering
        - Provides historical context for better decisions
        """
        commits = []
        
        try:
            for commit in self.repo.iter_commits('HEAD', max_count=limit):
                commits.append({
                    'hash': commit.hexsha[:7],
                    'message': commit.message.strip().split('\n')[0],  # First line only
                    'author': commit.author.name,
                    'date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                    'files_changed': len(commit.stats.files)
                })
        except:
            logger.warning("Could not retrieve recent commits")
        
        return commits


# Testing utilities for development
if __name__ == "__main__":
    """Quick test of analyzer functionality"""
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Analyzing repository: {repo_path}")
    print("-" * 50)
    
    try:
        analyzer = GitStateAnalyzer(repo_path)
        
        # Get repository state
        state = analyzer.get_repository_state()
        print(f"Repository State:")
        print(f"  Branch: {state.branch}")
        print(f"  Clean: {state.is_clean()}")
        print(f"  Changes: {state.total_changes}")
        print(f"  Ahead/Behind: {state.ahead_of_remote}/{state.behind_remote}")
        print()
        
        # Get changes
        changes = analyzer.get_uncommitted_changes()
        if changes:
            print(f"Uncommitted Changes ({len(changes)} files):")
            for change in changes[:5]:  # Show first 5
                print(f"  {change.change_type}: {change.path} [{change.category}]")
            if len(changes) > 5:
                print(f"  ... and {len(changes) - 5} more")
            print()
            
            # Generate summary
            summary = analyzer.generate_change_summary(changes)
            print(f"Change Summary:")
            print(f"  Pattern: {summary.work_pattern.value}")
            print(f"  Added: {len(summary.added_files)}")
            print(f"  Modified: {len(summary.modified_files)}")
            print(f"  Deleted: {len(summary.deleted_files)}")
            print(f"  Lines: +{summary.lines_added} -{summary.lines_deleted}")
        else:
            print("No uncommitted changes")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()