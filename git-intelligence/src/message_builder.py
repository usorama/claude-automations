"""
Message Builder - Fluent interface for building commit messages.

This module provides a builder pattern implementation for constructing commit messages
with proper component assembly, template variable replacement, and message enhancement
through a fluent interface.
"""

import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancementType(Enum):
    """Types of message enhancements."""
    CAPITALIZE = "capitalize"
    TRIM_WHITESPACE = "trim_whitespace"
    REMOVE_TRAILING_PERIODS = "remove_trailing_periods"
    FORMAT_LISTS = "format_lists"
    WRAP_LINES = "wrap_lines"
    ADD_PUNCTUATION = "add_punctuation"
    NORMALIZE_SPACING = "normalize_spacing"


@dataclass
class MessageComponents:
    """Components of a commit message."""
    type: str = ""
    scope: Optional[str] = None
    subject: str = ""
    body: Optional[str] = None
    footers: List[str] = field(default_factory=list)
    breaking_change: bool = False
    
    def is_complete(self) -> bool:
        """Check if essential components are present."""
        return bool(self.type and self.subject)
    
    def get_header(self) -> str:
        """Get formatted header line."""
        parts = [self.type]
        
        if self.scope:
            parts.append(f"({self.scope})")
        
        if self.breaking_change:
            parts.append("!")
        
        parts.extend([":", " ", self.subject])
        return "".join(parts)


class MessageBuilder:
    """
    Fluent interface for building commit messages.
    
    Provides a chainable API for constructing commit messages with validation,
    enhancement, and formatting capabilities.
    """
    
    def __init__(self):
        """Initialize message builder."""
        self.components = MessageComponents()
        self.template_variables = {}
        self.enhancements = []
        self.validation_rules = []
        self.max_subject_length = 50
        self.max_body_width = 72
    
    def set_type(self, commit_type: str) -> 'MessageBuilder':
        """
        Set the commit type.
        
        Args:
            commit_type: Type of commit (feat, fix, docs, etc.)
            
        Returns:
            Self for chaining
        """
        self.components.type = commit_type.lower().strip()
        return self
    
    def set_scope(self, scope: str) -> 'MessageBuilder':
        """
        Set the commit scope.
        
        Args:
            scope: Scope of the commit
            
        Returns:
            Self for chaining
        """
        self.components.scope = scope.strip() if scope else None
        return self
    
    def set_subject(self, subject: str) -> 'MessageBuilder':
        """
        Set the commit subject.
        
        Args:
            subject: Subject line of the commit
            
        Returns:
            Self for chaining
        """
        self.components.subject = subject.strip()
        return self
    
    def set_body(self, body: str) -> 'MessageBuilder':
        """
        Set the commit body.
        
        Args:
            body: Body text of the commit
            
        Returns:
            Self for chaining
        """
        self.components.body = body.strip() if body else None
        return self
    
    def add_body_line(self, line: str) -> 'MessageBuilder':
        """
        Add a line to the commit body.
        
        Args:
            line: Line to add to body
            
        Returns:
            Self for chaining
        """
        if not self.components.body:
            self.components.body = line
        else:
            self.components.body += "\n" + line
        return self
    
    def add_footer(self, footer: str) -> 'MessageBuilder':
        """
        Add a footer to the commit message.
        
        Args:
            footer: Footer text
            
        Returns:
            Self for chaining
        """
        if footer.strip():
            self.components.footers.append(footer.strip())
        return self
    
    def add_footers(self, footers: List[str]) -> 'MessageBuilder':
        """
        Add multiple footers to the commit message.
        
        Args:
            footers: List of footer texts
            
        Returns:
            Self for chaining
        """
        for footer in footers:
            self.add_footer(footer)
        return self
    
    def set_breaking_change(self, is_breaking: bool = True) -> 'MessageBuilder':
        """
        Mark as breaking change.
        
        Args:
            is_breaking: Whether this is a breaking change
            
        Returns:
            Self for chaining
        """
        self.components.breaking_change = is_breaking
        return self
    
    def add_breaking_change_footer(self, description: str) -> 'MessageBuilder':
        """
        Add breaking change footer.
        
        Args:
            description: Description of the breaking change
            
        Returns:
            Self for chaining
        """
        self.set_breaking_change(True)
        self.add_footer(f"BREAKING CHANGE: {description}")
        return self
    
    def set_template_variable(self, key: str, value: Any) -> 'MessageBuilder':
        """
        Set a template variable for replacement.
        
        Args:
            key: Variable key
            value: Variable value
            
        Returns:
            Self for chaining
        """
        self.template_variables[key] = str(value)
        return self
    
    def set_template_variables(self, variables: Dict[str, Any]) -> 'MessageBuilder':
        """
        Set multiple template variables.
        
        Args:
            variables: Dictionary of variables
            
        Returns:
            Self for chaining
        """
        for key, value in variables.items():
            self.set_template_variable(key, value)
        return self
    
    def add_enhancement(self, enhancement: EnhancementType) -> 'MessageBuilder':
        """
        Add an enhancement to be applied.
        
        Args:
            enhancement: Type of enhancement
            
        Returns:
            Self for chaining
        """
        if enhancement not in self.enhancements:
            self.enhancements.append(enhancement)
        return self
    
    def set_max_subject_length(self, length: int) -> 'MessageBuilder':
        """
        Set maximum subject line length.
        
        Args:
            length: Maximum length
            
        Returns:
            Self for chaining
        """
        self.max_subject_length = length
        return self
    
    def set_max_body_width(self, width: int) -> 'MessageBuilder':
        """
        Set maximum body line width.
        
        Args:
            width: Maximum width
            
        Returns:
            Self for chaining
        """
        self.max_body_width = width
        return self
    
    def replace_template_variables(self, text: str) -> str:
        """
        Replace template variables in text.
        
        Args:
            text: Text with template variables
            
        Returns:
            Text with variables replaced
        """
        if not self.template_variables:
            return text
        
        result = text
        for key, value in self.template_variables.items():
            # Replace both {{key}} and {key} formats
            result = result.replace(f"{{{{{key}}}}}", value)
            result = result.replace(f"{{{key}}}", value)
        
        return result
    
    def _enhance_text(self, text: str) -> str:
        """Apply enhancements to text."""
        if not text or not self.enhancements:
            return text
        
        result = text
        
        for enhancement in self.enhancements:
            if enhancement == EnhancementType.TRIM_WHITESPACE:
                result = result.strip()
            
            elif enhancement == EnhancementType.CAPITALIZE:
                if result:
                    result = result[0].upper() + result[1:]
            
            elif enhancement == EnhancementType.REMOVE_TRAILING_PERIODS:
                result = result.rstrip('.')
            
            elif enhancement == EnhancementType.ADD_PUNCTUATION:
                if result and not result[-1] in '.!?':
                    result += '.'
            
            elif enhancement == EnhancementType.NORMALIZE_SPACING:
                # Replace multiple spaces with single space
                result = re.sub(r'\s+', ' ', result)
                # Remove spaces before punctuation
                result = re.sub(r'\s+([.!?,:;])', r'\1', result)
            
            elif enhancement == EnhancementType.FORMAT_LISTS:
                # Convert simple lists to proper bullet lists
                lines = result.split('\n')
                formatted_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('-') and not stripped.startswith('*'):
                        # Check if line looks like a list item (starts with number, letter, etc.)
                        if re.match(r'^\d+\.|^[a-zA-Z]\.|^[•·‣]', stripped):
                            formatted_lines.append(f"- {stripped}")
                        else:
                            formatted_lines.append(line)
                    else:
                        formatted_lines.append(line)
                result = '\n'.join(formatted_lines)
        
        return result
    
    def _wrap_lines(self, text: str, width: int) -> str:
        """Wrap text lines to specified width."""
        if not text:
            return text
        
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if not line.strip():
                wrapped_lines.append(line)
                continue
            
            if len(line) <= width:
                wrapped_lines.append(line)
                continue
            
            # Wrap long line
            words = line.split()
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word)
                
                if current_length + word_length + len(current_line) <= width:
                    current_line.append(word)
                    current_length += word_length
                else:
                    if current_line:
                        wrapped_lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
            
            if current_line:
                wrapped_lines.append(' '.join(current_line))
        
        return '\n'.join(wrapped_lines)
    
    def build(self) -> str:
        """
        Build the complete commit message.
        
        Returns:
            Formatted commit message string
            
        Raises:
            ValueError: If required components are missing
        """
        if not self.components.is_complete():
            raise ValueError("Missing required components: type and subject must be set")
        
        # Apply template variable replacement
        enhanced_components = MessageComponents(
            type=self.replace_template_variables(self.components.type),
            scope=self.replace_template_variables(self.components.scope) if self.components.scope else None,
            subject=self.replace_template_variables(self.components.subject),
            body=self.replace_template_variables(self.components.body) if self.components.body else None,
            footers=[self.replace_template_variables(f) for f in self.components.footers],
            breaking_change=self.components.breaking_change
        )
        
        # Apply enhancements
        enhanced_components.type = self._enhance_text(enhanced_components.type)
        enhanced_components.subject = self._enhance_text(enhanced_components.subject)
        
        if enhanced_components.body:
            enhanced_components.body = self._enhance_text(enhanced_components.body)
            if EnhancementType.WRAP_LINES in self.enhancements:
                enhanced_components.body = self._wrap_lines(enhanced_components.body, self.max_body_width)
        
        enhanced_components.footers = [self._enhance_text(f) for f in enhanced_components.footers]
        
        # Build message parts
        message_parts = []
        
        # Header
        header = enhanced_components.get_header()
        
        # Truncate subject if too long
        if len(header) > self.max_subject_length:
            type_scope_part = enhanced_components.type
            if enhanced_components.scope:
                type_scope_part += f"({enhanced_components.scope})"
            if enhanced_components.breaking_change:
                type_scope_part += "!"
            type_scope_part += ": "
            
            available_length = self.max_subject_length - len(type_scope_part)
            if available_length > 10:
                truncated_subject = enhanced_components.subject[:available_length - 3] + "..."
                header = type_scope_part + truncated_subject
        
        message_parts.append(header)
        
        # Body
        if enhanced_components.body:
            message_parts.append("")  # Blank line
            message_parts.append(enhanced_components.body)
        
        # Footers
        if enhanced_components.footers:
            if not enhanced_components.body:
                message_parts.append("")  # Blank line before footers
            message_parts.append("")  # Blank line before footers
            message_parts.extend(enhanced_components.footers)
        
        return '\n'.join(message_parts)
    
    def get_components(self) -> MessageComponents:
        """
        Get the current message components.
        
        Returns:
            MessageComponents object
        """
        return self.components
    
    def validate(self) -> List[str]:
        """
        Validate the current message components.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        if not self.components.type:
            errors.append("Commit type is required")
        
        if not self.components.subject:
            errors.append("Subject is required")
        
        if self.components.subject and len(self.components.get_header()) > self.max_subject_length:
            errors.append(f"Header too long ({len(self.components.get_header())} > {self.max_subject_length})")
        
        return errors
    
    def reset(self) -> 'MessageBuilder':
        """
        Reset the builder to initial state.
        
        Returns:
            Self for chaining
        """
        self.components = MessageComponents()
        self.template_variables.clear()
        self.enhancements.clear()
        return self
    
    def copy(self) -> 'MessageBuilder':
        """
        Create a copy of this builder.
        
        Returns:
            New MessageBuilder instance with same state
        """
        new_builder = MessageBuilder()
        new_builder.components = MessageComponents(
            type=self.components.type,
            scope=self.components.scope,
            subject=self.components.subject,
            body=self.components.body,
            footers=self.components.footers.copy(),
            breaking_change=self.components.breaking_change
        )
        new_builder.template_variables = self.template_variables.copy()
        new_builder.enhancements = self.enhancements.copy()
        new_builder.max_subject_length = self.max_subject_length
        new_builder.max_body_width = self.max_body_width
        return new_builder


class MessageEnhancementPipeline:
    """Pipeline for applying multiple enhancements to commit messages."""
    
    def __init__(self):
        """Initialize enhancement pipeline."""
        self.processors = []
    
    def add_processor(self, processor: Callable[[str], str]) -> 'MessageEnhancementPipeline':
        """
        Add a processing function to the pipeline.
        
        Args:
            processor: Function that takes and returns a string
            
        Returns:
            Self for chaining
        """
        self.processors.append(processor)
        return self
    
    def process(self, message: str) -> str:
        """
        Process message through all processors in order.
        
        Args:
            message: Input message
            
        Returns:
            Processed message
        """
        result = message
        for processor in self.processors:
            try:
                result = processor(result)
            except Exception as e:
                logger.warning(f"Enhancement processor failed: {e}")
        return result


def create_conventional_builder() -> MessageBuilder:
    """
    Create a message builder configured for Conventional Commits.
    
    Returns:
        MessageBuilder configured for Conventional Commits
    """
    return (MessageBuilder()
            .set_max_subject_length(50)
            .set_max_body_width(72)
            .add_enhancement(EnhancementType.TRIM_WHITESPACE)
            .add_enhancement(EnhancementType.NORMALIZE_SPACING))


def create_semantic_builder() -> MessageBuilder:
    """
    Create a message builder configured for Semantic Commits.
    
    Returns:
        MessageBuilder configured for Semantic Commits
    """
    return (MessageBuilder()
            .set_max_subject_length(60)
            .set_max_body_width(72)
            .add_enhancement(EnhancementType.TRIM_WHITESPACE)
            .add_enhancement(EnhancementType.NORMALIZE_SPACING)
            .add_enhancement(EnhancementType.FORMAT_LISTS))


def main():
    """Main function for testing message builder."""
    print("=== Message Builder Test ===\n")
    
    # Test 1: Simple conventional commit
    print("Test 1: Simple conventional commit")
    builder = create_conventional_builder()
    message1 = (builder
                .set_type("feat")
                .set_scope("auth")
                .set_subject("add JWT token validation")
                .build())
    print(message1)
    print("-" * 40)
    
    # Test 2: Complex commit with body and footers
    print("Test 2: Complex commit with body and footers")
    builder = create_conventional_builder()
    message2 = (builder
                .set_type("feat")
                .set_scope("api")
                .set_subject("implement user registration endpoint")
                .set_body("Added new POST /api/users endpoint with validation:\n\n"
                         "- Email format validation\n"
                         "- Password strength requirements\n"
                         "- Duplicate email checking")
                .add_footer("Closes #123")
                .add_footer("Reviewed-by: John Doe <john@example.com>")
                .build())
    print(message2)
    print("-" * 40)
    
    # Test 3: Breaking change
    print("Test 3: Breaking change")
    builder = create_conventional_builder()
    message3 = (builder
                .set_type("feat")
                .set_scope("api")
                .set_subject("change user authentication method")
                .add_breaking_change_footer("Authentication now requires API key")
                .build())
    print(message3)
    print("-" * 40)
    
    # Test 4: Template variables
    print("Test 4: Template variables")
    builder = create_conventional_builder()
    message4 = (builder
                .set_type("fix")
                .set_subject("resolve {{issue_type}} in {{component}}")
                .set_body("Fixed the {{issue_type}} that was causing {{problem}}")
                .set_template_variables({
                    "issue_type": "memory leak",
                    "component": "user service",
                    "problem": "server crashes"
                })
                .build())
    print(message4)
    print("-" * 40)
    
    # Test 5: Enhancement pipeline
    print("Test 5: With enhancements")
    builder = (MessageBuilder()
               .set_type("feat")
               .set_subject("add new feature   ")  # Extra whitespace
               .set_body("this is a long line that should be wrapped because it exceeds the maximum width that we set for body lines in our configuration")
               .add_enhancement(EnhancementType.TRIM_WHITESPACE)
               .add_enhancement(EnhancementType.WRAP_LINES)
               .add_enhancement(EnhancementType.CAPITALIZE)
               .set_max_body_width(50))
    message5 = builder.build()
    print(message5)


if __name__ == "__main__":
    main()