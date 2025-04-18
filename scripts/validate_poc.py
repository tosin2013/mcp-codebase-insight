#!/usr/bin/env python3
"""
MCP Codebase Insight - PoC Validation Script
This script orchestrates the validation of all PoC components using Firecrawl MCP.
"""

import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

from mcp_firecrawl import (
    verify_environment,
    setup_repository,
    configure_environment,
    initialize_services,
    verify_transport_config,
    verify_sse_endpoints,
    verify_stdio_transport,
    test_transport_switch,
    validate_transport_features,
    test_cross_transport
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoCValidator:
    """Orchestrates PoC validation steps."""
    
    def __init__(self, config_path: str = ".env"):
        self.config_path = config_path
        self.results = {}
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load config from .env or other config file."""
        from dotenv import dotenv_values
        config = dotenv_values(self.config_path)
        return config
    
    async def setup_environment(self) -> bool:
        """Validate and setup the environment."""
        logger.info("Validating environment...")
        
        # Check system requirements
        env_check = verify_environment({
            "python_version": "3.11",
            "docker_version": "20.10.0",
            "ram_gb": 4,
            "cpu_cores": 2,
            "disk_space_gb": 20
        })
        
        if not env_check.success:
            logger.error("Environment validation failed:")
            for issue in env_check.issues:
                logger.error(f"- {issue}")
            return False
        
        logger.info("Environment validation successful")
        return True
    
    async def setup_services(self) -> bool:
        """Initialize and verify required services."""
        logger.info("Initializing services...")
        
        try:
            services = await initialize_services({
                "qdrant": {
                    "docker_compose": True,
                    "wait_for_ready": True
                },
                "vector_store": {
                    "init_collection": True,
                    "verify_connection": True
                }
            })
            
            logger.info("Services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return False
    
    async def validate_transports(self) -> bool:
        """Validate both SSE and stdio transports."""
        logger.info("Validating transport protocols...")
        
        # Verify SSE endpoints
        sse_result = await verify_sse_endpoints(
            "http://localhost:8000",
            {"Authorization": f"Bearer {self.config.get('API_KEY')}"}
        )
        
        # Verify stdio transport
        stdio_result = await verify_stdio_transport(
            "mcp-codebase-insight",
            {"auth_token": self.config.get('API_KEY')}
        )
        
        # Test transport switching
        switch_result = await test_transport_switch(
            server_url="http://localhost:8000",
            stdio_binary="mcp-codebase-insight",
            config={
                "auth_token": self.config.get('API_KEY'),
                "verify_endpoints": True,
                "check_data_consistency": True
            }
        )
        
        # Validate transport features
        sse_features = await validate_transport_features(
            "sse",
            {
                "server_url": "http://localhost:8000",
                "auth_token": self.config.get('API_KEY'),
                "features": [
                    "event_streaming",
                    "bidirectional_communication",
                    "error_handling",
                    "reconnection"
                ]
            }
        )
        
        stdio_features = await validate_transport_features(
            "stdio",
            {
                "binary": "mcp-codebase-insight",
                "auth_token": self.config.get('API_KEY'),
                "features": [
                    "synchronous_communication",
                    "process_isolation",
                    "error_propagation",
                    "signal_handling"
                ]
            }
        )
        
        # Test cross-transport compatibility
        cross_transport = await test_cross_transport({
            "sse_config": {
                "url": "http://localhost:8000",
                "auth_token": self.config.get('API_KEY')
            },
            "stdio_config": {
                "binary": "mcp-codebase-insight",
                "auth_token": self.config.get('API_KEY')
            },
            "test_operations": [
                "vector_search",
                "pattern_store",
                "task_management",
                "adr_queries"
            ]
        })
        
        all_passed = all([
            sse_result.success,
            stdio_result.success,
            switch_result.success,
            sse_features.success,
            stdio_features.success,
            cross_transport.success
        ])
        
        if all_passed:
            logger.info("Transport validation successful")
        else:
            logger.error("Transport validation failed")
        
        return all_passed
    
    async def run_validation(self) -> Dict[str, Any]:
        """Run all validation steps."""
        validation_steps = [
            ("environment", self.setup_environment()),
            ("services", self.setup_services()),
            ("transports", self.validate_transports()),
            # Add more validation steps here
        ]
        
        results = {}
        for step_name, coro in validation_steps:
            try:
                results[step_name] = await coro
                if not results[step_name]:
                    logger.error(f"Validation step '{step_name}' failed")
                    break
            except Exception as e:
                logger.error(f"Error in validation step '{step_name}': {e}")
                results[step_name] = False
                break
        
        return results

def main():
    """Main entry point for PoC validation."""
    parser = argparse.ArgumentParser(description="Validate MCP Codebase Insight PoC")
    parser.add_argument("--config", default=".env", help="Path to configuration file")
    args = parser.parse_args()
    
    validator = PoCValidator(args.config)
    results = asyncio.run(validator.run_validation())
    
    # Print summary
    print("\nValidation Results:")
    print("-" * 50)
    for step, success in results.items():
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{step:20} {status}")
    print("-" * 50)
    
    # Exit with appropriate status
    exit(0 if all(results.values()) else 1)

if __name__ == "__main__":
    main()