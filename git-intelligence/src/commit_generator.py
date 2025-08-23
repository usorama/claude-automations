"""
Commit Message Generator - Intelligent commit message generation system.

This module provides comprehensive commit message generation using AI-powered analysis
of Git repository state and changes. It supports multiple commit formats and can
generate context-aware commit messages with proper categorization and scope detection.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import logging
from collections import defaultdict

try:
    from .git_state_analyzer import GitState, GitStateAnalyzer, FileChange, FileCategory, WorkPatternType
    from .commit_formats import ConventionalCommitFormat, SemanticCommitFormat, CustomFormat
    from .prompt_templates import PromptTemplateManager
    from .validators import CommitValidator
    from .message_builder import MessageBuilder
except ImportError:
    # Fallback for direct execution
    from git_state_analyzer import GitState, GitStateAnalyzer, FileChange, FileCategory, WorkPatternType
    from commit_formats import ConventionalCommitFormat, SemanticCommitFormat, CustomFormat
    from prompt_templates import PromptTemplateManager
    from validators import CommitValidator
    from message_builder import MessageBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommitType(Enum):
    """Standard commit types."""
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERF = "perf"
    TEST = "test"
    BUILD = "build"
    CI = "ci"
    CHORE = "chore"
    REVERT = "revert"


class ScopeDetectionMode(Enum):
    """Scope detection modes."""
    AUTO = "auto"
    MANUAL = "manual"
    NONE = "none"


@dataclass
class CommitConfig:
    """Configuration for commit message generation."""
    format_type: str = "conventional"  # conventional, semantic, custom
    max_subject_length: int = 50
    max_body_length: int = 72
    include_body: bool = True
    include_footers: bool = True
    scope_detection: ScopeDetectionMode = ScopeDetectionMode.AUTO
    breaking_change_detection: bool = True
    multi_commit_threshold: int = 10  # Split into multiple commits if more files
    custom_format_template: Optional[str] = None
    exclude_patterns: List[str] = field(default_factory=list)
    include_co_authors: bool = False
    co_authors: List[str] = field(default_factory=list)


@dataclass
class CommitSuggestion:
    """Single commit suggestion."""
    type: CommitType
    scope: Optional[str]
    subject: str
    body: Optional[str]
    footers: List[str]
    breaking_change: bool
    files: List[str]
    confidence: float
    formatted_message: str


@dataclass
class CommitSuggestions:
    """Collection of commit suggestions."""
    suggestions: List[CommitSuggestion]
    primary_suggestion: CommitSuggestion
    multi_commit: bool
    total_confidence: float
    analysis_summary: str


class CommitMessageGenerator:
    """
    Intelligent commit message generator.
    
    This class analyzes Git repository state and generates contextually appropriate
    commit messages using configurable formats and AI-powered analysis.
    """
    
    def __init__(
        self,
        repo_path: str = ".",
        config: Optional[CommitConfig] = None,
        git_analyzer: Optional[GitStateAnalyzer] = None
    ):
        """
        Initialize the Commit Message Generator.
        
        Args:
            repo_path: Path to the Git repository
            config: Configuration options
            git_analyzer: Optional GitStateAnalyzer instance
        """
        self.repo_path = Path(repo_path).resolve()
        self.config = config or CommitConfig()
        self.git_analyzer = git_analyzer or GitStateAnalyzer(str(self.repo_path))
        
        # Initialize components
        self.prompt_manager = PromptTemplateManager()
        self.validator = CommitValidator()
        self.message_builder = MessageBuilder()
        
        # Initialize format handlers
        self.format_handlers = {
            "conventional": ConventionalCommitFormat(),
            "semantic": SemanticCommitFormat(),
            "custom": CustomFormat(self.config.custom_format_template)
        }
        
        # Scope detection patterns
        self.scope_patterns = {
            "api": [r"api/", r"endpoint", r"route", r"controller"],
            "ui": [r"components?/", r"views?/", r"pages?/", r"frontend/"],
            "auth": [r"auth", r"login", r"user", r"session"],
            "db": [r"database", r"model", r"migration", r"schema"],
            "config": [r"config", r"settings", r"env"],
            "test": [r"test", r"spec", r"__tests__"],
            "docs": [r"docs?/", r"README", r"\.md$"],
            "core": [r"src/", r"lib/", r"main"],
            "utils": [r"utils?/", r"helpers?/", r"tools?/"],
            "commit": [r"commit", r"message", r"generator"]
        }
    
    def _detect_commit_type(self, git_state: GitState) -> CommitType:
        """
        Detect the most appropriate commit type based on changes.
        
        Args:
            git_state: Git repository state
            
        Returns:
            Detected commit type
        """
        changes = git_state.staged_changes + git_state.uncommitted_changes
        work_pattern = git_state.work_pattern
        
        # Use work pattern as primary indicator
        if work_pattern.primary_pattern == WorkPatternType.FEATURE:
            return CommitType.FEAT
        elif work_pattern.primary_pattern == WorkPatternType.BUGFIX:
            return CommitType.FIX
        elif work_pattern.primary_pattern == WorkPatternType.DOCS:
            return CommitType.DOCS
        elif work_pattern.primary_pattern == WorkPatternType.TESTING:
            return CommitType.TEST
        elif work_pattern.primary_pattern == WorkPatternType.REFACTORING:
            return CommitType.REFACTOR
        elif work_pattern.primary_pattern == WorkPatternType.CONFIG:
            return CommitType.CHORE
        
        # Fallback to file-based detection
        file_categories = defaultdict(int)
        for change in changes:
            file_categories[change.category] += 1
        
        # Determine commit type based on file categories
        if file_categories[FileCategory.TEST] > len(changes) * 0.5:
            return CommitType.TEST
        elif file_categories[FileCategory.DOCS] > len(changes) * 0.5:
            return CommitType.DOCS
        elif file_categories[FileCategory.CONFIG] > len(changes) * 0.5:
            return CommitType.CHORE
        elif file_categories[FileCategory.BUILD] > 0:
            return CommitType.BUILD
        elif any("ci" in change.path.lower() or ".github" in change.path.lower() for change in changes):
            return CommitType.CI
        
        # Default fallback
        return CommitType.CHORE
    
    def _detect_scope(self, changes: List[FileChange]) -> Optional[str]:
        """
        Detect scope from file changes.
        
        Args:
            changes: List of file changes
            
        Returns:
            Detected scope or None
        """
        if self.config.scope_detection == ScopeDetectionMode.NONE:
            return None
        
        scope_scores = defaultdict(int)
        
        for change in changes:
            filepath = change.path.lower()
            
            for scope, patterns in self.scope_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, filepath):
                        scope_scores[scope] += 1
                        break
        
        if not scope_scores:
            return None
        
        # Return scope with highest score, but only if it's significant
        max_scope = max(scope_scores.keys(), key=lambda x: scope_scores[x])
        max_score = scope_scores[max_scope]
        
        # Require at least 30% of files to match the scope
        if max_score >= len(changes) * 0.3:
            return max_scope
        
        return None
    
    def _detect_breaking_changes(self, changes: List[FileChange]) -> bool:
        """
        Detect if changes contain breaking changes.
        
        Args:
            changes: List of file changes
            
        Returns:
            True if breaking changes detected
        """
        if not self.config.breaking_change_detection:
            return False
        
        breaking_patterns = [
            r"BREAKING",
            r"breaking.*change",
            r"remove.*deprecated",
            r"major.*version",
            r"api.*version",
            r"interface.*change"
        ]
        
        for change in changes:
            # Check if any files suggest breaking changes
            filepath = change.path.lower()
            for pattern in breaking_patterns:
                if re.search(pattern, filepath):
                    return True
        
        # TODO: Could analyze actual diff content for breaking changes
        return False
    
    def _generate_subject(
        self,
        commit_type: CommitType,
        scope: Optional[str],
        changes: List[FileChange],
        git_state: GitState
    ) -> str:
        """
        Generate commit subject line.
        
        Args:
            commit_type: Type of commit
            scope: Scope of changes
            changes: List of file changes
            git_state: Git repository state
            
        Returns:
            Generated subject line
        """
        # Get template for commit type
        template = self.prompt_manager.get_template(commit_type, changes, git_state)
        
        # Extract key information
        file_count = len(changes)
        primary_files = [c.path for c in changes[:3]]  # First 3 files
        
        # Generate subject based on commit type
        if commit_type == CommitType.FEAT:
            if scope:
                if file_count == 1:
                    subject = f"add {Path(primary_files[0]).stem} to {scope}"
                else:
                    subject = f"add {scope} functionality"
            else:
                subject = f"add new feature"
        
        elif commit_type == CommitType.FIX:
            if scope:
                subject = f"fix {scope} issue"
            else:
                subject = "fix bug"
        
        elif commit_type == CommitType.DOCS:
            if file_count == 1 and "readme" in primary_files[0].lower():
                subject = "update README"
            else:
                subject = "update documentation"
        
        elif commit_type == CommitType.TEST:
            if scope:
                subject = f"add {scope} tests"
            else:
                subject = "add tests"
        
        elif commit_type == CommitType.REFACTOR:
            if scope:
                subject = f"refactor {scope}"
            else:
                subject = "refactor code"
        
        elif commit_type == CommitType.STYLE:
            subject = "fix code style"
        
        elif commit_type == CommitType.PERF:
            if scope:
                subject = f"improve {scope} performance"
            else:
                subject = "improve performance"
        
        elif commit_type == CommitType.BUILD:
            subject = "update build configuration"
        
        elif commit_type == CommitType.CI:
            subject = "update CI configuration"
        
        else:  # CHORE
            if scope:
                subject = f"update {scope}"
            else:
                subject = "update configuration"
        
        # Truncate if too long
        if len(subject) > self.config.max_subject_length - 20:  # Leave room for type and scope
            subject = subject[:self.config.max_subject_length - 23] + "..."
        
        return subject
    
    def _generate_body(
        self,
        commit_type: CommitType,
        changes: List[FileChange],
        git_state: GitState
    ) -> Optional[str]:
        """
        Generate commit message body.
        
        Args:
            commit_type: Type of commit
            changes: List of file changes
            git_state: Git repository state
            
        Returns:
            Generated body or None
        """
        if not self.config.include_body:
            return None
        
        if len(changes) <= 3:  # Simple changes don't need body
            return None
        
        body_lines = []
        
        # Categorize changes
        categories = defaultdict(list)
        for change in changes:
            categories[change.category].append(change)
        
        # Generate body based on categories
        for category, category_changes in categories.items():
            if len(category_changes) > 1:
                body_lines.append(f"{category.value.title()} changes:")
                for change in category_changes[:5]:  # Limit to 5 per category
                    action = "Added" if change.status == "A" else "Modified" if change.status == "M" else "Deleted"
                    body_lines.append(f"- {action} {change.path}")
                
                if len(category_changes) > 5:
                    body_lines.append(f"- ... and {len(category_changes) - 5} more files")
                body_lines.append("")
        
        # Add statistics if significant
        total_lines = git_state.change_summary.total_lines_added + git_state.change_summary.total_lines_removed
        if total_lines > 100:
            body_lines.append(f"Total changes: +{git_state.change_summary.total_lines_added}, "
                            f"-{git_state.change_summary.total_lines_removed} lines")
        
        body = "\n".join(body_lines).strip()
        return body if body else None
    
    def _generate_footers(
        self,
        breaking_change: bool,
        changes: List[FileChange]
    ) -> List[str]:
        """
        Generate commit footers.
        
        Args:
            breaking_change: Whether this is a breaking change
            changes: List of file changes
            
        Returns:
            List of footer lines
        """
        footers = []
        
        if breaking_change:
            footers.append("BREAKING CHANGE: API changes require migration")
        
        # Add co-authors if configured
        if self.config.include_co_authors and self.config.co_authors:
            for co_author in self.config.co_authors:
                footers.append(f"Co-authored-by: {co_author}")
        
        return footers
    
    def _should_split_commit(self, changes: List[FileChange]) -> bool:
        """
        Determine if changes should be split into multiple commits.
        
        Args:
            changes: List of file changes
            
        Returns:
            True if should split
        """
        if len(changes) < self.config.multi_commit_threshold:
            return False
        
        # Check if changes span multiple categories
        categories = set(change.category for change in changes)
        if len(categories) > 2:
            return True
        
        # Check if changes span multiple scopes
        scopes = set()
        for change in changes:
            scope = self._detect_scope([change])
            if scope:
                scopes.add(scope)
        
        return len(scopes) > 2
    
    def _split_changes(self, changes: List[FileChange]) -> List[List[FileChange]]:
        """
        Split changes into logical commit groups.
        
        Args:
            changes: List of file changes
            
        Returns:
            List of change groups
        """
        # Group by category first
        category_groups = defaultdict(list)
        for change in changes:
            category_groups[change.category].append(change)
        
        # Further split large categories by scope
        split_groups = []
        for category, category_changes in category_groups.items():
            if len(category_changes) <= 5:
                split_groups.append(category_changes)
            else:
                # Split by scope within category
                scope_groups = defaultdict(list)
                for change in category_changes:
                    scope = self._detect_scope([change])
                    scope_groups[scope or "misc"].append(change)
                
                for scope_changes in scope_groups.values():
                    split_groups.append(scope_changes)
        
        return split_groups
    
    def _calculate_confidence(
        self,
        commit_type: CommitType,
        scope: Optional[str],
        work_pattern: WorkPatternType,
        changes: List[FileChange]
    ) -> float:
        """
        Calculate confidence score for commit suggestion.
        
        Args:
            commit_type: Detected commit type
            scope: Detected scope
            work_pattern: Work pattern from analysis
            changes: File changes
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on work pattern alignment
        pattern_type_map = {
            WorkPatternType.FEATURE: CommitType.FEAT,
            WorkPatternType.BUGFIX: CommitType.FIX,
            WorkPatternType.DOCS: CommitType.DOCS,
            WorkPatternType.TESTING: CommitType.TEST,
            WorkPatternType.REFACTORING: CommitType.REFACTOR,
            WorkPatternType.CONFIG: CommitType.CHORE
        }
        
        if pattern_type_map.get(work_pattern) == commit_type:
            confidence += 0.3
        
        # Boost for clear scope detection
        if scope:
            confidence += 0.1
        
        # Boost for consistent file types
        categories = [change.category for change in changes]
        if len(set(categories)) <= 2:  # Max 2 different categories
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def generate_commit_message(
        self,
        git_state: Optional[GitState] = None
    ) -> CommitSuggestions:
        """
        Generate commit message suggestions.
        
        Args:
            git_state: Optional pre-analyzed Git state
            
        Returns:
            CommitSuggestions object
            
        Raises:
            ValueError: If no changes to commit
        """
        # Analyze repository state if not provided
        if git_state is None:
            git_state = self.git_analyzer.analyze()
        
        # Get all changes (staged + uncommitted)
        all_changes = git_state.staged_changes + git_state.uncommitted_changes
        
        if not all_changes:
            raise ValueError("No changes to commit")
        
        # Filter out excluded patterns
        if self.config.exclude_patterns:
            filtered_changes = []
            for change in all_changes:
                excluded = False
                for pattern in self.config.exclude_patterns:
                    if re.search(pattern, change.path):
                        excluded = True
                        break
                if not excluded:
                    filtered_changes.append(change)
            all_changes = filtered_changes
        
        suggestions = []
        
        # Determine if we should split into multiple commits
        if self._should_split_commit(all_changes):
            change_groups = self._split_changes(all_changes)
            multi_commit = True
        else:
            change_groups = [all_changes]
            multi_commit = False
        
        # Generate suggestions for each group
        for i, changes in enumerate(change_groups):
            commit_type = self._detect_commit_type(git_state)
            scope = self._detect_scope(changes)
            breaking_change = self._detect_breaking_changes(changes)
            
            subject = self._generate_subject(commit_type, scope, changes, git_state)
            body = self._generate_body(commit_type, changes, git_state)
            footers = self._generate_footers(breaking_change, changes)
            
            # Build formatted message
            message_builder = MessageBuilder()
            message_builder.set_type(commit_type.value)
            if scope:
                message_builder.set_scope(scope)
            message_builder.set_subject(subject)
            if body:
                message_builder.set_body(body)
            for footer in footers:
                message_builder.add_footer(footer)
            
            # Get format handler and format message
            format_handler = self.format_handlers[self.config.format_type]
            formatted_message = format_handler.format(message_builder)
            
            # Validate message
            validation_result = self.validator.validate(formatted_message, self.config.format_type)
            if not validation_result.is_valid:
                logger.warning(f"Generated message validation failed: {validation_result.errors}")
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                commit_type, scope, git_state.work_pattern.primary_pattern, changes
            )
            
            suggestion = CommitSuggestion(
                type=commit_type,
                scope=scope,
                subject=subject,
                body=body,
                footers=footers,
                breaking_change=breaking_change,
                files=[change.path for change in changes],
                confidence=confidence,
                formatted_message=formatted_message
            )
            
            suggestions.append(suggestion)
        
        # Select primary suggestion (highest confidence or first if tied)
        primary_suggestion = max(suggestions, key=lambda s: s.confidence)
        total_confidence = sum(s.confidence for s in suggestions) / len(suggestions)
        
        # Generate analysis summary
        summary_lines = [
            f"Analyzed {len(all_changes)} changed files",
            f"Detected work pattern: {git_state.work_pattern.primary_pattern.value}",
            f"Generated {len(suggestions)} commit suggestion{'s' if len(suggestions) > 1 else ''}"
        ]
        
        if multi_commit:
            summary_lines.append("Recommending multiple commits for logical separation")
        
        analysis_summary = ". ".join(summary_lines)
        
        return CommitSuggestions(
            suggestions=suggestions,
            primary_suggestion=primary_suggestion,
            multi_commit=multi_commit,
            total_confidence=total_confidence,
            analysis_summary=analysis_summary
        )
    
    def get_formatted_message(self, suggestion: CommitSuggestion) -> str:
        """
        Get formatted commit message for a suggestion.
        
        Args:
            suggestion: Commit suggestion
            
        Returns:
            Formatted commit message
        """
        return suggestion.formatted_message
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration options.
        
        Args:
            **kwargs: Configuration options to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                logger.warning(f"Unknown configuration option: {key}")


def main():
    """Main function for command-line usage."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Generate intelligent commit messages")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to Git repository")
    parser.add_argument("--format", choices=["conventional", "semantic", "custom"], 
                       default="conventional", help="Commit message format")
    parser.add_argument("--max-subject", type=int, default=50, help="Maximum subject length")
    parser.add_argument("--no-body", action="store_true", help="Don't include message body")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--multi-commit", action="store_true", help="Allow multi-commit suggestions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        config = CommitConfig(
            format_type=args.format,
            max_subject_length=args.max_subject,
            include_body=not args.no_body,
            multi_commit_threshold=5 if args.multi_commit else 100
        )
        
        generator = CommitMessageGenerator(args.repo_path, config)
        suggestions = generator.generate_commit_message()
        
        if args.json:
            # Convert to JSON format
            suggestions_dict = {
                "suggestions": [
                    {
                        "type": s.type.value,
                        "scope": s.scope,
                        "subject": s.subject,
                        "body": s.body,
                        "footers": s.footers,
                        "breaking_change": s.breaking_change,
                        "files": s.files,
                        "confidence": s.confidence,
                        "formatted_message": s.formatted_message
                    }
                    for s in suggestions.suggestions
                ],
                "primary_suggestion": {
                    "type": suggestions.primary_suggestion.type.value,
                    "scope": suggestions.primary_suggestion.scope,
                    "subject": suggestions.primary_suggestion.subject,
                    "body": suggestions.primary_suggestion.body,
                    "footers": suggestions.primary_suggestion.footers,
                    "breaking_change": suggestions.primary_suggestion.breaking_change,
                    "files": suggestions.primary_suggestion.files,
                    "confidence": suggestions.primary_suggestion.confidence,
                    "formatted_message": suggestions.primary_suggestion.formatted_message
                },
                "multi_commit": suggestions.multi_commit,
                "total_confidence": suggestions.total_confidence,
                "analysis_summary": suggestions.analysis_summary
            }
            print(json.dumps(suggestions_dict, indent=2))
        else:
            print("=== Commit Message Generator ===")
            print(f"\n{suggestions.analysis_summary}")
            print(f"\nPrimary Suggestion (confidence: {suggestions.primary_suggestion.confidence:.1%}):")
            print("─" * 50)
            print(suggestions.primary_suggestion.formatted_message)
            
            if suggestions.multi_commit and len(suggestions.suggestions) > 1:
                print(f"\n=== Additional Suggestions ({len(suggestions.suggestions) - 1}) ===")
                for i, suggestion in enumerate(suggestions.suggestions[1:], 1):
                    print(f"\nCommit {i + 1} (confidence: {suggestion.confidence:.1%}):")
                    print("─" * 30)
                    print(suggestion.formatted_message)
    
    except Exception as e:
        logger.error(f"Error generating commit message: {e}")
        exit(1)


if __name__ == "__main__":
    main()