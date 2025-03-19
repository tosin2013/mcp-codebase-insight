"""Documentation management."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from mcp_codebase_insight.core.config import ServerConfig
from mcp_codebase_insight.core.errors import DocumentationError
from mcp_codebase_insight.utils.logger import get_logger

logger = get_logger(__name__)

class DocumentationType(str, Enum):
    """Types of documentation."""
    API = "api"
    ARCHITECTURE = "architecture"
    DEPLOYMENT = "deployment"
    DEVELOPMENT = "development"
    TESTING = "testing"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"

@dataclass
class Document:
    """A documentation document."""
    id: str
    title: str
    content: str
    type: DocumentationType
    source_url: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class DocumentationManager:
    """Manager for documentation."""

    def __init__(self, config: ServerConfig):
        """Initialize documentation manager."""
        self.config = config
        self.docs_dir = config.docs_cache_dir
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.docs_dir / "index.json"
        self._load_index()

    def _load_index(self):
        """Load documentation index."""
        try:
            if self.index_file.exists():
                with open(self.index_file, "r") as f:
                    index = json.load(f)
                self.documents = {
                    doc_id: Document(
                        id=doc_id,
                        title=doc["title"],
                        content=self._load_content(doc_id),
                        type=DocumentationType(doc["type"]),
                        source_url=doc.get("source_url"),
                        metadata=doc.get("metadata", {}),
                        created_at=datetime.fromisoformat(doc["created_at"]),
                        updated_at=datetime.fromisoformat(doc["updated_at"])
                    )
                    for doc_id, doc in index.items()
                }
            else:
                self.documents = {}
        except Exception as e:
            raise DocumentationError(f"Failed to load index: {e}")

    def _save_index(self):
        """Save documentation index."""
        try:
            index = {
                doc_id: {
                    "title": doc.title,
                    "type": doc.type.value,
                    "source_url": doc.source_url,
                    "metadata": doc.metadata,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat()
                }
                for doc_id, doc in self.documents.items()
            }
            with open(self.index_file, "w") as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            raise DocumentationError(f"Failed to save index: {e}")

    def _load_content(self, doc_id: str) -> str:
        """Load document content."""
        try:
            content_file = self.docs_dir / f"{doc_id}.txt"
            if not content_file.exists():
                raise DocumentationError(f"Content file not found: {doc_id}")
            with open(content_file, "r") as f:
                return f.read()
        except Exception as e:
            raise DocumentationError(f"Failed to load content: {e}")

    def _save_content(self, doc_id: str, content: str):
        """Save document content."""
        try:
            content_file = self.docs_dir / f"{doc_id}.txt"
            with open(content_file, "w") as f:
                f.write(content)
        except Exception as e:
            raise DocumentationError(f"Failed to save content: {e}")

    async def add_document(
        self,
        title: str,
        content: str,
        type: DocumentationType,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Add a new document."""
        try:
            from uuid import uuid4
            doc_id = str(uuid4())
            now = datetime.utcnow()
            
            document = Document(
                id=doc_id,
                title=title,
                content=content,
                type=type,
                source_url=source_url,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            
            self._save_content(doc_id, content)
            self.documents[doc_id] = document
            self._save_index()
            
            logger.info(f"Added document {doc_id}: {title}")
            return document
        except Exception as e:
            raise DocumentationError(f"Failed to add document: {e}")

    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID."""
        return self.documents.get(doc_id)

    async def update_document(
        self,
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        type: Optional[DocumentationType] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Update a document."""
        try:
            document = self.documents.get(doc_id)
            if not document:
                raise DocumentationError(f"Document not found: {doc_id}")
            
            if title is not None:
                document.title = title
            if content is not None:
                document.content = content
                self._save_content(doc_id, content)
            if type is not None:
                document.type = type
            if source_url is not None:
                document.source_url = source_url
            if metadata is not None:
                document.metadata.update(metadata)
            
            document.updated_at = datetime.utcnow()
            self._save_index()
            
            logger.info(f"Updated document {doc_id}")
            return document
        except Exception as e:
            raise DocumentationError(f"Failed to update document: {e}")

    async def delete_document(self, doc_id: str):
        """Delete a document."""
        try:
            if doc_id not in self.documents:
                raise DocumentationError(f"Document not found: {doc_id}")
            
            content_file = self.docs_dir / f"{doc_id}.txt"
            if content_file.exists():
                content_file.unlink()
            
            del self.documents[doc_id]
            self._save_index()
            
            logger.info(f"Deleted document {doc_id}")
        except Exception as e:
            raise DocumentationError(f"Failed to delete document: {e}")

    async def list_documents(
        self,
        type: Optional[DocumentationType] = None
    ) -> List[Document]:
        """List documents with optional type filter."""
        docs = list(self.documents.values())
        
        if type:
            docs = [d for d in docs if d.type == type]
        
        return sorted(docs, key=lambda d: d.updated_at, reverse=True)

    async def search_documents(
        self,
        query: str,
        type: Optional[DocumentationType] = None,
        limit: int = 5
    ) -> List[Document]:
        """Search documents by content."""
        # Simple text search for now
        # TODO: Implement vector search
        docs = await self.list_documents(type)
        results = []
        
        query = query.lower()
        for doc in docs:
            if (
                query in doc.title.lower() or
                query in doc.content.lower()
            ):
                results.append(doc)
                if len(results) >= limit:
                    break
        
        return results
