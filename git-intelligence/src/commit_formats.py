"""
Commit Formats - Implementation of different commit message formats.

This module provides format implementations for various commit message conventions
including Conventional Commits, Semantic Commits, and custom formats with proper
validation and formatting capabilities.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MessageComponents:
    """Components of a commit message."""
    type: str
    scope: Optional[str] = None
    subject: str = ""
    body: Optional[str] = None
    footers: List[str] = None
    breaking_change: bool = False
    
    def __post_init__(self):
        """Initialize default values."""
        if self.footers is None:
            self.footers = []


class BaseCommitFormat(ABC):
    """Base class for commit message formats."""
    
    @abstractmethod
    def format(self, message_builder) -> str:
        """
        Format a commit message using the message builder.
        
        Args:
            message_builder: MessageBuilder instance
            
        Returns:
            Formatted commit message string
        """
        pass
    
    @abstractmethod
    def parse(self, commit_message: str) -> MessageComponents:
        """
        Parse a commit message into components.
        
        Args:
            commit_message: Raw commit message string
            
        Returns:
            MessageComponents object
        """
        pass
    
    @abstractmethod
    def validate(self, commit_message: str) -> bool:
        """
        Validate if commit message follows the format.
        
        Args:
            commit_message: Commit message to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def get_format_name(self) -> str:
        """Get the name of this format."""
        return self.__class__.__name__.replace("Format", "").lower()


class ConventionalCommitFormat(BaseCommitFormat):
    """
    Conventional Commits format implementation.
    
    Format: <type>[optional scope]: <description>
    
    [optional body]
    
    [optional footer(s)]
    """
    
    # Valid commit types for conventional commits
    VALID_TYPES = {
        "feat", "fix", "docs", "style", "refactor", "perf", "test",
        "build", "ci", "chore", "revert"
    }
    
    # Type patterns with descriptions
    TYPE_DESCRIPTIONS = {
        "feat": "A new feature",
        "fix": "A bug fix",
        "docs": "Documentation only changes",
        "style": "Changes that do not affect the meaning of the code",
        "refactor": "A code change that neither fixes a bug nor adds a feature",
        "perf": "A code change that improves performance",
        "test": "Adding missing tests or correcting existing tests",
        "build": "Changes that affect the build system or external dependencies",
        "ci": "Changes to our CI configuration files and scripts",
        "chore": "Other changes that don't modify src or test files",
        "revert": "Reverts a previous commit"
    }
    
    def __init__(self, max_subject_length: int = 50, max_body_width: int = 72):
        """
        Initialize Conventional Commit formatter.
        
        Args:
            max_subject_length: Maximum length for subject line
            max_body_width: Maximum width for body lines
        """
        self.max_subject_length = max_subject_length
        self.max_body_width = max_body_width
        
        # Compiled regex for parsing
        self.header_pattern = re.compile(
            r'^(?P<type>\w+)'
            r'(?:\((?P<scope>[^)]+)\))?'
            r'(?P<breaking>!)?'
            r':\s*'
            r'(?P<subject>.*)$'
        )
    
    def format(self, message_builder) -> str:
        """Format commit message in Conventional Commits style."""
        components = message_builder.get_components()
        
        # Build header
        header_parts = [components.type]
        
        if components.scope:
            header_parts.append(f"({components.scope})")
        
        # Add breaking change indicator
        if components.breaking_change:
            header_parts.append("!")
        
        header_parts.extend([":", " ", components.subject])
        header = "".join(header_parts)
        
        # Truncate header if too long
        if len(header) > self.max_subject_length:
            available_length = self.max_subject_length - len("".join(header_parts[:-1]))
            if available_length > 10:  # Minimum useful subject length
                truncated_subject = components.subject[:available_length - 3] + "..."
                header_parts[-1] = truncated_subject
                header = "".join(header_parts)
        
        # Build full message
        message_parts = [header]
        
        # Add body if present
        if components.body:
            message_parts.append("")  # Empty line
            body_lines = self._wrap_text(components.body, self.max_body_width)
            message_parts.extend(body_lines)
        
        # Add footers if present
        if components.footers:
            if not components.body:
                message_parts.append("")  # Empty line before footers
            message_parts.append("")  # Empty line before footers
            message_parts.extend(components.footers)
        
        return "\n".join(message_parts)
    
    def parse(self, commit_message: str) -> MessageComponents:
        """Parse conventional commit message."""
        lines = commit_message.split('\n')
        
        if not lines:
            return MessageComponents(type="", subject="")
        
        # Parse header
        header_match = self.header_pattern.match(lines[0])
        if not header_match:
            # Fallback for non-conventional commits
            return MessageComponents(type="chore", subject=lines[0])
        
        type_str = header_match.group('type')
        scope = header_match.group('scope')
        breaking = bool(header_match.group('breaking'))
        subject = header_match.group('subject')
        
        # Parse body and footers
        body_lines = []
        footer_lines = []
        
        in_body = False
        in_footers = False
        
        for i, line in enumerate(lines[1:], 1):
            if not line.strip() and not in_body and not in_footers:
                in_body = True
                continue
            
            if in_body and not in_footers:
                # Check if this looks like a footer
                if re.match(r'^[A-Za-z-]+:\s+.+$', line.strip()) or line.startswith('BREAKING CHANGE:'):
                    in_footers = True
                    footer_lines.append(line.strip())
                elif line.strip():
                    body_lines.append(line)
                elif body_lines:  # Empty line in body
                    body_lines.append("")
            
            elif in_footers:
                if line.strip():
                    footer_lines.append(line.strip())
        
        body = "\n".join(body_lines).strip() if body_lines else None
        
        # Check for breaking change in footers
        for footer in footer_lines:
            if footer.startswith('BREAKING CHANGE:'):
                breaking = True
                break
        
        return MessageComponents(
            type=type_str,
            scope=scope,
            subject=subject,
            body=body,
            footers=footer_lines,
            breaking_change=breaking
        )
    
    def validate(self, commit_message: str) -> bool:
        """Validate conventional commit format."""
        if not commit_message.strip():
            return False
        
        lines = commit_message.split('\n')
        header = lines[0]
        
        # Check header format
        if not self.header_pattern.match(header):
            return False
        
        # Extract type and validate
        match = self.header_pattern.match(header)
        commit_type = match.group('type').lower()
        
        if commit_type not in self.VALID_TYPES:
            logger.warning(f"Unknown commit type: {commit_type}")
            return False
        
        # Check subject length
        subject = match.group('subject')
        if len(header) > self.max_subject_length:
            logger.warning(f"Header too long: {len(header)} > {self.max_subject_length}")
            return False
        
        if not subject.strip():
            logger.warning("Empty subject")
            return False
        
        return True
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width."""
        if not text:
            return []
        
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph.strip():
                lines.append("")
                continue
            
            words = paragraph.split()
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word)
                
                if current_length + word_length + len(current_line) <= width:
                    current_line.append(word)
                    current_length += word_length
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = word_length
            
            if current_line:
                lines.append(" ".join(current_line))
        
        return lines


class SemanticCommitFormat(BaseCommitFormat):
    """
    Semantic commit format implementation.
    
    Similar to conventional commits but with more flexible type system
    and additional semantic information.
    """
    
    # Extended set of semantic types
    VALID_TYPES = {
        "add", "remove", "change", "fix", "update", "improve", "refactor",
        "docs", "test", "style", "config", "build", "deploy", "security",
        "performance", "accessibility", "breaking", "deprecate"
    }
    
    def __init__(self, max_subject_length: int = 60, max_body_width: int = 72):
        """
        Initialize Semantic Commit formatter.
        
        Args:
            max_subject_length: Maximum length for subject line
            max_body_width: Maximum width for body lines
        """
        self.max_subject_length = max_subject_length
        self.max_body_width = max_body_width
        
        # Compiled regex for parsing
        self.header_pattern = re.compile(
            r'^(?P<type>\w+)'
            r'(?:\((?P<scope>[^)]+)\))?'
            r':\s*'
            r'(?P<subject>.*)$'
        )
    
    def format(self, message_builder) -> str:
        """Format commit message in Semantic style."""
        components = message_builder.get_components()
        
        # Build header - similar to conventional but more flexible
        header_parts = [components.type]
        
        if components.scope:
            header_parts.append(f"({components.scope})")
        
        header_parts.extend([":", " ", components.subject])
        header = "".join(header_parts)
        
        # Build full message
        message_parts = [header]
        
        # Add body if present
        if components.body:
            message_parts.append("")  # Empty line
            body_lines = self._wrap_text(components.body, self.max_body_width)
            message_parts.extend(body_lines)
        
        # Add breaking change notice if needed
        if components.breaking_change:
            message_parts.append("")
            message_parts.append("BREAKING CHANGE: This commit contains breaking changes")
        
        # Add footers
        if components.footers:
            if not components.body and not components.breaking_change:
                message_parts.append("")
            message_parts.append("")
            message_parts.extend(components.footers)
        
        return "\n".join(message_parts)
    
    def parse(self, commit_message: str) -> MessageComponents:
        """Parse semantic commit message."""
        # Similar to conventional parsing but more lenient
        lines = commit_message.split('\n')
        
        if not lines:
            return MessageComponents(type="", subject="")
        
        # Parse header
        header_match = self.header_pattern.match(lines[0])
        if not header_match:
            return MessageComponents(type="change", subject=lines[0])
        
        type_str = header_match.group('type')
        scope = header_match.group('scope')
        subject = header_match.group('subject')
        
        # Parse body and footers (same as conventional)
        body_lines = []
        footer_lines = []
        breaking_change = False
        
        in_body = False
        in_footers = False
        
        for line in lines[1:]:
            if not line.strip() and not in_body and not in_footers:
                in_body = True
                continue
            
            if "BREAKING CHANGE:" in line:
                breaking_change = True
            
            if in_body and not in_footers:
                if re.match(r'^[A-Za-z-]+:\s+.+$', line.strip()) or "BREAKING CHANGE:" in line:
                    in_footers = True
                    footer_lines.append(line.strip())
                elif line.strip():
                    body_lines.append(line)
                elif body_lines:
                    body_lines.append("")
            elif in_footers and line.strip():
                footer_lines.append(line.strip())
        
        body = "\n".join(body_lines).strip() if body_lines else None
        
        return MessageComponents(
            type=type_str,
            scope=scope,
            subject=subject,
            body=body,
            footers=footer_lines,
            breaking_change=breaking_change
        )
    
    def validate(self, commit_message: str) -> bool:
        """Validate semantic commit format."""
        if not commit_message.strip():
            return False
        
        lines = commit_message.split('\n')
        header = lines[0]
        
        # More flexible validation than conventional
        if not self.header_pattern.match(header):
            return False
        
        # Check length
        if len(header) > self.max_subject_length:
            return False
        
        return True
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width."""
        # Same implementation as conventional
        if not text:
            return []
        
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph.strip():
                lines.append("")
                continue
            
            words = paragraph.split()
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word)
                
                if current_length + word_length + len(current_line) <= width:
                    current_line.append(word)
                    current_length += word_length
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = word_length
            
            if current_line:
                lines.append(" ".join(current_line))
        
        return lines


class CustomFormat(BaseCommitFormat):
    """
    Custom commit format implementation.
    
    Allows users to define their own commit message templates using
    variable substitution.
    """
    
    def __init__(self, template: Optional[str] = None):
        """
        Initialize Custom format with template.
        
        Args:
            template: Custom template string with variables like {{type}}, {{subject}}, etc.
        """
        self.template = template or self._get_default_template()
        self._parse_template()
    
    def _get_default_template(self) -> str:
        """Get default custom template."""
        return """{{type}}{{scope_prefix}}{{scope}}{{scope_suffix}}: {{subject}}

{{body}}

{{footers}}"""
    
    def _parse_template(self):
        """Parse template to identify required variables."""
        self.required_vars = set(re.findall(r'{{(\w+)}}', self.template))
        self.optional_vars = {
            'scope_prefix', 'scope_suffix', 'body', 'footers', 'breaking_prefix'
        }
    
    def format(self, message_builder) -> str:
        """Format commit message using custom template."""
        components = message_builder.get_components()
        
        # Prepare template variables
        template_vars = {
            'type': components.type,
            'subject': components.subject,
            'scope': components.scope or '',
            'scope_prefix': '(' if components.scope else '',
            'scope_suffix': ')' if components.scope else '',
            'body': components.body or '',
            'footers': '\n'.join(components.footers) if components.footers else '',
            'breaking_prefix': '! ' if components.breaking_change else '',
        }
        
        # Replace variables in template
        result = self.template
        for var, value in template_vars.items():
            result = result.replace('{{' + var + '}}', str(value))
        
        # Clean up empty lines
        lines = result.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip() or (cleaned_lines and cleaned_lines[-1].strip()):
                cleaned_lines.append(line)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def parse(self, commit_message: str) -> MessageComponents:
        """Parse custom format commit message."""
        # Basic parsing - extract first line as subject
        lines = commit_message.split('\n')
        
        if not lines:
            return MessageComponents(type="", subject="")
        
        # Try to extract type from first line
        header = lines[0]
        type_match = re.match(r'^(\w+)', header)
        commit_type = type_match.group(1) if type_match else "change"
        
        # Extract scope if present
        scope_match = re.search(r'\(([^)]+)\)', header)
        scope = scope_match.group(1) if scope_match else None
        
        # Subject is everything after the first colon
        colon_pos = header.find(':')
        if colon_pos > 0:
            subject = header[colon_pos + 1:].strip()
        else:
            subject = header
        
        # Body is everything between header and footers
        body_lines = []
        footer_lines = []
        
        in_body = False
        in_footers = False
        
        for line in lines[1:]:
            if not line.strip() and not in_body:
                in_body = True
                continue
            
            if in_body and not in_footers:
                if re.match(r'^[A-Za-z-]+:\s+.+$', line.strip()):
                    in_footers = True
                    footer_lines.append(line.strip())
                elif line.strip():
                    body_lines.append(line)
            elif in_footers and line.strip():
                footer_lines.append(line.strip())
        
        body = '\n'.join(body_lines).strip() if body_lines else None
        
        # Check for breaking changes
        breaking_change = '!' in header or any('BREAKING' in footer for footer in footer_lines)
        
        return MessageComponents(
            type=commit_type,
            scope=scope,
            subject=subject,
            body=body,
            footers=footer_lines,
            breaking_change=breaking_change
        )
    
    def validate(self, commit_message: str) -> bool:
        """Validate custom format."""
        # Basic validation - ensure message is not empty
        if not commit_message.strip():
            return False
        
        lines = commit_message.split('\n')
        if not lines[0].strip():
            return False
        
        # Custom formats are generally more flexible
        return True
    
    def set_template(self, template: str):
        """Update the custom template."""
        self.template = template
        self._parse_template()


def get_format_handler(format_type: str, **kwargs) -> BaseCommitFormat:
    """
    Get format handler for specified format type.
    
    Args:
        format_type: Type of format ("conventional", "semantic", "custom")
        **kwargs: Additional arguments for format initialization
        
    Returns:
        Format handler instance
        
    Raises:
        ValueError: If format type is unknown
    """
    format_handlers = {
        "conventional": ConventionalCommitFormat,
        "semantic": SemanticCommitFormat,
        "custom": CustomFormat
    }
    
    if format_type not in format_handlers:
        raise ValueError(f"Unknown format type: {format_type}. "
                        f"Available: {list(format_handlers.keys())}")
    
    return format_handlers[format_type](**kwargs)


def main():
    """Main function for testing formats."""
    from .message_builder import MessageBuilder
    
    # Test different formats
    formats = [
        ConventionalCommitFormat(),
        SemanticCommitFormat(),
        CustomFormat("{{type}}: {{subject}}\n\n{{body}}")
    ]
    
    for fmt in formats:
        print(f"\n=== {fmt.__class__.__name__} ===")
        
        # Create sample message
        builder = MessageBuilder()
        builder.set_type("feat")
        builder.set_scope("auth")
        builder.set_subject("add user authentication")
        builder.set_body("Implemented JWT-based authentication with refresh tokens")
        builder.add_footer("Closes #123")
        
        # Format and display
        message = fmt.format(builder)
        print("Formatted message:")
        print(message)
        print(f"\nValid: {fmt.validate(message)}")
        
        # Parse back
        parsed = fmt.parse(message)
        print(f"Parsed type: {parsed.type}")
        print(f"Parsed scope: {parsed.scope}")
        print(f"Parsed subject: {parsed.subject}")


if __name__ == "__main__":
    main()