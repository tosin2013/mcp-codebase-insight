#!/usr/bin/env python
"""
Store Build Verification Report in MCP Codebase Insight

This script reads the build verification report and stores it in the MCP server
using the vector database for later retrieval and analysis.
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path
import uuid

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mcp_codebase_insight.core.vector_store import VectorStore
from src.mcp_codebase_insight.core.embeddings import SentenceTransformerEmbedding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/store_report.log')
    ]
)
logger = logging.getLogger('store_report')

async def store_report(report_file: str, config_path: str = None):
    """Store the build verification report in the MCP server.
    
    Args:
        report_file: Path to the report file
        config_path: Path to configuration file (optional)
    """
    # Load configuration
    config = {
        'qdrant_url': os.environ.get('QDRANT_URL', 'http://localhost:6333'),
        'qdrant_api_key': os.environ.get('QDRANT_API_KEY', ''),
        'collection_name': os.environ.get('COLLECTION_NAME', 'mcp-codebase-insight'),
        'embedding_model': os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    }
    
    # Override with config file if provided
    if config_path:
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
    
    try:
        # Load report
        logger.info(f"Loading report from {report_file}")
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        # Initialize embedder
        logger.info("Initializing embedder...")
        embedder = SentenceTransformerEmbedding(model_name=config['embedding_model'])
        await embedder.initialize()
        
        # Initialize vector store
        logger.info(f"Connecting to vector store at {config['qdrant_url']}...")
        vector_store = VectorStore(
            url=config['qdrant_url'],
            embedder=embedder,
            collection_name=config['collection_name'],
            api_key=config.get('qdrant_api_key'),
            vector_name="default"
        )
        await vector_store.initialize()
        
        # Prepare report for storage
        report_text = json.dumps(report, indent=2)
        
        # Extract summary information for metadata
        timestamp = report["build_verification_report"]["timestamp"]
        summary = report["build_verification_report"]["summary"]
        overall_status = report["build_verification_report"]["verification_results"]["overall_status"]
        
        # Create more user-friendly metadata
        metadata = {
            "type": "build_verification_report",
            "timestamp": timestamp,
            "overall_status": overall_status,
            "summary": summary,
            "tests_passed": report["build_verification_report"]["test_summary"]["passed"],
            "tests_total": report["build_verification_report"]["test_summary"]["total"],
            "criteria_passed": sum(1 for c in report["build_verification_report"]["verification_results"]["criteria_results"].values() if c["passed"]),
            "criteria_total": len(report["build_verification_report"]["verification_results"]["criteria_results"]),
            "build_date": datetime.now().strftime("%Y-%m-%d"),
            "project": "mcp-codebase-insight",
            "stored_by": "automated-build-verification"
        }
        
        # Store in vector database
        report_id = str(uuid.uuid4())
        logger.info(f"Storing report with ID: {report_id}")
        
        # Generate embedding
        vector = await embedder.embed(report_text)
        
        # Store directly using the client to work around compatibility issues
        from qdrant_client.http import models as rest
        vector_store.client.upsert(
            collection_name=vector_store.collection_name,
            points=[
                rest.PointStruct(
                    id=report_id,
                    vector=vector,  # Use vector instead of vectors
                    payload=metadata
                )
            ]
        )
        
        logger.info(f"Successfully stored report in MCP server with ID: {report_id}")
        
        # Create a record of stored reports
        try:
            history_file = Path("logs/report_history.json")
            history = []
            
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            history.append({
                "id": report_id,
                "timestamp": timestamp,
                "status": overall_status,
                "summary": summary
            })
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
            logger.info(f"Updated report history in {history_file}")
        except Exception as e:
            logger.warning(f"Could not update report history: {e}")
        
        return report_id
        
    except Exception as e:
        logger.error(f"Failed to store report: {e}")
        raise
    finally:
        if 'vector_store' in locals():
            await vector_store.close()

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Store Build Verification Report in MCP")
    parser.add_argument("--report", default="logs/build_verification_report.json", help="Path to report file")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    try:
        report_id = await store_report(args.report, args.config)
        print(f"Report stored successfully with ID: {report_id}")
        return 0
    except Exception as e:
        print(f"Error storing report: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 