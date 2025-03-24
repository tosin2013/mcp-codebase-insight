"""Tests for the build verification script."""

import os
import json
import sys
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
from datetime import datetime
from pathlib import Path

# Import the BuildVerifier class
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.verify_build import BuildVerifier

@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    mock = AsyncMock()
    
    # Mock search method to return search results
    async def mock_search(text, filter_conditions=None, limit=5):
        if "dependency map" in text:
            return [
                MagicMock(
                    id="dep-map",
                    score=0.95,
                    metadata={
                        "dependencies": {
                            "module_a": ["module_b", "module_c"],
                            "module_b": ["module_d"],
                            "module_c": []
                        }
                    }
                )
            ]
        elif "critical system components" in text:
            return [
                MagicMock(
                    id="critical-components",
                    score=0.90,
                    metadata={
                        "critical_components": ["module_a", "module_d"]
                    }
                )
            ]
        elif "build verification success criteria" in text:
            return [
                MagicMock(
                    id="build-criteria",
                    score=0.85,
                    metadata={
                        "criteria": [
                            "All tests must pass (maximum 0 failures allowed)",
                            "Test coverage must be at least 80.0%",
                            "Build process must complete without errors",
                            "Critical modules (module_a, module_d) must pass all tests",
                            "Performance tests must complete within 500ms"
                        ]
                    }
                )
            ]
        elif "common issues and solutions" in text:
            return [
                MagicMock(
                    id="troubleshooting",
                    score=0.80,
                    metadata={
                        "potential_causes": [
                            "Incorrect function arguments",
                            "Missing dependency",
                            "API version mismatch"
                        ],
                        "recommended_actions": [
                            "Check function signatures",
                            "Verify all dependencies are installed",
                            "Ensure API version compatibility"
                        ]
                    }
                )
            ]
        else:
            return []
    
    mock.search = mock_search
    return mock

@pytest.fixture
def mock_embedder():
    """Create a mock embedder."""
    mock = AsyncMock()
    # Set attributes that would normally be set after initialization
    mock.initialized = True
    mock.vector_size = 384  # Standard size for sentence-transformers models
    mock.model = MagicMock()  # Mock the model object
    
    # Mock async initialize method
    async def mock_initialize():
        mock.initialized = True
        return
    
    mock.initialize = mock_initialize
    
    # Mock embedding methods
    async def mock_embed(text):
        # Return a simple vector of the correct size
        return [0.1] * mock.vector_size
        
    async def mock_embed_batch(texts):
        # Return a batch of simple vectors
        return [[0.1] * mock.vector_size for _ in texts]
    
    mock.embed = mock_embed
    mock.embed_batch = mock_embed_batch
    
    return mock

@pytest.fixture
def build_verifier(mock_vector_store, mock_embedder):
    """Create a BuildVerifier with mocked dependencies."""
    with patch('scripts.verify_build.SentenceTransformerEmbedding', return_value=mock_embedder):
        verifier = BuildVerifier()
        verifier.vector_store = mock_vector_store
        verifier.embedder = mock_embedder
        verifier.config = {
            'qdrant_url': 'http://localhost:6333',
            'qdrant_api_key': 'test-api-key',
            'collection_name': 'test-collection',
            'embedding_model': 'test-model',
            'build_command': 'make build',
            'test_command': 'make test',
            'success_criteria': {
                'min_test_coverage': 80.0,
                'max_allowed_failures': 0,
                'critical_modules': ['module_a', 'module_d'],
                'performance_threshold_ms': 500
            }
        }
        verifier.build_start_time = datetime.now()
        verifier.build_end_time = datetime.now()
        return verifier

class TestBuildVerifier:
    """Tests for the BuildVerifier class."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, build_verifier, mock_vector_store):
        """Test initialization of the BuildVerifier."""
        # Reset to None for the test
        build_verifier.vector_store = None
        
        # Mock the entire SentenceTransformerEmbedding class 
        mock_embedder = AsyncMock()
        mock_embedder.initialized = True
        mock_embedder.model = MagicMock()
        mock_embedder.vector_size = 384
        
        # Replace the embedder with our controlled mock
        build_verifier.embedder = mock_embedder
        
        # Mock VectorStore class
        with patch('scripts.verify_build.VectorStore', return_value=mock_vector_store):
            await build_verifier.initialize()
            
            # Verify vector store was initialized
            assert build_verifier.vector_store is not None
            build_verifier.vector_store.initialize.assert_called_once()
            
            # Verify dependency map and critical components were loaded
            assert build_verifier.dependency_map == {
                "module_a": ["module_b", "module_c"],
                "module_b": ["module_d"],
                "module_c": []
            }
            assert set(build_verifier.critical_components) == {"module_a", "module_d"}
    
    @pytest.mark.asyncio
    async def test_trigger_build_success(self, build_verifier):
        """Test successful build triggering."""
        with patch('scripts.verify_build.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.returncode = 0
            mock_process.communicate.return_value = ("Build successful", "")
            
            result = await build_verifier.trigger_build()
            
            # Verify subprocess was called with correct command
            mock_popen.assert_called_once()
            assert mock_popen.call_args[0][0] == build_verifier.config['build_command']
            
            # Verify result is True for successful build
            assert result is True
            
            # Verify build output and logs were captured
            assert build_verifier.build_output == "Build successful"
            assert build_verifier.build_logs == ["Build successful"]
    
    @pytest.mark.asyncio
    async def test_trigger_build_failure(self, build_verifier):
        """Test failed build triggering."""
        with patch('scripts.verify_build.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.returncode = 1
            mock_process.communicate.return_value = ("", "Build failed")
            
            result = await build_verifier.trigger_build()
            
            # Verify result is False for failed build
            assert result is False
            
            # Verify error logs were captured
            assert "ERROR: Build failed" in build_verifier.build_logs
    
    @pytest.mark.asyncio
    async def test_run_tests_success(self, build_verifier):
        """Test successful test execution."""
        with patch('scripts.verify_build.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.returncode = 0
            mock_process.communicate.return_value = (
                "collected 10 items\n"
                "..........                                                     [100%]\n"
                "----------- coverage: platform darwin, python 3.9.10-final-0 -----------\n"
                "Name                                   Stmts   Miss  Cover   Missing\n"
                "--------------------------------------------------------------------\n"
                "src/mcp_codebase_insight/__init__.py       7      0   100%\n"
                "TOTAL                                     600    100    83%\n", 
                ""
            )
            
            # Mock the _parse_test_results method to avoid complex parsing
            with patch.object(build_verifier, '_parse_test_results') as mock_parse:
                result = await build_verifier.run_tests()
                
                # Verify subprocess was called with correct command
                mock_popen.assert_called_once()
                assert mock_popen.call_args[0][0] == build_verifier.config['test_command']
                
                # Verify result is True for successful tests
                assert result is True
                
                # Verify parse method was called
                mock_parse.assert_called_once()
    
    def test_parse_test_results(self, build_verifier):
        """Test parsing of test results."""
        test_output = (
            "collected 10 items\n"
            "......FAILED tests/test_module_a.py::test_function                [70%]\n"
            "..FAILED tests/test_module_b.py::test_another_function            [90%]\n"
            "ERROR tests/test_module_c.py::test_error                          [100%]\n"
            "----------- coverage: platform darwin, python 3.9.10-final-0 -----------\n"
            "Name                                   Stmts   Miss  Cover   Missing\n"
            "--------------------------------------------------------------------\n"
            "src/mcp_codebase_insight/__init__.py       7      0   100%\n"
            "TOTAL                                     600    100    83%\n"
        )
        
        build_verifier._parse_test_results(test_output)
        
        # Verify test results were parsed correctly
        assert build_verifier.test_results["total"] == 10
        assert build_verifier.test_results["failed"] == 2  # Only counts FAILED, not ERROR
        assert build_verifier.test_results["coverage"] == 83.0
        assert len(build_verifier.test_results["failures"]) == 2
        assert "FAILED tests/test_module_a.py::test_function" in build_verifier.test_results["failures"]
        assert "FAILED tests/test_module_b.py::test_function" not in build_verifier.test_results["failures"]
    
    @pytest.mark.asyncio
    async def test_gather_verification_criteria(self, build_verifier):
        """Test gathering verification criteria from vector database."""
        await build_verifier.gather_verification_criteria()
        
        # Verify criteria were loaded from vector database
        assert len(build_verifier.success_criteria) == 5
        assert "All tests must pass" in build_verifier.success_criteria[0]
        assert "Test coverage must be at least 80.0%" in build_verifier.success_criteria[1]
        assert "Build process must complete without errors" in build_verifier.success_criteria[2]
        assert "Critical modules" in build_verifier.success_criteria[3]
        assert "Performance tests must complete within 500ms" in build_verifier.success_criteria[4]
    
    @pytest.mark.asyncio
    async def test_analyze_build_results_success(self, build_verifier):
        """Test analysis of successful build results."""
        # Set up successful build and test results
        build_verifier.build_logs = ["Build successful"]
        build_verifier.test_results = {
            "total": 10,
            "passed": 10,
            "failed": 0,
            "skipped": 0,
            "coverage": 85.0,
            "duration_ms": 450,
            "failures": []
        }
        build_verifier.success_criteria = [
            "All tests must pass (maximum 0 failures allowed)",
            "Test coverage must be at least 80.0%",
            "Build process must complete without errors",
            "Critical modules (module_a, module_d) must pass all tests",
            "Performance tests must complete within 500ms"
        ]
        
        success, results = await build_verifier.analyze_build_results()
        
        # Verify analysis results
        assert success is True
        assert results["build_success"] is True
        assert results["tests_success"] is True
        assert results["coverage_success"] is True
        assert results["critical_modules_success"] is True
        assert results["performance_success"] is True
        assert results["overall_success"] is True
        
        # Verify criteria results
        for criterion_result in results["criteria_results"].values():
            assert criterion_result["passed"] is True
    
    @pytest.mark.asyncio
    async def test_analyze_build_results_failure(self, build_verifier):
        """Test analysis of failed build results."""
        # Set up failed build and test results with severe build errors
        build_verifier.build_logs = ["ERROR: Build failed with exit code 1"]
        build_verifier.test_results = {
            "total": 10,
            "passed": 8,
            "failed": 2,
            "skipped": 0,
            "coverage": 75.0,
            "duration_ms": 550,
            "failures": [
                "FAILED tests/test_module_a.py::test_function",
                "FAILED tests/test_module_b.py::test_another_function"
            ]
        }
        build_verifier.success_criteria = [
            "All tests must pass (maximum 0 failures allowed)",
            "Test coverage must be at least 80.0%",
            "Build process must complete without errors",
            "Critical modules (module_a, module_d) must pass all tests",
            "Performance tests must complete within 500ms"
        ]
        build_verifier.critical_components = ["module_a", "module_d"]
        
        # Patch the build_success detection method to return False
        with patch.object(build_verifier, '_detect_build_success', return_value=False):
            success, results = await build_verifier.analyze_build_results()
            
            # Verify analysis results
            assert success is False
            assert results["build_success"] is False
            assert results["tests_success"] is False
            assert results["coverage_success"] is False
            assert results["critical_modules_success"] is False
            assert results["performance_success"] is False
            assert results["overall_success"] is False
            
            # Verify failure analysis
            assert len(results["failure_analysis"]) > 0
    
    @pytest.mark.asyncio
    async def test_contextual_verification(self, build_verifier):
        """Test contextual verification of build failures."""
        # Set up analysis results with failures
        analysis_results = {
            "build_success": True,
            "tests_success": False,
            "coverage_success": True,
            "critical_modules_success": False,
            "performance_success": True,
            "overall_success": False,
            "criteria_results": {},
            "failure_analysis": []
        }
        
        # Set up test failures
        build_verifier.test_results = {
            "failures": [
                "FAILED tests/test_module_a.py::test_function"
            ]
        }
        
        # Set up dependency map - making sure the test module is properly mapped
        build_verifier.dependency_map = {
            "module_a": ["module_b", "module_c"],
            "module_b": ["module_d"],
            "module_c": [],
            "tests.test_module_a": ["module_b", "module_c"]  # Add this mapping
        }
        
        # Mock the _extract_module_from_failure method to return the correct module name
        with patch.object(build_verifier, '_extract_module_from_failure', return_value="tests.test_module_a"):
            results = await build_verifier.contextual_verification(analysis_results)
            
            # Verify contextual verification results
            assert "contextual_verification" in results
            assert len(results["contextual_verification"]) == 1
            
            # Verify failure analysis
            failure_analysis = results["contextual_verification"][0]
            assert failure_analysis["module"] == "tests.test_module_a"
            assert failure_analysis["dependencies"] == ["module_b", "module_c"]
            assert len(failure_analysis["potential_causes"]) > 0
            assert len(failure_analysis["recommended_actions"]) > 0
    
    def test_extract_module_from_failure(self, build_verifier):
        """Test extraction of module name from failure message."""
        failure = "FAILED tests/test_module_a.py::test_function"
        module = build_verifier._extract_module_from_failure(failure)
        assert module == "tests.test_module_a"
        
        failure = "ERROR tests/test_module_b.py::test_function"
        module = build_verifier._extract_module_from_failure(failure)
        assert module is None
    
    def test_generate_report(self, build_verifier):
        """Test generation of build verification report."""
        # Set up analysis results
        results = {
            "build_success": True,
            "tests_success": True,
            "coverage_success": True,
            "critical_modules_success": True,
            "performance_success": True,
            "overall_success": True,
            "criteria_results": {
                "All tests must pass": {"passed": True, "details": "10/10 tests passed, 0 failed"},
                "Test coverage must be at least 80.0%": {"passed": True, "details": "Coverage: 85.0%, required: 80.0%"}
            },
            "contextual_verification": []
        }
        
        # Set up test results
        build_verifier.test_results = {
            "total": 10,
            "passed": 10,
            "failed": 0,
            "skipped": 0,
            "coverage": 85.0
        }
        
        report = build_verifier.generate_report(results)
        
        # Verify report structure
        assert "build_verification_report" in report
        assert "timestamp" in report["build_verification_report"]
        assert "build_info" in report["build_verification_report"]
        assert "test_summary" in report["build_verification_report"]
        assert "verification_results" in report["build_verification_report"]
        assert "summary" in report["build_verification_report"]
        
        # Verify report content
        assert report["build_verification_report"]["verification_results"]["overall_status"] == "PASS"
        assert report["build_verification_report"]["test_summary"]["total"] == 10
        assert report["build_verification_report"]["test_summary"]["passed"] == 10
        assert report["build_verification_report"]["test_summary"]["coverage"] == 85.0
    
    @pytest.mark.asyncio
    async def test_save_report(self, build_verifier, tmp_path):
        """Test saving report to file and vector database."""
        # Create a temporary report file
        report_file = tmp_path / "report.json"
        
        # Create a report
        report = {
            "build_verification_report": {
                "timestamp": datetime.now().isoformat(),
                "verification_results": {
                    "overall_status": "PASS"
                },
                "summary": "Build verification: PASS. 5/5 criteria passed."
            }
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            await build_verifier.save_report(report, str(report_file))
            
            # Verify file was opened for writing
            mock_file.assert_called_once_with(str(report_file), 'w')
            
            # Verify report was written to file
            mock_file().write.assert_called()
        
        # Verify report was stored in vector database
        build_verifier.vector_store.store_pattern.assert_called_once()
        call_args = build_verifier.vector_store.store_pattern.call_args[1]
        assert call_args["text"] == json.dumps(report)
        assert "build-verification-" in call_args["id"]
        assert call_args["metadata"]["type"] == "build_verification_report"
        assert call_args["metadata"]["overall_status"] == "PASS"
    
    @pytest.mark.asyncio
    async def test_verify_build_success(self, build_verifier):
        """Test end-to-end build verification process with success."""
        # Mock all component methods
        with patch.object(build_verifier, 'initialize', AsyncMock()), \
             patch.object(build_verifier, 'trigger_build', AsyncMock(return_value=True)), \
             patch.object(build_verifier, 'run_tests', AsyncMock(return_value=True)), \
             patch.object(build_verifier, 'gather_verification_criteria', AsyncMock()), \
             patch.object(build_verifier, 'analyze_build_results', AsyncMock(return_value=(True, {}))), \
             patch.object(build_verifier, 'contextual_verification', AsyncMock(return_value={})), \
             patch.object(build_verifier, 'generate_report', return_value={}), \
             patch.object(build_verifier, 'save_report', AsyncMock()), \
             patch.object(build_verifier, 'cleanup', AsyncMock()):
            
            result = await build_verifier.verify_build()
            
            # Verify all methods were called
            build_verifier.initialize.assert_called_once()
            build_verifier.trigger_build.assert_called_once()
            build_verifier.run_tests.assert_called_once()
            build_verifier.gather_verification_criteria.assert_called_once()
            build_verifier.analyze_build_results.assert_called_once()
            build_verifier.contextual_verification.assert_called_once()
            build_verifier.generate_report.assert_called_once()
            build_verifier.save_report.assert_called_once()
            build_verifier.cleanup.assert_called_once()
            
            # Verify result is True for successful verification
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_build_failure(self, build_verifier):
        """Test end-to-end build verification process with failure."""
        # Mock component methods with build failure
        with patch.object(build_verifier, 'initialize', AsyncMock()), \
             patch.object(build_verifier, 'trigger_build', AsyncMock(return_value=False)), \
             patch.object(build_verifier, 'run_tests', AsyncMock()) as mock_run_tests, \
             patch.object(build_verifier, 'gather_verification_criteria', AsyncMock()), \
             patch.object(build_verifier, 'analyze_build_results', AsyncMock(return_value=(False, {}))), \
             patch.object(build_verifier, 'contextual_verification', AsyncMock(return_value={})), \
             patch.object(build_verifier, 'generate_report', return_value={}), \
             patch.object(build_verifier, 'save_report', AsyncMock()), \
             patch.object(build_verifier, 'cleanup', AsyncMock()):
            
            result = await build_verifier.verify_build()
            
            # Verify methods were called appropriately
            build_verifier.initialize.assert_called_once()
            build_verifier.trigger_build.assert_called_once()
            
            # Run tests should not be called if build fails
            mock_run_tests.assert_not_called()
            
            # Verification and report methods should still be called
            build_verifier.gather_verification_criteria.assert_called_once()
            build_verifier.analyze_build_results.assert_called_once()
            build_verifier.contextual_verification.assert_called_once()
            build_verifier.generate_report.assert_called_once()
            build_verifier.save_report.assert_called_once()
            build_verifier.cleanup.assert_called_once()
            
            # Verify result is False for failed verification
            assert result is False 