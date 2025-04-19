#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

import sys
import importlib
import os

def test_import(module_name):
    try:
        module = importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False
    
def print_path():
    print("\nPython Path:")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")

def main():
    print("=== Testing Package Imports ===")
    
    print("\nEnvironment:")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    print("\nTesting core package imports:")
    
    # First ensure the parent directory is in the path
    sys.path.insert(0, os.getcwd())
    print_path()
    
    print("\nTesting imports:")
    
    # Test basic Python imports
    test_import("os")
    test_import("sys")
    
    # Test ML/NLP packages
    test_import("torch")
    test_import("numpy")
    test_import("transformers")
    test_import("sentence_transformers")
    
    # Test FastAPI and web packages
    test_import("fastapi")
    test_import("starlette")
    test_import("pydantic")
    
    # Test database packages
    test_import("qdrant_client")
    
    # Test project specific modules
    test_import("src.mcp_codebase_insight.core.config")
    test_import("src.mcp_codebase_insight.core.embeddings")
    test_import("src.mcp_codebase_insight.core.vector_store")
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    main()
