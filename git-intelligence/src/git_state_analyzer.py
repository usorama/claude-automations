"""
Git State Analyzer - A comprehensive tool for analyzing Git repository state and changes.

This module provides functionality to analyze Git repositories, detect changes,
categorize files, and generate intelligent summaries of the current work state.
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkPatternType(Enum):
    """Enumeration of different work patterns."""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    DOCS = "docs"
    TESTING = "testing"
    REFACTORING = "refactoring"
    CONFIG = "config"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class FileCategory(Enum):
    """Enumeration of file categories."""
    SOURCE = "source"
    TEST = "test"
    CONFIG = "config"
    DOCS = "docs"
    BUILD = "build"
    ASSETS = "assets"
    OTHER = "other"


@dataclass
class FileChange:
    """Represents a single file change in the repository."""
    path: str
    status: str  # M, A, D, R, C, U
    category: FileCategory
    lines_added: int = 0
    lines_removed: int = 0
    is_binary: bool = False
    
    @property
    def change_type(self) -> str:
        """Return human-readable change type."""
        status_map = {
            'M': 'Modified',
            'A': 'Added',
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            'U': 'Unmerged'
        }
        return status_map.get(self.status, 'Unknown')


@dataclass
class ChangeSummary:
    """Summary of changes in the repository."""
    total_files: int
    files_by_category: Dict[FileCategory, int] = field(default_factory=dict)
    files_by_status: Dict[str, int] = field(default_factory=dict)
    total_lines_added: int = 0
    total_lines_removed: int = 0
    binary_files: int = 0
    
    def __post_init__(self):
        """Initialize default dictionaries after creation."""
        if not self.files_by_category:
            self.files_by_category = defaultdict(int)
        if not self.files_by_status:
            self.files_by_status = defaultdict(int)


@dataclass
class WorkPattern:
    """Represents detected work patterns based on file changes."""
    primary_pattern: WorkPatternType
    confidence: float
    patterns: Dict[WorkPatternType, float] = field(default_factory=dict)
    indicators: List[str] = field(default_factory=list)


@dataclass
class GitState:
    """Complete state of a Git repository."""
    repo_path: str
    is_valid_repo: bool
    current_branch: str
    has_remote: bool
    is_detached_head: bool
    uncommitted_changes: List[FileChange]
    staged_changes: List[FileChange]
    untracked_files: List[str]
    change_summary: ChangeSummary
    work_pattern: WorkPattern
    last_commit_hash: Optional[str] = None
    last_commit_message: Optional[str] = None
    commits_ahead: int = 0
    commits_behind: int = 0


class GitStateAnalyzer:
    """
    Comprehensive Git repository state analyzer.
    
    This class provides methods to analyze the current state of a Git repository,
    including detecting changes, categorizing files, and identifying work patterns.
    """
    
    def __init__(self, repo_path: str = ".", patterns_file: Optional[str] = None):
        """
        Initialize the Git State Analyzer.
        
        Args:
            repo_path: Path to the Git repository
            patterns_file: Path to patterns configuration file
        """
        self.repo_path = Path(repo_path).resolve()
        self.patterns_file = patterns_file or self._default_patterns_file()
        self.patterns_config = self._load_patterns_config()
        
        # File categorization patterns (order matters - test patterns first)
        self.file_patterns = {
            FileCategory.TEST: [
                r'test_.*\.py$',
                r'.*_test\.py$',
                r'.*\.test\.(js|ts|jsx|tsx)$',
                r'.*\.spec\.(js|ts|jsx|tsx)$',
                r'tests?/.*',
                r'__tests__/.*',
                r'.*Test\.(java|cs|kt)$'
            ],
            FileCategory.CONFIG: [
                r'\.(json|yaml|yml|toml|ini|cfg|conf)$',
                r'(^|/)dockerfile.*',
                r'docker-compose.*\.ya?ml$',
                r'\.(env|example|sample)$',
                r'requirements.*\.txt$',
                r'package\.json$',
                r'tsconfig\.json$',
                r'\.gitignore$',
                r'\..*rc$'
            ],
            FileCategory.SOURCE: [
                r'\.(py|js|ts|jsx|tsx|java|cpp|c|h|cs|rb|php|go|rs|swift|kt)$',
                r'\.(html|css|scss|sass|less|vue|svelte)$'
            ],
            FileCategory.DOCS: [
                r'\.(md|rst|txt|doc|docx|pdf)$',
                r'README.*',
                r'CHANGELOG.*',
                r'docs?/.*'
            ],
            FileCategory.BUILD: [
                r'Makefile$',
                r'CMakeLists\.txt$',
                r'build\.gradle$',
                r'pom\.xml$',
                r'setup\.py$',
                r'pyproject\.toml$',
                r'webpack\.config\.js$',
                r'rollup\.config\.js$'
            ],
            FileCategory.ASSETS: [
                r'\.(png|jpg|jpeg|gif|svg|ico|webp)$',
                r'\.(woff|woff2|ttf|eot)$',
                r'\.(mp3|mp4|wav|avi|mov)$'
            ]
        }
    
    def _default_patterns_file(self) -> str:
        """Get default patterns file path."""
        return str(self.repo_path / "src" / "patterns.json")
    
    def _load_patterns_config(self) -> Dict:
        """Load work patterns configuration from file."""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load patterns file {self.patterns_file}: {e}")
        
        # Return default patterns if file doesn't exist or can't be loaded
        return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict:
        """Get default work patterns configuration."""
        return {
            "feature": {
                "file_patterns": [".*\\.py$", ".*\\.js$", ".*\\.ts$"],
                "path_patterns": ["src/", "lib/", "components/"],
                "keywords": ["add", "new", "create", "implement", "feature"],
                "weight": 1.0
            },
            "bugfix": {
                "file_patterns": [".*\\.py$", ".*\\.js$", ".*\\.ts$"],
                "path_patterns": ["src/", "lib/"],
                "keywords": ["fix", "bug", "error", "issue", "patch"],
                "weight": 1.2
            },
            "docs": {
                "file_patterns": [".*\\.md$", ".*\\.rst$", ".*\\.txt$"],
                "path_patterns": ["docs/", "README"],
                "keywords": ["doc", "readme", "documentation"],
                "weight": 0.8
            },
            "testing": {
                "file_patterns": ["test_.*\\.py$", ".*_test\\.py$", ".*\\.test\\.(js|ts)$"],
                "path_patterns": ["tests/", "test/", "__tests__/"],
                "keywords": ["test", "spec", "mock"],
                "weight": 0.9
            },
            "refactoring": {
                "file_patterns": [".*\\.(py|js|ts|jsx|tsx)$"],
                "path_patterns": ["src/", "lib/"],
                "keywords": ["refactor", "cleanup", "optimize", "restructure"],
                "weight": 0.7
            }
        }
    
    def _run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """
        Run a git command and return success status and output.
        
        Args:
            command: Git command as list of strings
            
        Returns:
            Tuple of (success, output)
        """
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.error("Git command timed out")
            return False, ""
        except Exception as e:
            logger.error(f"Error running git command: {e}")
            return False, ""
    
    def _is_valid_repo(self) -> bool:
        """Check if the current directory is a valid Git repository."""
        success, _ = self._run_git_command(['rev-parse', '--git-dir'])
        return success
    
    def _get_current_branch(self) -> str:
        """Get the current branch name."""
        success, output = self._run_git_command(['branch', '--show-current'])
        if success and output:
            return output
        
        # Fallback for detached HEAD
        success, output = self._run_git_command(['rev-parse', '--short', 'HEAD'])
        if success:
            return f"HEAD ({output})"
        
        return "unknown"
    
    def _is_detached_head(self) -> bool:
        """Check if repository is in detached HEAD state."""
        success, output = self._run_git_command(['symbolic-ref', '-q', 'HEAD'])
        return not success
    
    def _has_remote(self) -> bool:
        """Check if repository has a remote."""
        success, output = self._run_git_command(['remote'])
        return success and bool(output.strip())
    
    def _get_remote_status(self) -> Tuple[int, int]:
        """Get commits ahead and behind remote."""
        if not self._has_remote():
            return 0, 0
        
        success, output = self._run_git_command(['rev-list', '--left-right', '--count', 'HEAD...@{upstream}'])
        if success and output:
            try:
                ahead, behind = output.split()
                return int(ahead), int(behind)
            except (ValueError, IndexError):
                pass
        
        return 0, 0
    
    def _get_last_commit_info(self) -> Tuple[Optional[str], Optional[str]]:
        """Get last commit hash and message."""
        success, hash_output = self._run_git_command(['rev-parse', '--short', 'HEAD'])
        commit_hash = hash_output if success else None
        
        success, msg_output = self._run_git_command(['log', '-1', '--pretty=format:%s'])
        commit_message = msg_output if success else None
        
        return commit_hash, commit_message
    
    def _categorize_file(self, filepath: str) -> FileCategory:
        """
        Categorize a file based on its path and extension.
        
        Args:
            filepath: Path to the file
            
        Returns:
            FileCategory enum value
        """
        filepath_lower = filepath.lower()
        
        for category, patterns in self.file_patterns.items():
            for pattern in patterns:
                if re.search(pattern, filepath_lower):
                    return category
        
        return FileCategory.OTHER
    
    def _get_file_stats(self, filepath: str) -> Tuple[int, int, bool]:
        """
        Get file statistics (lines added, removed, is_binary).
        
        Args:
            filepath: Path to the file
            
        Returns:
            Tuple of (lines_added, lines_removed, is_binary)
        """
        success, output = self._run_git_command(['diff', '--numstat', 'HEAD', '--', filepath])
        if not success or not output:
            return 0, 0, False
        
        parts = output.split('\t')
        if len(parts) >= 2:
            try:
                added = int(parts[0]) if parts[0] != '-' else 0
                removed = int(parts[1]) if parts[1] != '-' else 0
                is_binary = parts[0] == '-' and parts[1] == '-'
                return added, removed, is_binary
            except ValueError:
                pass
        
        return 0, 0, False
    
    def _parse_git_status(self) -> Tuple[List[FileChange], List[FileChange], List[str]]:
        """
        Parse git status output to get changes.
        
        Returns:
            Tuple of (staged_changes, uncommitted_changes, untracked_files)
        """
        success, output = self._run_git_command(['status', '--porcelain'])
        if not success:
            return [], [], []
        
        staged_changes = []
        uncommitted_changes = []
        untracked_files = []
        
        for line in output.split('\n'):
            if not line:
                continue
            
            if len(line) < 3:
                continue
            
            index_status = line[0]
            worktree_status = line[1]
            filepath = line[3:]  # Skip the two status characters and space
            
            # Handle untracked files
            if index_status == '?' and worktree_status == '?':
                untracked_files.append(filepath)
                continue
            
            category = self._categorize_file(filepath)
            lines_added, lines_removed, is_binary = self._get_file_stats(filepath)
            
            # Staged changes (index status)
            if index_status != ' ' and index_status != '?':
                staged_changes.append(FileChange(
                    path=filepath,
                    status=index_status,
                    category=category,
                    lines_added=lines_added,
                    lines_removed=lines_removed,
                    is_binary=is_binary
                ))
            
            # Uncommitted changes (worktree status)
            if worktree_status != ' ' and worktree_status != '?':
                uncommitted_changes.append(FileChange(
                    path=filepath,
                    status=worktree_status,
                    category=category,
                    lines_added=lines_added,
                    lines_removed=lines_removed,
                    is_binary=is_binary
                ))
        
        return staged_changes, uncommitted_changes, untracked_files
    
    def _create_change_summary(self, changes: List[FileChange]) -> ChangeSummary:
        """
        Create a summary of file changes.
        
        Args:
            changes: List of FileChange objects
            
        Returns:
            ChangeSummary object
        """
        summary = ChangeSummary(total_files=len(changes))
        
        for change in changes:
            # Count by category
            summary.files_by_category[change.category] += 1
            
            # Count by status
            summary.files_by_status[change.status] += 1
            
            # Sum line changes
            summary.total_lines_added += change.lines_added
            summary.total_lines_removed += change.lines_removed
            
            # Count binary files
            if change.is_binary:
                summary.binary_files += 1
        
        return summary
    
    def _detect_work_pattern(self, changes: List[FileChange]) -> WorkPattern:
        """
        Detect work patterns based on file changes.
        
        Args:
            changes: List of FileChange objects
            
        Returns:
            WorkPattern object
        """
        if not changes:
            return WorkPattern(
                primary_pattern=WorkPatternType.UNKNOWN,
                confidence=0.0,
                patterns={},
                indicators=[]
            )
        
        pattern_scores = defaultdict(float)
        indicators = []
        
        # Analyze files for patterns
        for change in changes:
            filepath = change.path.lower()
            
            for pattern_name, config in self.patterns_config.items():
                score = 0.0
                weight = config.get('weight', 1.0)
                
                # Check file patterns
                for file_pattern in config.get('file_patterns', []):
                    if re.search(file_pattern, filepath):
                        score += 1.0
                        indicators.append(f"File pattern match: {file_pattern}")
                
                # Check path patterns
                for path_pattern in config.get('path_patterns', []):
                    if path_pattern.lower() in filepath:
                        score += 0.5
                        indicators.append(f"Path pattern match: {path_pattern}")
                
                try:
                    pattern_scores[WorkPatternType(pattern_name)] += score * weight
                except ValueError:
                    # Skip unknown pattern types
                    logger.debug(f"Unknown work pattern type: {pattern_name}")
        
        # Analyze file categories for additional patterns
        category_counts = defaultdict(int)
        for change in changes:
            category_counts[change.category] += 1
        
        # Test files suggest testing work
        if category_counts[FileCategory.TEST] > 0:
            test_ratio = category_counts[FileCategory.TEST] / len(changes)
            pattern_scores[WorkPatternType.TESTING] += test_ratio * 2.0
            indicators.append(f"Test files: {category_counts[FileCategory.TEST]}")
        
        # Doc files suggest documentation work
        if category_counts[FileCategory.DOCS] > 0:
            doc_ratio = category_counts[FileCategory.DOCS] / len(changes)
            pattern_scores[WorkPatternType.DOCS] += doc_ratio * 2.0
            indicators.append(f"Documentation files: {category_counts[FileCategory.DOCS]}")
        
        # Config files suggest configuration work
        if category_counts[FileCategory.CONFIG] > 0:
            config_ratio = category_counts[FileCategory.CONFIG] / len(changes)
            pattern_scores[WorkPatternType.CONFIG] += config_ratio * 1.5
            indicators.append(f"Configuration files: {category_counts[FileCategory.CONFIG]}")
        
        # Determine primary pattern and confidence
        if not pattern_scores:
            primary_pattern = WorkPatternType.UNKNOWN
            confidence = 0.0
        else:
            total_score = sum(pattern_scores.values())
            if total_score == 0:
                primary_pattern = WorkPatternType.UNKNOWN
                confidence = 0.0
            else:
                # Normalize scores
                normalized_scores = {k: v / total_score for k, v in pattern_scores.items()}
                primary_pattern = max(normalized_scores.keys(), key=lambda k: normalized_scores[k])
                confidence = normalized_scores[primary_pattern]
                
                # Check for mixed patterns
                significant_patterns = [k for k, v in normalized_scores.items() if v > 0.25]
                if len(significant_patterns) > 2 and confidence < 0.6:
                    primary_pattern = WorkPatternType.MIXED
                    confidence = min(confidence, 0.7)  # Reduce confidence for mixed patterns
        
        return WorkPattern(
            primary_pattern=primary_pattern,
            confidence=confidence,
            patterns=dict(pattern_scores),
            indicators=indicators[:10]  # Limit indicators to prevent clutter
        )
    
    def analyze(self) -> GitState:
        """
        Perform complete analysis of the Git repository state.
        
        Returns:
            GitState object containing all analysis results
            
        Raises:
            ValueError: If the repository is invalid or has critical issues
        """
        # Basic repository validation
        if not self._is_valid_repo():
            raise ValueError(f"Not a valid Git repository: {self.repo_path}")
        
        # Get basic repository information
        current_branch = self._get_current_branch()
        is_detached = self._is_detached_head()
        has_remote = self._has_remote()
        
        # Get commit information
        last_commit_hash, last_commit_message = self._get_last_commit_info()
        commits_ahead, commits_behind = self._get_remote_status()
        
        # Parse changes
        try:
            staged_changes, uncommitted_changes, untracked_files = self._parse_git_status()
        except Exception as e:
            logger.error(f"Error parsing git status: {e}")
            staged_changes, uncommitted_changes, untracked_files = [], [], []
        
        # Create summaries and detect patterns
        all_changes = staged_changes + uncommitted_changes
        change_summary = self._create_change_summary(all_changes)
        work_pattern = self._detect_work_pattern(all_changes)
        
        return GitState(
            repo_path=str(self.repo_path),
            is_valid_repo=True,
            current_branch=current_branch,
            has_remote=has_remote,
            is_detached_head=is_detached,
            uncommitted_changes=uncommitted_changes,
            staged_changes=staged_changes,
            untracked_files=untracked_files,
            change_summary=change_summary,
            work_pattern=work_pattern,
            last_commit_hash=last_commit_hash,
            last_commit_message=last_commit_message,
            commits_ahead=commits_ahead,
            commits_behind=commits_behind
        )
    
    def get_change_summary_text(self, state: GitState) -> str:
        """
        Generate a human-readable summary of changes.
        
        Args:
            state: GitState object from analyze()
            
        Returns:
            Formatted string summary
        """
        lines = []
        
        # Repository status
        lines.append(f"Repository: {state.repo_path}")
        lines.append(f"Branch: {state.current_branch}")
        
        if state.is_detached_head:
            lines.append("⚠️  Detached HEAD state")
        
        if not state.has_remote:
            lines.append("⚠️  No remote repository configured")
        
        if state.commits_ahead > 0:
            lines.append(f"↑ {state.commits_ahead} commits ahead of remote")
        
        if state.commits_behind > 0:
            lines.append(f"↓ {state.commits_behind} commits behind remote")
        
        lines.append("")
        
        # Change summary
        total_changes = len(state.uncommitted_changes) + len(state.staged_changes)
        if total_changes == 0:
            lines.append("✅ No uncommitted changes")
        else:
            lines.append(f"📊 Total changes: {total_changes}")
            
            if state.staged_changes:
                lines.append(f"   Staged: {len(state.staged_changes)}")
            
            if state.uncommitted_changes:
                lines.append(f"   Uncommitted: {len(state.uncommitted_changes)}")
            
            if state.untracked_files:
                lines.append(f"   Untracked: {len(state.untracked_files)}")
        
        # Category breakdown
        if state.change_summary.files_by_category:
            lines.append("\n📁 Files by category:")
            for category, count in state.change_summary.files_by_category.items():
                if count > 0:
                    lines.append(f"   {category.value.title()}: {count}")
        
        # Line changes
        if state.change_summary.total_lines_added > 0 or state.change_summary.total_lines_removed > 0:
            lines.append(f"\n📈 Lines changed: +{state.change_summary.total_lines_added}, -{state.change_summary.total_lines_removed}")
        
        # Work pattern
        if state.work_pattern.primary_pattern != WorkPatternType.UNKNOWN:
            confidence_pct = int(state.work_pattern.confidence * 100)
            lines.append(f"\n🎯 Work pattern: {state.work_pattern.primary_pattern.value.title()} ({confidence_pct}% confidence)")
            
            if state.work_pattern.indicators:
                lines.append("   Indicators:")
                for indicator in state.work_pattern.indicators[:3]:  # Show top 3
                    lines.append(f"   • {indicator}")
        
        return "\n".join(lines)


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Git repository state")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to Git repository")
    parser.add_argument("--patterns", help="Path to patterns configuration file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        analyzer = GitStateAnalyzer(args.repo_path, args.patterns)
        state = analyzer.analyze()
        
        if args.json:
            # Convert to JSON-serializable format
            import dataclasses
            state_dict = dataclasses.asdict(state)
            # Convert enums to strings
            for change in state_dict['uncommitted_changes'] + state_dict['staged_changes']:
                change['category'] = change['category'].value
            state_dict['work_pattern']['primary_pattern'] = state_dict['work_pattern']['primary_pattern'].value
            state_dict['change_summary']['files_by_category'] = {
                k.value if hasattr(k, 'value') else str(k): v 
                for k, v in state.change_summary.files_by_category.items()
            }
            
            print(json.dumps(state_dict, indent=2))
        else:
            print(analyzer.get_change_summary_text(state))
    
    except Exception as e:
        logger.error(f"Error analyzing repository: {e}")
        exit(1)


if __name__ == "__main__":
    main()