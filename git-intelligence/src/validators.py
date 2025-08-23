"""
Validators - Comprehensive validation system for commit messages.

This module provides validation for different commit message formats and styles,
ensuring compliance with conventional commits, semantic commits, and custom rules.
It includes detailed error reporting and suggestions for fixes.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Callable
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: ValidationSeverity
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    rule_name: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of commit message validation."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    score: float = 0.0  # Quality score from 0.0 to 1.0
    
    def __post_init__(self):
        """Separate issues by severity."""
        self.errors = [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
        self.warnings = [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
        
        # Calculate score based on issues
        error_penalty = len(self.errors) * 0.3
        warning_penalty = len(self.warnings) * 0.1
        self.score = max(0.0, 1.0 - error_penalty - warning_penalty)
        
        # Valid if no errors
        self.is_valid = len(self.errors) == 0


class BaseValidator(ABC):
    """Base class for commit message validators."""
    
    @abstractmethod
    def validate(self, commit_message: str) -> List[ValidationIssue]:
        """
        Validate a commit message.
        
        Args:
            commit_message: Commit message to validate
            
        Returns:
            List of validation issues
        """
        pass
    
    def get_name(self) -> str:
        """Get validator name."""
        return self.__class__.__name__.replace("Validator", "").lower()


class ConventionalCommitValidator(BaseValidator):
    """Validator for Conventional Commits specification."""
    
    # Valid conventional commit types
    VALID_TYPES = {
        "feat", "fix", "docs", "style", "refactor", "perf", "test",
        "build", "ci", "chore", "revert"
    }
    
    # Common typos and their corrections
    TYPE_CORRECTIONS = {
        "feature": "feat",
        "bugfix": "fix",
        "bug": "fix",
        "documentation": "docs",
        "doc": "docs",
        "formatting": "style",
        "tests": "test",
        "testing": "test",
        "config": "chore",
        "configuration": "chore",
        "update": "chore",
        "cleanup": "chore",
    }
    
    def __init__(
        self,
        max_subject_length: int = 50,
        max_line_length: int = 72,
        require_scope: bool = False,
        allowed_scopes: Optional[List[str]] = None
    ):
        """
        Initialize Conventional Commit validator.
        
        Args:
            max_subject_length: Maximum length for subject line
            max_line_length: Maximum length for body lines
            require_scope: Whether scope is required
            allowed_scopes: List of allowed scopes (None for any)
        """
        self.max_subject_length = max_subject_length
        self.max_line_length = max_line_length
        self.require_scope = require_scope
        self.allowed_scopes = set(allowed_scopes) if allowed_scopes else None
        
        # Compile regex patterns
        self.header_pattern = re.compile(
            r'^(?P<type>\w+)'
            r'(?:\((?P<scope>[^)]+)\))?'
            r'(?P<breaking>!)?'
            r':\s*'
            r'(?P<subject>.+)$'
        )
        
        self.footer_pattern = re.compile(r'^[A-Za-z-]+:\s+.+$')
    
    def validate(self, commit_message: str) -> List[ValidationIssue]:
        """Validate conventional commit message."""
        issues = []
        
        if not commit_message.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Commit message cannot be empty",
                rule_name="empty_message"
            ))
            return issues
        
        lines = commit_message.split('\n')
        header = lines[0]
        
        # Validate header format
        issues.extend(self._validate_header(header))
        
        # Validate body and footers if present
        if len(lines) > 1:
            issues.extend(self._validate_body_and_footers(lines[1:]))
        
        # Check for common issues
        issues.extend(self._check_common_issues(commit_message))
        
        return issues
    
    def _validate_header(self, header: str) -> List[ValidationIssue]:
        """Validate the header line."""
        issues = []
        
        # Check header format
        match = self.header_pattern.match(header)
        if not match:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Header does not match conventional commit format",
                line_number=1,
                rule_name="header_format",
                suggestion="Use format: type(scope): description"
            ))
            return issues  # Can't continue without valid header
        
        commit_type = match.group('type').lower()
        scope = match.group('scope')
        subject = match.group('subject')
        
        # Validate type
        if commit_type not in self.VALID_TYPES:
            suggestion = None
            if commit_type in self.TYPE_CORRECTIONS:
                suggestion = f"Did you mean '{self.TYPE_CORRECTIONS[commit_type]}'?"
            
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Invalid commit type '{commit_type}'",
                line_number=1,
                rule_name="invalid_type",
                suggestion=suggestion
            ))
        
        # Validate scope
        if self.require_scope and not scope:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Scope is required but not provided",
                line_number=1,
                rule_name="missing_scope"
            ))
        
        if scope and self.allowed_scopes and scope not in self.allowed_scopes:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Scope '{scope}' is not in allowed scopes",
                line_number=1,
                rule_name="invalid_scope",
                suggestion=f"Allowed scopes: {', '.join(sorted(self.allowed_scopes))}"
            ))
        
        # Validate subject
        if not subject.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Subject cannot be empty",
                line_number=1,
                rule_name="empty_subject"
            ))
        
        if len(header) > self.max_subject_length:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Header too long ({len(header)} > {self.max_subject_length})",
                line_number=1,
                rule_name="header_too_long",
                suggestion="Shorten the subject line"
            ))
        
        # Style checks
        if subject and subject[0].isupper():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Subject should start with lowercase letter",
                line_number=1,
                rule_name="subject_case",
                suggestion="Use lowercase for the first letter"
            ))
        
        if subject and subject.endswith('.'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Subject should not end with period",
                line_number=1,
                rule_name="subject_period",
                suggestion="Remove trailing period"
            ))
        
        return issues
    
    def _validate_body_and_footers(self, lines: List[str]) -> List[ValidationIssue]:
        """Validate body and footer lines."""
        issues = []
        
        # Skip empty line after header
        start_idx = 0
        while start_idx < len(lines) and not lines[start_idx].strip():
            start_idx += 1
        
        if start_idx == 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Missing blank line after header",
                line_number=2,
                rule_name="missing_blank_line",
                suggestion="Add blank line between header and body"
            ))
        
        # Check line lengths
        for i, line in enumerate(lines, 2):
            if len(line) > self.max_line_length:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Line too long ({len(line)} > {self.max_line_length})",
                    line_number=i,
                    rule_name="line_too_long",
                    suggestion="Wrap long lines"
                ))
        
        # Validate footer format
        in_footer = False
        for i, line in enumerate(lines, 2):
            if line.strip():
                # Check if this looks like a footer
                if self.footer_pattern.match(line.strip()) or line.startswith('BREAKING CHANGE:'):
                    in_footer = True
                elif in_footer:
                    # We're in footer section but this doesn't look like a footer
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message="Invalid footer format",
                        line_number=i,
                        rule_name="invalid_footer",
                        suggestion="Use format 'Key: value' or 'BREAKING CHANGE: description'"
                    ))
        
        return issues
    
    def _check_common_issues(self, commit_message: str) -> List[ValidationIssue]:
        """Check for common commit message issues."""
        issues = []
        
        # Check for imperative mood
        lines = commit_message.split('\n')
        if lines:
            subject = lines[0].split(':', 1)[-1].strip()
            if subject:
                # Common non-imperative indicators
                non_imperative = ['added', 'updated', 'fixed', 'removed', 'changed']
                first_word = subject.split()[0].lower()
                
                if first_word in non_imperative:
                    imperative_form = {
                        'added': 'add',
                        'updated': 'update',
                        'fixed': 'fix',
                        'removed': 'remove',
                        'changed': 'change'
                    }.get(first_word, first_word[:-2])  # Remove 'ed'
                    
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        message=f"Consider using imperative mood",
                        line_number=1,
                        rule_name="imperative_mood",
                        suggestion=f"Use '{imperative_form}' instead of '{first_word}'"
                    ))
        
        # Check for personal pronouns
        personal_pronouns = ['I', 'we', 'my', 'our']
        for pronoun in personal_pronouns:
            if re.search(rf'\b{pronoun}\b', commit_message, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message=f"Avoid personal pronouns like '{pronoun}'",
                    rule_name="personal_pronouns",
                    suggestion="Use impersonal language"
                ))
                break
        
        return issues


class SemanticCommitValidator(BaseValidator):
    """Validator for Semantic Commits."""
    
    VALID_TYPES = {
        "add", "remove", "change", "fix", "update", "improve", "refactor",
        "docs", "test", "style", "config", "build", "deploy", "security",
        "performance", "accessibility", "breaking", "deprecate"
    }
    
    def __init__(self, max_subject_length: int = 60, max_line_length: int = 72):
        """Initialize Semantic Commit validator."""
        self.max_subject_length = max_subject_length
        self.max_line_length = max_line_length
        
        self.header_pattern = re.compile(
            r'^(?P<type>\w+)'
            r'(?:\((?P<scope>[^)]+)\))?'
            r':\s*'
            r'(?P<subject>.+)$'
        )
    
    def validate(self, commit_message: str) -> List[ValidationIssue]:
        """Validate semantic commit message."""
        issues = []
        
        if not commit_message.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Commit message cannot be empty",
                rule_name="empty_message"
            ))
            return issues
        
        lines = commit_message.split('\n')
        header = lines[0]
        
        # Validate header
        match = self.header_pattern.match(header)
        if not match:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Header does not match semantic commit format",
                line_number=1,
                rule_name="header_format"
            ))
            return issues
        
        commit_type = match.group('type').lower()
        subject = match.group('subject')
        
        # Validate type (more lenient than conventional)
        if commit_type not in self.VALID_TYPES:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Uncommon commit type '{commit_type}'",
                line_number=1,
                rule_name="uncommon_type"
            ))
        
        # Validate subject length
        if len(header) > self.max_subject_length:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Header too long ({len(header)} > {self.max_subject_length})",
                line_number=1,
                rule_name="header_too_long"
            ))
        
        # Check line lengths in body
        for i, line in enumerate(lines[1:], 2):
            if len(line) > self.max_line_length:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message=f"Line too long ({len(line)} > {self.max_line_length})",
                    line_number=i,
                    rule_name="line_too_long"
                ))
        
        return issues


class CustomRuleValidator(BaseValidator):
    """Validator for custom rules."""
    
    def __init__(self):
        """Initialize custom rule validator."""
        self.rules = []
    
    def add_rule(
        self,
        name: str,
        check_function: Callable[[str], bool],
        message: str,
        severity: ValidationSeverity = ValidationSeverity.WARNING,
        suggestion: Optional[str] = None
    ):
        """
        Add a custom validation rule.
        
        Args:
            name: Rule name
            check_function: Function that takes commit message and returns True if valid
            message: Error message for rule violation
            severity: Severity level
            suggestion: Optional suggestion for fixing
        """
        self.rules.append({
            'name': name,
            'check': check_function,
            'message': message,
            'severity': severity,
            'suggestion': suggestion
        })
    
    def validate(self, commit_message: str) -> List[ValidationIssue]:
        """Validate using custom rules."""
        issues = []
        
        for rule in self.rules:
            if not rule['check'](commit_message):
                issues.append(ValidationIssue(
                    severity=rule['severity'],
                    message=rule['message'],
                    rule_name=rule['name'],
                    suggestion=rule['suggestion']
                ))
        
        return issues


class CommitValidator:
    """Main commit message validator that coordinates different validators."""
    
    def __init__(self):
        """Initialize commit validator."""
        self.validators = {}
        self.custom_validator = CustomRuleValidator()
        
        # Register default validators
        self.register_validator('conventional', ConventionalCommitValidator())
        self.register_validator('semantic', SemanticCommitValidator())
        self.register_validator('custom', self.custom_validator)
    
    def register_validator(self, name: str, validator: BaseValidator):
        """Register a validator."""
        self.validators[name] = validator
    
    def add_custom_rule(
        self,
        name: str,
        check_function: Callable[[str], bool],
        message: str,
        severity: ValidationSeverity = ValidationSeverity.WARNING,
        suggestion: Optional[str] = None
    ):
        """Add a custom validation rule."""
        self.custom_validator.add_rule(name, check_function, message, severity, suggestion)
    
    def validate(
        self,
        commit_message: str,
        format_type: str = 'conventional',
        include_custom: bool = True
    ) -> ValidationResult:
        """
        Validate commit message using specified format and custom rules.
        
        Args:
            commit_message: Commit message to validate
            format_type: Type of format validation ('conventional', 'semantic')
            include_custom: Whether to include custom rule validation
            
        Returns:
            ValidationResult object
        """
        all_issues = []
        
        # Run format-specific validation
        if format_type in self.validators:
            format_validator = self.validators[format_type]
            issues = format_validator.validate(commit_message)
            all_issues.extend(issues)
        else:
            logger.warning(f"Unknown format type: {format_type}")
        
        # Run custom rules if requested
        if include_custom:
            custom_issues = self.custom_validator.validate(commit_message)
            all_issues.extend(custom_issues)
        
        return ValidationResult(
            is_valid=not any(issue.severity == ValidationSeverity.ERROR for issue in all_issues),
            issues=all_issues
        )
    
    def get_format_validator(self, format_type: str) -> Optional[BaseValidator]:
        """Get validator for specific format."""
        return self.validators.get(format_type)


def create_common_rules() -> List[tuple]:
    """Create common custom validation rules."""
    rules = []
    
    # Rule: No WIP commits
    rules.append((
        "no_wip",
        lambda msg: "wip" not in msg.lower() and "work in progress" not in msg.lower(),
        "Commit messages should not contain WIP or 'work in progress'",
        ValidationSeverity.WARNING,
        "Complete the work before committing"
    ))
    
    # Rule: Minimum length
    rules.append((
        "minimum_length",
        lambda msg: len(msg.split('\n')[0]) >= 10,
        "Header should be at least 10 characters",
        ValidationSeverity.WARNING,
        "Provide more descriptive commit message"
    ))
    
    # Rule: No trailing whitespace
    rules.append((
        "no_trailing_whitespace",
        lambda msg: all(not line.endswith(' ') and not line.endswith('\t') 
                       for line in msg.split('\n')),
        "Lines should not have trailing whitespace",
        ValidationSeverity.INFO,
        "Remove trailing spaces and tabs"
    ))
    
    # Rule: No merge commit messages
    rules.append((
        "no_merge_commits",
        lambda msg: not msg.startswith("Merge "),
        "Avoid merge commit messages",
        ValidationSeverity.INFO,
        "Use rebase instead of merge"
    ))
    
    return rules


def main():
    """Main function for testing validators."""
    # Test messages
    test_messages = [
        "feat: add user authentication",  # Valid conventional
        "feat(auth): add JWT token validation",  # Valid with scope
        "Feature: Add new user auth",  # Invalid type
        "fix: this is a very long subject line that exceeds the maximum length limit",  # Too long
        "fix: \n\nFixed the bug where users couldn't login properly",  # Missing blank line
        "add: new feature",  # Valid semantic
        "",  # Empty
    ]
    
    validator = CommitValidator()
    
    # Add some custom rules
    for rule in create_common_rules():
        validator.add_custom_rule(*rule)
    
    print("=== Commit Message Validation ===\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {repr(message)}")
        
        # Test conventional format
        result = validator.validate(message, 'conventional')
        
        print(f"Valid: {result.is_valid}")
        print(f"Score: {result.score:.2f}")
        
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error.message}")
                if error.suggestion:
                    print(f"    Suggestion: {error.suggestion}")
        
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning.message}")
                if warning.suggestion:
                    print(f"    Suggestion: {warning.suggestion}")
        
        print("-" * 50)


if __name__ == "__main__":
    main()