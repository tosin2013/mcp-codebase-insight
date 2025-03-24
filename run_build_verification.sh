#!/bin/bash
# End-to-End Build Verification Script
# 
# This script automates the process of verifying an end-to-end build by:
# 1. First analyzing the codebase to store component relationships
# 2. Triggering the build verification process
# 3. Reporting the results

set -e

# Set up environment
source .venv/bin/activate || source test_env/bin/activate || echo "No virtual environment found, using system Python"

# Create required directories
mkdir -p logs knowledge cache

# Set environment variables for testing
export MCP_EMBEDDING_TIMEOUT=120  # Increase timeout for embedder initialization
export QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
export QDRANT_API_KEY="${QDRANT_API_KEY:-}"
export MCP_COLLECTION_NAME="${MCP_COLLECTION_NAME:-mcp-codebase-insight}"

# Default values
CONFIG_FILE="verification-config.json"
OUTPUT_FILE="logs/build_verification_report.json"
ANALYZE_FIRST=true
VERBOSE=false

# Check if Qdrant is running locally
check_qdrant() {
  if curl -s "http://localhost:6333/collections" > /dev/null; then
    echo "Local Qdrant instance detected"
    return 0
  else
    echo "Warning: No local Qdrant instance found at http://localhost:6333"
    echo "You may need to start Qdrant using Docker:"
    echo "docker run -p 6333:6333 qdrant/qdrant"
    return 1
  fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --config)
      CONFIG_FILE="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    --skip-analysis)
      ANALYZE_FIRST=false
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--config CONFIG_FILE] [--output OUTPUT_FILE] [--skip-analysis] [--verbose]"
      exit 1
      ;;
  esac
done

# Set up logging
LOG_FILE="logs/build_verification.log"
if $VERBOSE; then
  # Log to both console and file
  exec > >(tee -a "$LOG_FILE") 2>&1
else
  # Log only to file
  exec >> "$LOG_FILE" 2>&1
fi

echo "==================================================================="
echo "Starting End-to-End Build Verification at $(date)"
echo "==================================================================="
echo "Config file: $CONFIG_FILE"
echo "Output file: $OUTPUT_FILE"
echo "Analyze first: $ANALYZE_FIRST"
echo "Verbose mode: $VERBOSE"
echo "-------------------------------------------------------------------"

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: Config file $CONFIG_FILE not found!"
  exit 1
fi

# Function to check if a command is available
check_command() {
  if ! command -v "$1" &> /dev/null; then
    echo "Error: $1 is required but not installed."
    exit 1
  fi
}

# Check required commands
check_command python
check_command pip

# Ensure all dependencies are installed
echo "Checking dependencies..."
pip install -q -r requirements.txt
pip install -q -e .

# Step 1: Check Qdrant availability
echo "Checking Qdrant availability..."
if ! check_qdrant; then
  if [[ "$QDRANT_URL" == "http://localhost:6333" ]]; then
    echo "Error: Local Qdrant instance is not running and no alternative QDRANT_URL is set"
    echo "Please either:"
    echo "1. Start a local Qdrant instance using Docker:"
    echo "   docker run -p 6333:6333 qdrant/qdrant"
    echo "2. Or set QDRANT_URL to point to your Qdrant instance"
    exit 1
  else
    echo "Using alternative Qdrant instance at $QDRANT_URL"
  fi
fi

# Step 2: Analyze codebase and store component relationships (if enabled)
if $ANALYZE_FIRST; then
  echo "Analyzing codebase and storing component relationships..."
  python -m scripts.store_code_relationships --config "$CONFIG_FILE"
  
  if [[ $? -ne 0 ]]; then
    echo "Error: Failed to analyze codebase and store component relationships!"
    exit 1
  fi
  
  echo "Component relationships analysis completed successfully."
else
  echo "Skipping codebase analysis as requested."
fi

# Step 3: Run build verification
echo "Running tests with standardized test runner..."
chmod +x run_tests.py
./run_tests.py --all --clean --isolated --coverage --html --verbose
TEST_EXIT_CODE=$?

echo "Running build verification..."
python -m scripts.verify_build --config "$CONFIG_FILE" --output "$OUTPUT_FILE"
BUILD_STATUS=$?

# Use the worst exit code between tests and build verification
if [ $TEST_EXIT_CODE -ne 0 ]; then
  BUILD_STATUS=$TEST_EXIT_CODE
fi

if [[ $BUILD_STATUS -ne 0 ]]; then
  echo "Build verification failed with exit code $BUILD_STATUS!"
else
  echo "Build verification completed successfully."
fi

# Step 4: Report results
echo "Build verification report saved to $OUTPUT_FILE"

if [[ -f "$OUTPUT_FILE" ]]; then
  # Extract summary from report if jq is available
  if command -v jq &> /dev/null; then
    SUMMARY=$(jq -r '.build_verification_report.summary' "$OUTPUT_FILE")
    STATUS=$(jq -r '.build_verification_report.verification_results.overall_status' "$OUTPUT_FILE")
    echo "-------------------------------------------------------------------"
    echo "Build Verification Status: $STATUS"
    echo "Summary: $SUMMARY"
    echo "-------------------------------------------------------------------"
    
    # Print test results
    TOTAL=$(jq -r '.build_verification_report.test_summary.total' "$OUTPUT_FILE")
    PASSED=$(jq -r '.build_verification_report.test_summary.passed' "$OUTPUT_FILE")
    FAILED=$(jq -r '.build_verification_report.test_summary.failed' "$OUTPUT_FILE")
    COVERAGE=$(jq -r '.build_verification_report.test_summary.coverage' "$OUTPUT_FILE")
    
    echo "Test Results:"
    echo "- Total Tests: $TOTAL"
    echo "- Passed: $PASSED"
    echo "- Failed: $FAILED"
    echo "- Coverage: $COVERAGE%"
    
    # Print failure info if any
    if [[ "$STATUS" != "PASS" ]]; then
      echo "-------------------------------------------------------------------"
      echo "Failures detected. See $OUTPUT_FILE for details."
      
      # Print failure analysis if available
      if jq -e '.build_verification_report.failure_analysis' "$OUTPUT_FILE" > /dev/null; then
        echo "Failure Analysis:"
        jq -r '.build_verification_report.failure_analysis[] | "- " + .description' "$OUTPUT_FILE"
      fi
    fi
  else
    echo "-------------------------------------------------------------------"
    echo "Install jq for better report formatting."
    echo "Report saved to $OUTPUT_FILE"
  fi
else
  echo "Error: Build verification report not found at $OUTPUT_FILE!"
fi

echo "==================================================================="
echo "End-to-End Build Verification completed at $(date)"
echo "Exit status: $BUILD_STATUS"
echo "==================================================================="

exit $BUILD_STATUS 