"""Prompt management and generation."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.knowledge import KnowledgeBase, Pattern
from mcp_codebase_insight.core.errors import ValidationError
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class PromptType(str, Enum):
    """Types of prompts."""
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE = "architecture"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REFACTORING = "refactoring"

@dataclass
class PromptContext:
    """Context for prompt generation."""
    type: PromptType
    input_text: str
    patterns: List[Pattern]
    metadata: Dict[str, Any]

class PromptManager:
    """Manager for prompt generation and templates."""

    def __init__(self, config: ServerConfig, knowledge_base: KnowledgeBase):
        """Initialize prompt manager."""
        self.config = config
        self.knowledge_base = knowledge_base
        self._load_templates()

    def _load_templates(self):
        """Load prompt templates."""
        self.templates = {
            PromptType.CODE_ANALYSIS: """
Analyze the following code for patterns, best practices, and potential improvements:

{input_text}

Consider these relevant patterns:
{patterns}

Focus on:
- Code organization and structure
- Design patterns and principles
- Error handling and edge cases
- Performance considerations
- Security implications
- Documentation and readability

Additional context:
{metadata}
""",
            PromptType.ARCHITECTURE: """
Review the following architectural design:

{input_text}

Consider these relevant patterns:
{patterns}

Evaluate:
- Component relationships and dependencies
- Scalability and maintainability
- Integration points and interfaces
- Data flow and state management
- Security and compliance
- Deployment and operations

Additional context:
{metadata}
""",
            PromptType.DEBUGGING: """
Debug the following issue:

{input_text}

Consider these relevant patterns:
{patterns}

Analyze:
- Error symptoms and triggers
- System state and context
- Component interactions
- Data validation and processing
- Resource usage and timing
- Error handling and logging

Additional context:
{metadata}
""",
            PromptType.DOCUMENTATION: """
Generate documentation for:

{input_text}

Consider these relevant patterns:
{patterns}

Include:
- Overview and purpose
- Installation and setup
- Usage examples and APIs
- Configuration options
- Common issues and solutions
- Security considerations

Additional context:
{metadata}
""",
            PromptType.TESTING: """
Design tests for:

{input_text}

Consider these relevant patterns:
{patterns}

Cover:
- Unit tests and integration tests
- Edge cases and error conditions
- Performance benchmarks
- Security testing
- Mocking and test data
- CI/CD integration

Additional context:
{metadata}
""",
            PromptType.REFACTORING: """
Suggest refactoring improvements for:

{input_text}

Consider these relevant patterns:
{patterns}

Focus on:
- Code duplication and complexity
- Design patterns and principles
- Performance optimization
- Error handling
- Maintainability and readability
- Test coverage

Additional context:
{metadata}
"""
        }

    def _format_patterns(self, patterns: List[Pattern]) -> str:
        """Format patterns for prompt inclusion."""
        if not patterns:
            return "No relevant patterns found."
        
        formatted = []
        for p in patterns:
            formatted.append(f"""
Pattern: {p.name}
Type: {p.type.value}
Confidence: {p.confidence.value}
Description: {p.description}
Examples:
{chr(10).join(f'- {e}' for e in p.examples)}
""")
        return "\n".join(formatted)

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for prompt inclusion."""
        if not metadata:
            return "No additional context provided."
        
        formatted = []
        for k, v in metadata.items():
            formatted.append(f"{k}: {v}")
        return "\n".join(formatted)

    async def generate_prompt(
        self,
        type: PromptType,
        input_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a prompt with context."""
        try:
            if not input_text.strip():
                raise ValidationError("Input text cannot be empty")
            
            # Find relevant patterns
            patterns = await self.knowledge_base.find_similar_patterns(
                text=input_text,
                type=type,
                limit=3
            )
            
            # Create context
            context = PromptContext(
                type=type,
                input_text=input_text,
                patterns=patterns,
                metadata=metadata or {}
            )
            
            # Get template
            template = self.templates.get(type)
            if not template:
                raise ValidationError(f"Unknown prompt type: {type}")
            
            # Format prompt
            prompt = template.format(
                input_text=input_text,
                patterns=self._format_patterns(patterns),
                metadata=self._format_metadata(metadata or {})
            )
            
            return prompt.strip()
        except Exception as e:
            logger.error(f"Failed to generate prompt: {e}")
            raise
