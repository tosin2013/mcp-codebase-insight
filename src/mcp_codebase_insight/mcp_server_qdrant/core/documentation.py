from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import structlog

from .config import ServerConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class DocReference:
    """Reference to external documentation."""
    url: str
    title: str
    description: str
    content: str
    last_updated: datetime
    tags: List[str]
    source_type: str  # api, framework, best_practice, etc.
    local_path: Path

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "last_updated": self.last_updated.isoformat(),
            "tags": self.tags,
            "source_type": self.source_type,
            "local_path": str(self.local_path)
        }

    @classmethod
    def from_dict(cls, data: Dict, content: str) -> "DocReference":
        """Create from dictionary and content."""
        return cls(
            url=data["url"],
            title=data["title"],
            description=data["description"],
            content=content,
            last_updated=datetime.fromisoformat(data["last_updated"]),
            tags=data["tags"],
            source_type=data["source_type"],
            local_path=Path(data["local_path"])
        )

class DocumentationManager:
    """Manages external documentation references."""

    def __init__(self, config: ServerConfig):
        """Initialize documentation manager."""
        self.config = config
        self.cache_dir = config.docs_cache_dir
        self.index_path = self.cache_dir / "index.json"
        self.gitignore_path = config.gitignore_path
        
        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize index
        if not self.index_path.exists():
            self.index_path.write_text("{}")

    async def crawl_documentation(self, urls: List[str], source_type: str) -> List[DocReference]:
        """Crawl and store documentation from URLs."""
        references = []
        async with aiohttp.ClientSession() as session:
            tasks = [self._crawl_url(session, url, source_type) for url in urls]
            references = await asyncio.gather(*tasks)
        
        # Update gitignore
        await self._update_gitignore()
        
        return [ref for ref in references if ref is not None]

    async def get_reference(self, url: str) -> Optional[DocReference]:
        """Get documentation reference by URL."""
        index = json.loads(self.index_path.read_text())
        if url not in index:
            return None
        
        ref_data = index[url]
        local_path = Path(ref_data["local_path"])
        if not local_path.exists():
            return None
        
        content = local_path.read_text()
        return DocReference.from_dict(ref_data, content)

    async def search_references(
        self,
        query: str,
        source_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[DocReference]:
        """Search documentation references."""
        index = json.loads(self.index_path.read_text())
        results = []
        
        for url, ref_data in index.items():
            # Apply filters
            if source_type and ref_data["source_type"] != source_type:
                continue
            if tags and not all(tag in ref_data["tags"] for tag in tags):
                continue
            
            # Check if content matches query
            local_path = Path(ref_data["local_path"])
            if not local_path.exists():
                continue
            
            content = local_path.read_text()
            if query.lower() in content.lower():
                results.append(DocReference.from_dict(ref_data, content))
        
        return results

    async def update_references(self) -> None:
        """Update all documentation references."""
        index = json.loads(self.index_path.read_text())
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._crawl_url(
                    session,
                    url,
                    ref_data["source_type"],
                    existing_ref=DocReference.from_dict(
                        ref_data,
                        Path(ref_data["local_path"]).read_text()
                    )
                )
                for url, ref_data in index.items()
            ]
            await asyncio.gather(*tasks)

    async def _crawl_url(
        self,
        session: aiohttp.ClientSession,
        url: str,
        source_type: str,
        existing_ref: Optional[DocReference] = None
    ) -> Optional[DocReference]:
        """Crawl single URL and store content."""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: {response.status}")
                    return existing_ref
                
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                
                # Extract metadata
                title = soup.title.string if soup.title else url
                description = (
                    soup.find("meta", {"name": "description"})["content"]
                    if soup.find("meta", {"name": "description"})
                    else ""
                )
                
                # Generate filename from URL
                filename = url.replace("://", "_").replace("/", "_")
                if len(filename) > 100:
                    filename = filename[:100]  # Truncate long filenames
                local_path = self.cache_dir / f"{filename}.html"
                
                # Save content
                if len(content) > self.config.docs_max_size:
                    logger.warning(f"Content too large for {url}, truncating")
                    content = content[:self.config.docs_max_size]
                local_path.write_text(content)
                
                # Create reference
                ref = DocReference(
                    url=url,
                    title=title,
                    description=description,
                    content=content,
                    last_updated=datetime.now(),
                    tags=[],  # Tags can be added later
                    source_type=source_type,
                    local_path=local_path
                )
                
                # Update index
                index = json.loads(self.index_path.read_text())
                index[url] = ref.to_dict()
                self.index_path.write_text(json.dumps(index, indent=2))
                
                return ref
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return existing_ref

    async def _update_gitignore(self) -> None:
        """Update .gitignore with documentation cache directory."""
        if not self.gitignore_path.exists():
            self.gitignore_path.write_text("")
        
        content = self.gitignore_path.read_text()
        cache_pattern = str(self.cache_dir) + "/"
        
        if cache_pattern not in content:
            if not content.endswith("\n"):
                content += "\n"
            content += f"{cache_pattern}\n"
            self.gitignore_path.write_text(content)
