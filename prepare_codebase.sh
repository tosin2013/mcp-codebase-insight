#!/bin/bash
set -x  # Enable debugging

# Set output files
STRUCTURE_FILE="codebase_structure.txt"
SUMMARY_FILE="summary_document.txt"
MODULE_SUMMARY_DIR="module_summaries"
WORKFLOWS_FILE="core_workflows.txt"

# Define directories to ignore for the file search
IGNORE_DIRS=("node_modules" ".venv" "venv" "vendor")

# Create a directory for module summaries
mkdir -p "$MODULE_SUMMARY_DIR"

# Construct the 'find' command to exclude ignored directories
FIND_CMD="find ."

for dir in "${IGNORE_DIRS[@]}"; do
    FIND_CMD+=" -path ./$dir -prune -o"
done

# Add file search conditions
FIND_CMD+=" -type f \( -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name '*.sh' \
    -o -name '*.py' -o -name '*.md' -o -name '*.json' -o -name '*.yml' -o -name '*.yaml'  -o -name '*.j2' \) -print | sort"

# Debugging: Show the generated find command
echo "Executing command: $FIND_CMD"

# Execute and store results
eval "$FIND_CMD" > "$STRUCTURE_FILE"

# Check if files were captured
if [ ! -s "$STRUCTURE_FILE" ]; then
    echo "⚠️ Warning: No matching files found. Please check directory paths."
fi

# Create summary document
cat <<EOL > "$SUMMARY_FILE"
# Application Summary

## Architecture
This document provides a summary of the application's architecture, key modules, and their relationships.

## Key Modules
- Placeholder for module descriptions.
- Include information about the functionality, dependencies, and interaction with other modules.

## Relationships
- Describe how the modules interact with one another.
- Mention any patterns such as MVC, Microservices, etc.

## High-Level Next Steps for LLM
1. Identify and generate module summaries for frontend, backend, and database.
2. Document core workflows and user journeys within the application.

EOL

# Generate module summaries with placeholders for customization
echo "Generating module summaries... Please customize the contents as necessary."
cat <<EOL > "$MODULE_SUMMARY_DIR/frontend_summary.txt"
# Frontend Module Summary
- **Purpose**: Describe the frontend's role in the application.
- **Key Components**: List key components such as main frameworks, libraries, and UI components.
- **Dependencies**: Mention any dependencies on backend services or external APIs.
EOL

cat <<EOL > "$MODULE_SUMMARY_DIR/backend_summary.txt"
# Backend Module Summary
- **Purpose**: Describe the backend's role in the application.
- **Key Components**: List key components such as main frameworks, APIs, and data handling.
- **Dependencies**: Mention any database connections and external services it relies on.
EOL

cat <<EOL > "$MODULE_SUMMARY_DIR/database_summary.txt"
# Database Module Summary
- **Purpose**: Describe the database’s role in the application.
- **Key Components**: List database types, schema designs, and any ORM tools used.
- **Dependencies**: Mention the relationships with the backend and data sources.
EOL

# Document core workflows with placeholders for customization
echo "Identifying core workflows... Please customize the contents as necessary."
cat <<EOL > "$WORKFLOWS_FILE"
# Core Workflows

## User Journeys
1. **Product Browsing**:
   - Relevant code files: [list of files responsible for navigation, product listing]
  
2. **Checkout Process**:
   - Relevant code files: [list of files responsible for cart management, payment handling]
  
3. **User Authentication**:
   - Relevant code files: [list of files responsible for login, logout, user session management]

### Note:
- The workflows and summaries provided are examples. Please modify them to fit the specific use case and structure of your application repository.
EOL

# Completion message
echo "Directory structure saved to $STRUCTURE_FILE."
echo "Summary document created at $SUMMARY_FILE."
echo "Module summaries created in the $MODULE_SUMMARY_DIR directory."
echo "Core workflows documented in $WORKFLOWS_FILE."