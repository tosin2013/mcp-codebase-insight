"""API request and response models."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ToolRequest(BaseModel):
    """Base request model for tool endpoints."""
    name: str
    arguments: Dict[str, Any]

class CrawlDocsRequest(BaseModel):
    """Request model for crawl-docs endpoint."""
    urls: List[str]
    source_type: str

class AnalyzeCodeRequest(BaseModel):
    """Request model for analyze-code endpoint."""
    code: str
    context: Dict[str, Any]

class SearchKnowledgeRequest(BaseModel):
    """Request model for search-knowledge endpoint."""
    query: str
    pattern_type: str
    limit: int = 5

class CodeAnalysisRequest(BaseModel):
    """Code analysis request model."""
    
    code: str
    context: Optional[Dict[str, Any]] = None 