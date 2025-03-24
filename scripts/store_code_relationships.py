#!/usr/bin/env python
"""
Store Code Component Relationships in Vector Database

This script analyzes the codebase to extract relationships between components
and stores them in the vector database for use in build verification.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import uuid

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mcp_codebase_insight.core.vector_store import VectorStore
from src.mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path('logs/code_relationships.log'))
    ]
)
logger = logging.getLogger('code_relationships')

class CodeRelationshipAnalyzer:
    """Code relationship analyzer for storing component relationships in vector database."""
    
    def __init__(self, config_path: str = None):
        """Initialize the code relationship analyzer.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.vector_store = None
        self.embedder = None
        self.dependency_map = {}
        self.critical_components = set()
        self.source_files = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file or environment variables.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        config = {
            'qdrant_url': os.environ.get('QDRANT_URL', 'http://localhost:6333'),
            'qdrant_api_key': os.environ.get('QDRANT_API_KEY', ''),
            'collection_name': os.environ.get('COLLECTION_NAME', 'mcp-codebase-insight'),
            'embedding_model': os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
            'source_dirs': ['src'],
            'exclude_dirs': ['__pycache__', '.git', '.venv', 'test_env', 'dist', 'build'],
            'critical_modules': [
                'mcp_codebase_insight.core.vector_store',
                'mcp_codebase_insight.core.knowledge',
                'mcp_codebase_insight.server'
            ]
        }
        
        # Override with config file if provided
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                logger.error(f"Failed to load config from {config_path}: {e}")
        
        return config
    
    async def initialize(self):
        """Initialize the analyzer."""
        logger.info("Initializing code relationship analyzer...")
        
        # Initialize embedder
        logger.info("Initializing embedder...")
        self.embedder = SentenceTransformerEmbedding(model_name=self.config['embedding_model'])
        await self.embedder.initialize()
        
        # Initialize vector store
        logger.info(f"Connecting to vector store at {self.config['qdrant_url']}...")
        self.vector_store = VectorStore(
            url=self.config['qdrant_url'],
            embedder=self.embedder,
            collection_name=self.config['collection_name'],
            api_key=self.config.get('qdrant_api_key'),
            vector_name="default"  # Specify a vector name for the collection
        )
        await self.vector_store.initialize()
        
        # Set critical components
        self.critical_components = set(self.config.get('critical_modules', []))
        
        logger.info("Code relationship analyzer initialized successfully")
    
    def find_source_files(self) -> List[Path]:
        """Find all source files to analyze.
        
        Returns:
            List of source file paths
        """
        logger.info("Finding source files...")
        
        source_files = []
        source_dirs = [Path(dir_name) for dir_name in self.config['source_dirs']]
        exclude_dirs = self.config['exclude_dirs']
        
        for source_dir in source_dirs:
            if not source_dir.exists():
                logger.warning(f"Source directory {source_dir} does not exist")
                continue
                
            for root, dirs, files in os.walk(source_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if file.endswith('.py'):
                        source_files.append(Path(root) / file)
        
        logger.info(f"Found {len(source_files)} source files")
        self.source_files = source_files
        return source_files
    
    def analyze_file_dependencies(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze dependencies for a single file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary mapping module name to list of dependencies
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract imports
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Skip comments
                if line.startswith('#'):
                    continue
                    
                # Handle import statements
                if line.startswith('import ') or ' import ' in line:
                    if line.startswith('import '):
                        # Handle "import module" or "import module as alias"
                        import_part = line[7:].strip()
                        if ' as ' in import_part:
                            import_part = import_part.split(' as ')[0].strip()
                        dependencies.append(import_part)
                    elif line.startswith('from ') and ' import ' in line:
                        # Handle "from module import something"
                        from_part = line[5:].split(' import ')[0].strip()
                        dependencies.append(from_part)
            
            # Convert file path to module name
            module_name = str(file_path).replace('/', '.').replace('\\', '.').replace('.py', '')
            for source_dir in self.config['source_dirs']:
                prefix = f"{source_dir}."
                if module_name.startswith(prefix):
                    module_name = module_name[len(prefix):]
            
            return {module_name: dependencies}
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {}
    
    def analyze_all_dependencies(self) -> Dict[str, List[str]]:
        """Analyze dependencies for all source files.
        
        Returns:
            Dictionary mapping module names to lists of dependencies
        """
        logger.info("Analyzing dependencies for all source files...")
        
        if not self.source_files:
            self.find_source_files()
        
        dependency_map = {}
        
        for file_path in self.source_files:
            file_dependencies = self.analyze_file_dependencies(file_path)
            dependency_map.update(file_dependencies)
        
        logger.info(f"Analyzed dependencies for {len(dependency_map)} modules")
        self.dependency_map = dependency_map
        return dependency_map
    
    def identify_critical_components(self) -> Set[str]:
        """Identify critical components in the codebase.
        
        Returns:
            Set of critical component names
        """
        logger.info("Identifying critical components...")
        
        # Start with configured critical modules
        critical_components = set(self.critical_components)
        
        # Add modules with many dependents
        if self.dependency_map:
            # Count how many times each module is a dependency
            dependent_count = {}
            for module, dependencies in self.dependency_map.items():
                for dependency in dependencies:
                    if dependency in dependent_count:
                        dependent_count[dependency] += 1
                    else:
                        dependent_count[dependency] = 1
            
            # Add modules with more than 3 dependents to critical components
            for module, count in dependent_count.items():
                if count > 3:
                    critical_components.add(module)
        
        logger.info(f"Identified {len(critical_components)} critical components")
        self.critical_components = critical_components
        return critical_components
    
    async def store_in_vector_database(self):
        """Store code relationships in vector database."""
        try:
            # Store dependency map
            dependency_text = json.dumps({
                'type': 'dependency_map',
                'dependencies': self.dependency_map
            })
            dependency_vector = await self.vector_store.embedder.embed(dependency_text)
            dependency_data = {
                'id': str(uuid.uuid4()),
                'vector': dependency_vector,
                'payload': {
                    'type': 'dependency_map',
                    'timestamp': datetime.now().isoformat(),
                    'module_count': len(self.dependency_map)
                }
            }
            
            # Store critical components
            critical_text = json.dumps({
                'type': 'critical_components',
                'components': list(self.critical_components)
            })
            critical_vector = await self.vector_store.embedder.embed(critical_text)
            critical_data = {
                'id': str(uuid.uuid4()),
                'vector': critical_vector,
                'payload': {
                    'type': 'critical_components',
                    'timestamp': datetime.now().isoformat(),
                    'component_count': len(self.critical_components)
                }
            }
            
            # Store build verification criteria
            criteria_text = json.dumps({
                'type': 'build_criteria',
                'critical_modules': list(self.critical_components),
                'min_test_coverage': 80.0,
                'max_allowed_failures': 0
            })
            criteria_vector = await self.vector_store.embedder.embed(criteria_text)
            criteria_data = {
                'id': str(uuid.uuid4()),
                'vector': criteria_vector,
                'payload': {
                    'type': 'build_criteria',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Store all data points
            data_points = [dependency_data, critical_data, criteria_data]
            self.vector_store.client.upsert(
                collection_name=self.vector_store.collection_name,
                points=[rest.PointStruct(
                    id=data['id'],
                    vectors={self.vector_store.vector_name: data['vector']},
                    payload=data['payload']
                ) for data in data_points]
            )
            
            logger.info("Successfully stored code relationships in vector database")
            
        except Exception as e:
            logger.error(f"Error storing in vector database: {e}")
            raise
    
    async def analyze_and_store(self):
        """Analyze code relationships and store them in the vector database."""
        try:
            # Find source files
            self.find_source_files()
            
            # Analyze dependencies
            self.analyze_all_dependencies()
            
            # Identify critical components
            self.identify_critical_components()
            
            # Store in vector database
            await self.store_in_vector_database()
            
            logger.info("Analysis and storage completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing and storing code relationships: {e}")
            return False
        
    async def cleanup(self):
        """Clean up resources."""
        if self.vector_store:
            await self.vector_store.cleanup()
            await self.vector_store.close()

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Code Relationship Analyzer")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    analyzer = CodeRelationshipAnalyzer(args.config)
    
    try:
        await analyzer.initialize()
        success = await analyzer.analyze_and_store()
        
        if success:
            logger.info("Code relationship analysis completed successfully")
            return 0
        else:
            logger.error("Code relationship analysis failed")
            return 1
            
    except Exception as e:
        logger.error(f"Error in code relationship analysis: {e}")
        return 1
        
    finally:
        await analyzer.cleanup()

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 