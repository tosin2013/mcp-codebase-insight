"""Prompt management and generation module."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

class PromptType(str, Enum):
    """Prompt type enumeration."""
    
    CODE_ANALYSIS = "code_analysis"
    PATTERN_EXTRACTION = "pattern_extraction"
    DOCUMENTATION = "documentation"
    DEBUG = "debug"
    ADR = "adr"

class PromptTemplate(BaseModel):
    """Prompt template model."""
    
    id: UUID
    name: str
    type: PromptType
    template: str
    description: Optional[str] = None
    variables: List[str]
    examples: Optional[List[Dict]] = None
    created_at: datetime
    updated_at: datetime
    version: Optional[str] = None

class PromptManager:
    """Manager for prompt templates and generation."""
    
    def __init__(self, config):
        """Initialize prompt manager."""
        self.config = config
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default prompt templates."""
        # Code Analysis Templates
        self.add_template(
            name="code_pattern_analysis",
            type=PromptType.CODE_ANALYSIS,
            template="""Analyze the following code for patterns and best practices:

Code:
{code}

Consider:
- Design patterns used
- Architecture patterns
- Code organization
- Error handling
- Performance considerations
- Security implications

Provide detailed analysis focusing on:
{focus_areas}""",
            variables=["code", "focus_areas"],
            description="Template for analyzing code patterns"
        )
        
        # Pattern Extraction Templates
        self.add_template(
            name="extract_design_patterns",
            type=PromptType.PATTERN_EXTRACTION,
            template="""Extract design patterns from the following code:

Code:
{code}

Look for instances of:
- Creational patterns
- Structural patterns
- Behavioral patterns
- Architectural patterns

For each pattern found, explain:
- Pattern name and category
- How it's implemented
- Benefits and tradeoffs
- Potential improvements""",
            variables=["code"],
            description="Template for extracting design patterns"
        )
        
        # Documentation Templates
        self.add_template(
            name="generate_documentation",
            type=PromptType.DOCUMENTATION,
            template="""Generate documentation for the following code:

Code:
{code}

Documentation type: {doc_type}
Include:
- Overview
- Usage examples
- API reference
- Dependencies
- Configuration
- Error handling
- Best practices""",
            variables=["code", "doc_type"],
            description="Template for generating documentation"
        )
        
        # Debug Templates
        self.add_template(
            name="debug_analysis",
            type=PromptType.DEBUG,
            template="""Analyze the following issue:

Description:
{description}

Error:
{error}

Context:
{context}

Provide:
- Root cause analysis
- Potential solutions
- Prevention strategies
- Testing recommendations""",
            variables=["description", "error", "context"],
            description="Template for debug analysis"
        )
        
        # ADR Templates
        self.add_template(
            name="adr_template",
            type=PromptType.ADR,
            template="""# Architecture Decision Record

## Title: {title}

## Status: {status}

## Context
{context}

## Decision Drivers
{decision_drivers}

## Considered Options
{options}

## Decision
{decision}

## Consequences
{consequences}

## Implementation
{implementation}

## Related Decisions
{related_decisions}""",
            variables=[
                "title", "status", "context", "decision_drivers",
                "options", "decision", "consequences", "implementation",
                "related_decisions"
            ],
            description="Template for architecture decision records"
        )
    
    def add_template(
        self,
        name: str,
        type: PromptType,
        template: str,
        variables: List[str],
        description: Optional[str] = None,
        examples: Optional[List[Dict]] = None,
        version: Optional[str] = None
    ) -> PromptTemplate:
        """Add a new prompt template."""
        now = datetime.utcnow()
        template = PromptTemplate(
            id=uuid4(),
            name=name,
            type=type,
            template=template,
            description=description,
            variables=variables,
            examples=examples,
            version=version,
            created_at=now,
            updated_at=now
        )
        
        self.templates[name] = template
        return template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get prompt template by name."""
        return self.templates.get(name)
    
    def list_templates(
        self,
        type: Optional[PromptType] = None
    ) -> List[PromptTemplate]:
        """List all templates, optionally filtered by type."""
        templates = list(self.templates.values())
        if type:
            templates = [t for t in templates if t.type == type]
        return sorted(templates, key=lambda x: x.name)
    
    def generate_prompt(
        self,
        template_name: str,
        variables: Dict[str, str]
    ) -> Optional[str]:
        """Generate prompt from template and variables."""
        template = self.get_template(template_name)
        if not template:
            return None
            
        # Validate variables
        missing = [v for v in template.variables if v not in variables]
        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")
            
        try:
            return template.template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Invalid variable: {e}")
        except Exception as e:
            raise ValueError(f"Error generating prompt: {e}")
    
    def update_template(
        self,
        name: str,
        template: Optional[str] = None,
        description: Optional[str] = None,
        examples: Optional[List[Dict]] = None,
        version: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        """Update prompt template."""
        tmpl = self.get_template(name)
        if not tmpl:
            return None
            
        if template:
            tmpl.template = template
        if description:
            tmpl.description = description
        if examples:
            tmpl.examples = examples
        if version:
            tmpl.version = version
            
        tmpl.updated_at = datetime.utcnow()
        return tmpl
