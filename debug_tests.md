# Debug MCP Codebase Insight Tests

## Problem Statement
Debug and fix the test execution issues in the MCP Codebase Insight project. The main test script `run_tests.py` is encountering issues with module imports and test execution.

## Current Issues
1. Module import errors for `mcp_codebase_insight` package
2. Test execution failures
3. Coverage reporting issues

## Expected Behavior
- All tests should run successfully
- Coverage reports should be generated
- No import errors should occur

## Additional Context
- The project uses pytest for testing
- Coverage reporting is handled through pytest-cov
- The project is set up with a virtual environment
- Environment variables are set in .env file 