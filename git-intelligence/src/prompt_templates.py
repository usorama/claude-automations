"""
Prompt Templates - AI-powered prompt templates for commit message generation.

This module provides context-aware prompt templates for different types of commits,
enabling intelligent and consistent commit message generation based on file changes
and repository state.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import re
from pathlib import Path

try:
    from .git_state_analyzer import GitState, FileChange, FileCategory
except ImportError:
    from git_state_analyzer import GitState, FileChange, FileCategory

# Forward reference to avoid circular imports
from enum import Enum

class CommitType(Enum):
    """Standard commit types (duplicated to avoid circular import)."""
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


@dataclass
class TemplateContext:
    """Context information for template generation."""
    commit_type: CommitType
    changes: List[FileChange]
    git_state: GitState
    file_count: int
    primary_files: List[str]
    file_categories: Dict[FileCategory, int]
    scope: Optional[str] = None
    breaking_change: bool = False


class TemplateVariable(Enum):
    """Available template variables."""
    COMMIT_TYPE = "commit_type"
    SCOPE = "scope"
    FILE_COUNT = "file_count"
    PRIMARY_FILES = "primary_files"
    PRIMARY_FILE = "primary_file"
    FILE_LIST = "file_list"
    CATEGORIES = "categories"
    MAIN_CATEGORY = "main_category"
    LINES_ADDED = "lines_added"
    LINES_REMOVED = "lines_removed"
    BRANCH_NAME = "branch_name"
    BREAKING_INDICATOR = "breaking_indicator"


class BaseTemplate(ABC):
    """Base class for commit message templates."""
    
    @abstractmethod
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject line for the commit."""
        pass
    
    @abstractmethod
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for the commit."""
        pass
    
    def replace_variables(self, template: str, context: TemplateContext) -> str:
        """Replace template variables with actual values."""
        replacements = {
            "{{commit_type}}": context.commit_type.value,
            "{{scope}}": context.scope or "",
            "{{file_count}}": str(context.file_count),
            "{{primary_files}}": ", ".join(context.primary_files[:3]),
            "{{primary_file}}": context.primary_files[0] if context.primary_files else "",
            "{{file_list}}": "\n".join(f"- {f}" for f in context.primary_files[:5]),
            "{{main_category}}": max(context.file_categories.keys(), 
                                   key=lambda k: context.file_categories[k]).value if context.file_categories else "unknown",
            "{{lines_added}}": str(context.git_state.change_summary.total_lines_added),
            "{{lines_removed}}": str(context.git_state.change_summary.total_lines_removed),
            "{{branch_name}}": context.git_state.current_branch,
            "{{breaking_indicator}}": "!" if context.breaking_change else "",
        }
        
        result = template
        for var, value in replacements.items():
            result = result.replace(var, value)
        
        return result


class FeatureTemplate(BaseTemplate):
    """Template for feature additions."""
    
    SUBJECT_TEMPLATES = [
        "add {{primary_file}}",
        "implement {{scope}} functionality",
        "add new {{main_category}} feature",
        "introduce {{scope}} component",
        "create {{primary_file}} module"
    ]
    
    BODY_TEMPLATES = [
        "Added {{file_count}} new files implementing {{scope}} functionality:\n{{file_list}}",
        "New feature implementation includes:\n{{file_list}}\n\nTotal changes: +{{lines_added}} lines",
        "Implemented {{scope}} with the following components:\n{{file_list}}"
    ]
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for feature addition."""
        if context.file_count == 1:
            filename = Path(context.primary_files[0]).stem
            if context.scope:
                return f"add {filename} to {context.scope}"
            else:
                return f"add {filename}"
        
        elif context.scope:
            return f"add {context.scope} functionality"
        
        elif context.file_categories:
            main_category = max(context.file_categories.keys(), 
                              key=lambda k: context.file_categories[k])
            return f"add new {main_category.value} feature"
        
        else:
            return "add new feature"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for feature addition."""
        if context.file_count <= 3:
            return None
        
        body_lines = []
        
        if context.scope:
            body_lines.append(f"Implemented {context.scope} with the following components:")
        else:
            body_lines.append("New feature implementation includes:")
        
        body_lines.append("")
        
        # Group files by category
        category_files = {}
        for change in context.changes:
            if change.category not in category_files:
                category_files[change.category] = []
            category_files[change.category].append(change.path)
        
        for category, files in category_files.items():
            body_lines.append(f"{category.value.title()}:")
            for file in files[:3]:  # Limit to 3 files per category
                body_lines.append(f"- {file}")
            if len(files) > 3:
                body_lines.append(f"- ... and {len(files) - 3} more files")
            body_lines.append("")
        
        # Add statistics if significant
        if context.git_state.change_summary.total_lines_added > 50:
            body_lines.append(f"Total additions: +{context.git_state.change_summary.total_lines_added} lines")
        
        return "\n".join(body_lines).strip()


class BugFixTemplate(BaseTemplate):
    """Template for bug fixes."""
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for bug fix."""
        if context.scope:
            return f"fix {context.scope} issue"
        elif context.file_count == 1:
            filename = Path(context.primary_files[0]).stem
            return f"fix {filename} bug"
        else:
            return "fix bug"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for bug fix."""
        if context.file_count <= 2:
            return None
        
        body_lines = []
        
        if context.scope:
            body_lines.append(f"Fixed issue in {context.scope} affecting:")
        else:
            body_lines.append("Bug fix affecting:")
        
        body_lines.append("")
        
        for change in context.changes[:5]:
            body_lines.append(f"- {change.path}")
        
        if context.file_count > 5:
            body_lines.append(f"- ... and {context.file_count - 5} more files")
        
        return "\n".join(body_lines)


class DocsTemplate(BaseTemplate):
    """Template for documentation updates."""
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for documentation update."""
        if context.file_count == 1:
            filename = Path(context.primary_files[0]).name
            if "readme" in filename.lower():
                return "update README"
            elif filename.endswith('.md'):
                return f"update {Path(filename).stem}"
            else:
                return f"update {filename}"
        else:
            return "update documentation"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for documentation update."""
        if context.file_count <= 2:
            return None
        
        body_lines = ["Updated documentation files:", ""]
        
        for change in context.changes[:5]:
            body_lines.append(f"- {change.path}")
        
        if context.file_count > 5:
            body_lines.append(f"- ... and {context.file_count - 5} more files")
        
        return "\n".join(body_lines)


class TestTemplate(BaseTemplate):
    """Template for test additions."""
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for test addition."""
        if context.scope:
            return f"add {context.scope} tests"
        elif context.file_count == 1:
            filename = Path(context.primary_files[0]).stem
            # Remove test prefixes/suffixes for cleaner subject
            clean_name = re.sub(r'(test_|_test|\.test|\.spec)', '', filename)
            return f"add {clean_name} tests"
        else:
            return "add tests"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for test addition."""
        if context.file_count <= 2:
            return None
        
        body_lines = ["Added test coverage for:", ""]
        
        for change in context.changes[:5]:
            # Extract what's being tested from test file name
            filename = Path(change.path).stem
            tested_component = re.sub(r'(test_|_test|\.test|\.spec)', '', filename)
            body_lines.append(f"- {tested_component} ({change.path})")
        
        if context.file_count > 5:
            body_lines.append(f"- ... and {context.file_count - 5} more test files")
        
        return "\n".join(body_lines)


class RefactorTemplate(BaseTemplate):
    """Template for refactoring."""
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for refactoring."""
        if context.scope:
            return f"refactor {context.scope}"
        elif context.file_count == 1:
            filename = Path(context.primary_files[0]).stem
            return f"refactor {filename}"
        else:
            return "refactor code"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for refactoring."""
        if context.file_count <= 3:
            return None
        
        body_lines = []
        
        if context.scope:
            body_lines.append(f"Refactored {context.scope} codebase:")
        else:
            body_lines.append("Code refactoring includes:")
        
        body_lines.append("")
        
        for change in context.changes[:5]:
            body_lines.append(f"- {change.path}")
        
        if context.file_count > 5:
            body_lines.append(f"- ... and {context.file_count - 5} more files")
        
        # Add line change statistics
        lines_added = context.git_state.change_summary.total_lines_added
        lines_removed = context.git_state.change_summary.total_lines_removed
        
        if lines_added > 0 or lines_removed > 0:
            body_lines.append("")
            body_lines.append(f"Changes: +{lines_added}, -{lines_removed} lines")
        
        return "\n".join(body_lines)


class StyleTemplate(BaseTemplate):
    """Template for style/formatting changes."""
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for style changes."""
        if context.scope:
            return f"style: format {context.scope} code"
        else:
            return "style: fix formatting"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for style changes."""
        if context.file_count <= 5:
            return None
        
        body_lines = ["Applied code formatting to:", ""]
        
        for change in context.changes[:5]:
            body_lines.append(f"- {change.path}")
        
        if context.file_count > 5:
            body_lines.append(f"- ... and {context.file_count - 5} more files")
        
        return "\n".join(body_lines)


class BuildTemplate(BaseTemplate):
    """Template for build/configuration changes."""
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for build changes."""
        if any("package.json" in f for f in context.primary_files):
            return "build: update dependencies"
        elif any("webpack" in f.lower() for f in context.primary_files):
            return "build: update webpack config"
        elif any("dockerfile" in f.lower() for f in context.primary_files):
            return "build: update Docker configuration"
        else:
            return "build: update configuration"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for build changes."""
        if context.file_count <= 2:
            return None
        
        body_lines = ["Updated build configuration:", ""]
        
        for change in context.changes:
            body_lines.append(f"- {change.path}")
        
        return "\n".join(body_lines)


class ChoreTemplate(BaseTemplate):
    """Template for chores/maintenance."""
    
    def generate_subject(self, context: TemplateContext) -> str:
        """Generate subject for chores."""
        if context.scope:
            return f"chore: update {context.scope}"
        elif any("config" in f.lower() for f in context.primary_files):
            return "chore: update configuration"
        elif any(".env" in f for f in context.primary_files):
            return "chore: update environment variables"
        else:
            return "chore: maintenance"
    
    def generate_body(self, context: TemplateContext) -> Optional[str]:
        """Generate body for chores."""
        if context.file_count <= 3:
            return None
        
        body_lines = ["Maintenance updates:", ""]
        
        for change in context.changes[:5]:
            body_lines.append(f"- {change.path}")
        
        if context.file_count > 5:
            body_lines.append(f"- ... and {context.file_count - 5} more files")
        
        return "\n".join(body_lines)


class PromptTemplateManager:
    """Manager for commit message templates."""
    
    def __init__(self):
        """Initialize template manager with default templates."""
        self.templates = {
            CommitType.FEAT: FeatureTemplate(),
            CommitType.FIX: BugFixTemplate(),
            CommitType.DOCS: DocsTemplate(),
            CommitType.TEST: TestTemplate(),
            CommitType.REFACTOR: RefactorTemplate(),
            CommitType.STYLE: StyleTemplate(),
            CommitType.BUILD: BuildTemplate(),
            CommitType.CI: BuildTemplate(),  # Use build template for CI
            CommitType.CHORE: ChoreTemplate(),
            CommitType.PERF: RefactorTemplate(),  # Use refactor template for performance
        }
        
        self.custom_templates = {}
    
    def register_template(self, commit_type: CommitType, template: BaseTemplate):
        """Register a custom template for a commit type."""
        self.custom_templates[commit_type] = template
    
    def get_template(
        self,
        commit_type: CommitType,
        changes: List[FileChange],
        git_state: GitState,
        scope: Optional[str] = None,
        breaking_change: bool = False
    ) -> BaseTemplate:
        """
        Get template for the specified commit type.
        
        Args:
            commit_type: Type of commit
            changes: List of file changes
            git_state: Git repository state
            scope: Optional scope
            breaking_change: Whether this is a breaking change
            
        Returns:
            Template instance
        """
        # Use custom template if available
        if commit_type in self.custom_templates:
            return self.custom_templates[commit_type]
        
        # Use default template
        return self.templates.get(commit_type, self.templates[CommitType.CHORE])
    
    def generate_context(
        self,
        commit_type: CommitType,
        changes: List[FileChange],
        git_state: GitState,
        scope: Optional[str] = None,
        breaking_change: bool = False
    ) -> TemplateContext:
        """
        Generate template context from commit information.
        
        Args:
            commit_type: Type of commit
            changes: List of file changes
            git_state: Git repository state
            scope: Optional scope
            breaking_change: Whether this is a breaking change
            
        Returns:
            TemplateContext instance
        """
        from collections import defaultdict
        
        file_count = len(changes)
        primary_files = [change.path for change in changes]
        
        # Count files by category
        file_categories = defaultdict(int)
        for change in changes:
            file_categories[change.category] += 1
        
        return TemplateContext(
            commit_type=commit_type,
            changes=changes,
            git_state=git_state,
            file_count=file_count,
            primary_files=primary_files,
            file_categories=dict(file_categories),
            scope=scope,
            breaking_change=breaking_change
        )
    
    def generate_subject(
        self,
        commit_type: CommitType,
        changes: List[FileChange],
        git_state: GitState,
        scope: Optional[str] = None,
        breaking_change: bool = False
    ) -> str:
        """
        Generate subject line using appropriate template.
        
        Args:
            commit_type: Type of commit
            changes: List of file changes
            git_state: Git repository state
            scope: Optional scope
            breaking_change: Whether this is a breaking change
            
        Returns:
            Generated subject line
        """
        template = self.get_template(commit_type, changes, git_state, scope, breaking_change)
        context = self.generate_context(commit_type, changes, git_state, scope, breaking_change)
        
        return template.generate_subject(context)
    
    def generate_body(
        self,
        commit_type: CommitType,
        changes: List[FileChange],
        git_state: GitState,
        scope: Optional[str] = None,
        breaking_change: bool = False
    ) -> Optional[str]:
        """
        Generate body using appropriate template.
        
        Args:
            commit_type: Type of commit
            changes: List of file changes
            git_state: Git repository state
            scope: Optional scope
            breaking_change: Whether this is a breaking change
            
        Returns:
            Generated body or None
        """
        template = self.get_template(commit_type, changes, git_state, scope, breaking_change)
        context = self.generate_context(commit_type, changes, git_state, scope, breaking_change)
        
        return template.generate_body(context)


def main():
    """Main function for testing templates."""
    from .git_state_analyzer import GitStateAnalyzer, FileChange, FileCategory
    from .commit_generator import CommitType
    
    # Create sample data for testing
    changes = [
        FileChange("src/auth/login.py", "M", FileCategory.SOURCE, 25, 5),
        FileChange("src/auth/models.py", "M", FileCategory.SOURCE, 10, 0),
        FileChange("tests/test_auth.py", "A", FileCategory.TEST, 50, 0),
    ]
    
    # Mock git state
    class MockGitState:
        def __init__(self):
            self.current_branch = "feature/auth-improvements"
            self.change_summary = type('obj', (object,), {
                'total_lines_added': 85,
                'total_lines_removed': 5
            })
    
    git_state = MockGitState()
    
    manager = PromptTemplateManager()
    
    # Test different commit types
    for commit_type in [CommitType.FEAT, CommitType.FIX, CommitType.TEST]:
        print(f"\n=== {commit_type.value.upper()} Template ===")
        
        subject = manager.generate_subject(commit_type, changes, git_state, "auth")
        body = manager.generate_body(commit_type, changes, git_state, "auth")
        
        print(f"Subject: {subject}")
        if body:
            print(f"Body:\n{body}")
        else:
            print("Body: None")


if __name__ == "__main__":
    main()