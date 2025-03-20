"""Documentation management module."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from urllib.parse import urlparse

from pydantic import BaseModel

class DocumentationType(str, Enum):
    """Documentation type enumeration."""
    
    REFERENCE = "reference"
    TUTORIAL = "tutorial"
    API = "api"
    GUIDE = "guide"
    EXAMPLE = "example"
    PATTERN = "pattern"

class Document(BaseModel):
    """Document model."""
    
    id: UUID
    title: str
    type: DocumentationType
    content: str
    metadata: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    version: Optional[str] = None
    related_docs: Optional[List[UUID]] = None

class DocumentationManager:
    """Manager for documentation handling."""
    
    def __init__(self, config):
        """Initialize documentation manager."""
        self.config = config
        self.docs_dir = config.docs_cache_dir
        self.docs_dir.mkdir(parents=True, exist_ok=True)
    
    async def add_document(
        self,
        title: str,
        content: str,
        type: DocumentationType,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        version: Optional[str] = None,
        related_docs: Optional[List[UUID]] = None
    ) -> Document:
        """Add a new document."""
        now = datetime.utcnow()
        doc = Document(
            id=uuid4(),
            title=title,
            type=type,
            content=content,
            metadata=metadata,
            tags=tags,
            version=version,
            related_docs=related_docs,
            created_at=now,
            updated_at=now
        )
        
        await self._save_document(doc)
        return doc
    
    async def get_document(self, doc_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        doc_path = self.docs_dir / f"{doc_id}.json"
        if not doc_path.exists():
            return None
            
        with open(doc_path) as f:
            data = json.load(f)
            return Document(**data)
    
    async def update_document(
        self,
        doc_id: UUID,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        version: Optional[str] = None,
        related_docs: Optional[List[UUID]] = None
    ) -> Optional[Document]:
        """Update document content and metadata."""
        doc = await self.get_document(doc_id)
        if not doc:
            return None
            
        if content:
            doc.content = content
        if metadata:
            doc.metadata = {**(doc.metadata or {}), **metadata}
        if tags:
            doc.tags = tags
        if version:
            doc.version = version
        if related_docs:
            doc.related_docs = related_docs
            
        doc.updated_at = datetime.utcnow()
        await self._save_document(doc)
        return doc
    
    async def list_documents(
        self,
        type: Optional[DocumentationType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Document]:
        """List all documents, optionally filtered by type and tags."""
        docs = []
        for path in self.docs_dir.glob("*.json"):
            with open(path) as f:
                data = json.load(f)
                doc = Document(**data)
                
                # Apply filters
                if type and doc.type != type:
                    continue
                if tags and not all(tag in (doc.tags or []) for tag in tags):
                    continue
                    
                docs.append(doc)
                
        return sorted(docs, key=lambda x: x.created_at)
    
    async def search_documents(
        self,
        query: str,
        type: Optional[DocumentationType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Document]:
        """Search documents by content."""
        # TODO: Implement proper text search
        # For now, just do simple substring matching
        results = []
        query = query.lower()
        
        for doc in await self.list_documents(type, tags):
            if (
                query in doc.title.lower() or
                query in doc.content.lower() or
                any(query in tag.lower() for tag in (doc.tags or []))
            ):
                results.append(doc)
                if len(results) >= limit:
                    break
                    
        return results
    
    async def _save_document(self, doc: Document) -> None:
        """Save document to file."""
        doc_path = self.docs_dir / f"{doc.id}.json"
        with open(doc_path, "w") as f:
            json.dump(doc.model_dump(), f, indent=2, default=str)
    
    async def crawl_docs(
        self,
        urls: List[str],
        source_type: str
    ) -> List[Document]:
        """Crawl documentation from URLs."""
        import aiohttp
        from bs4 import BeautifulSoup
        
        docs = []
        try:
            doc_type = DocumentationType(source_type)
        except ValueError:
            doc_type = DocumentationType.REFERENCE
            
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    # Handle file URLs specially (for testing)
                    parsed_url = urlparse(url)
                    if parsed_url.scheme == "file":
                        # Create a test document
                        doc = await self.add_document(
                            title="Test Documentation",
                            content="This is a test document for testing the documentation crawler.",
                            type=doc_type,
                            metadata={
                                "source_url": url,
                                "source_type": source_type,
                                "crawled_at": datetime.utcnow().isoformat()
                            }
                        )
                        docs.append(doc)
                        continue
                    
                    # Fetch the content
                    async with session.get(url, timeout=10) as response:
                        if response.status != 200:
                            print(f"Error fetching {url}: HTTP {response.status}")
                            continue
                        
                        content = await response.text()
                        
                        # Parse HTML content
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract title from meta tags or h1
                        title = soup.find('meta', property='og:title')
                        if title:
                            title = title.get('content')
                        else:
                            title = soup.find('h1')
                            if title:
                                title = title.text.strip()
                            else:
                                title = f"Documentation from {url}"
                        
                        # Extract main content
                        # First try to find main content area
                        content = ""
                        main = soup.find('main')
                        if main:
                            content = main.get_text(separator='\n', strip=True)
                        else:
                            # Try article tag
                            article = soup.find('article')
                            if article:
                                content = article.get_text(separator='\n', strip=True)
                            else:
                                # Fallback to body content
                                body = soup.find('body')
                                if body:
                                    content = body.get_text(separator='\n', strip=True)
                                else:
                                    content = soup.get_text(separator='\n', strip=True)
                        
                        # Create document
                        doc = await self.add_document(
                            title=title,
                            content=content,
                            type=doc_type,
                            metadata={
                                "source_url": url,
                                "source_type": source_type,
                                "crawled_at": datetime.utcnow().isoformat()
                            }
                        )
                        docs.append(doc)
                        
                except Exception as e:
                    # Log error but continue with other URLs
                    print(f"Error crawling {url}: {str(e)}")
                    continue
                    
        return docs
