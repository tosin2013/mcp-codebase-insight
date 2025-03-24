#!/bin/bash
set -x  # Enable debugging

# Set output files
STRUCTURE_FILE="codebase_structure.txt"
SUMMARY_FILE="summary_document.txt"
MODULE_SUMMARY_DIR="module_summaries"
WORKFLOWS_FILE="core_workflows.txt"
STATS_FILE="codebase_stats.txt"
LLM_PROMPT_FILE="llm_relationship_prompt.txt"
VECTOR_GRAPH_FILE="vector_relationship_graph.txt"

# Define directories to ignore for the file search
IGNORE_DIRS=("node_modules" ".venv" "venv" "vendor" "test_env")

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

# Count the number of files found
FILE_COUNT=$(wc -l < "$STRUCTURE_FILE")

# Count the total lines of code in all files
echo "Counting lines of code across all files..."
TOTAL_LINES=0
LINES_BY_EXTENSION=()
FILE_LINE_COUNTS=()

while IFS= read -r file; do
    if [ -f "$file" ]; then
        file_lines=$(wc -l < "$file")
        TOTAL_LINES=$((TOTAL_LINES + file_lines))
        
        # Store file name and line count
        FILE_LINE_COUNTS+=("$file:$file_lines")
        
        # Extract file extension
        extension="${file##*.}"
        if [[ -n "$extension" && "$extension" != "$file" ]]; then
            # Add to lines by extension
            LINES_BY_EXTENSION+=("$extension:$file_lines")
        fi
    fi
done < "$STRUCTURE_FILE"

# Create stats file
echo "Generating codebase statistics..."
cat <<EOL > "$STATS_FILE"
# Codebase Statistics

## General Statistics
- Total files: $FILE_COUNT
- Total lines of code: $TOTAL_LINES

## Lines by File Extension
EOL

# Process lines by extension
declare -A ext_lines
for item in "${LINES_BY_EXTENSION[@]}"; do
    ext="${item%%:*}"
    lines="${item#*:}"
    if [[ -n "${ext_lines[$ext]}" ]]; then
        ext_lines[$ext]=$((ext_lines[$ext] + lines))
    else
        ext_lines[$ext]=$lines
    fi
done

# Output lines by extension to stats file
for ext in "${!ext_lines[@]}"; do
    echo "- .$ext: ${ext_lines[$ext]} lines" >> "$STATS_FILE"
done

# Add individual file line counts, sorted by line count in descending order
echo -e "\n## Line Counts by File" >> "$STATS_FILE"
echo "Listing files by line count (largest files first):" >> "$STATS_FILE"

# Sort files by line count (numerically, descending order)
IFS=$'\n' sorted_files=($(for item in "${FILE_LINE_COUNTS[@]}"; do
    echo "$item"
done | sort -t ':' -k2,2nr))

# Output top files by line count
for item in "${sorted_files[@]}"; do
    file="${item%%:*}"
    lines="${item#*:}"
    echo "- $file: $lines lines" >> "$STATS_FILE"
done

# Append the stats to the codebase structure file
echo -e "\n\n# CODEBASE STATISTICS" >> "$STRUCTURE_FILE"
cat "$STATS_FILE" >> "$STRUCTURE_FILE"

# Create a dependency map for imports/requires across files
echo "Analyzing file dependencies..."
DEPENDENCY_MAP_FILE="dependency_map.txt"
echo "# File Dependency Map" > "$DEPENDENCY_MAP_FILE"

# Examine imports in common file types
echo "## Python Dependencies" >> "$DEPENDENCY_MAP_FILE"
grep -r --include="*.py" -E "^(import|from)" . 2>/dev/null | grep -v -E "$(printf '%s|' "${IGNORE_DIRS[@]}")" | sort >> "$DEPENDENCY_MAP_FILE"

echo -e "\n## JavaScript/TypeScript Dependencies" >> "$DEPENDENCY_MAP_FILE"
grep -r --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" -E "(import|require)" . 2>/dev/null | grep -v -E "$(printf '%s|' "${IGNORE_DIRS[@]}")" | sort >> "$DEPENDENCY_MAP_FILE"

# Generate the LLM prompt file
echo "Generating LLM prompt for relationship analysis..."
cat <<EOL > "$LLM_PROMPT_FILE"
# Codebase Relationship Analysis Prompt

## Task
As an AI assistant, your task is to analyze the codebase structure and identify relationships between different files, modules, and components. Focus on extracting the architecture, dependencies, and interaction patterns.
Once completed load the results into a vector database that is connected to the MCP server.

## Codebase Statistics
Total files: $FILE_COUNT
Total lines of code: $TOTAL_LINES

## Available Information
The following files are provided for your analysis:
1. \`codebase_structure.txt\`: List of all files in the codebase
2. \`codebase_stats.txt\`: Statistics about file types and line counts, including per-file line counts
3. \`dependency_map.txt\`: Map of import/require statements across files

## Questions to Answer

1. **Architectural Analysis**:
   - What architectural pattern(s) does this codebase follow? (e.g., MVC, microservices, etc.)
   - How are the different layers or components organized?
   - What are the main modules or services in this application?
   - Which files appear to be the most significant based on their size (line count)?

2. **Dependency Analysis**:
   - Identify the key dependencies between files and modules
   - Create a directed graph representation of these dependencies
   - Which modules are most central to the codebase?
   - Are there any circular dependencies that could be problematic?
   - Based on file size and import relationships, which files are most critical?

3. **Module Interaction Patterns**:
   - How do frontend components interact with backend services?
   - What communication patterns are used between services?
   - How is data transformed as it moves through the system?
   - Which large files have the most connections to other files?

4. **File Relationship Analysis**:
   - Examine the relationship between the largest files in the codebase
   - Identify logical groupings of files based on naming patterns and imports
   - Are there files that should be related but don't show dependencies?

5. **Recommendations**:
   - Are there any architectural improvements you would suggest?
   - Are there potential bottlenecks or coupling issues in the codebase?
   - Should any large files be refactored or split up?

## Output Format
Please provide your analysis in the following format:

### Architectural Overview
[Describe the overall architecture, patterns, and organization]

### Key Module Relationships
[List and describe the relationships between major modules]

### Critical Files Analysis
[Analyze the largest and most connected files in the codebase]

### Dependency Graph
[Textual representation of the major dependencies]

### Recommendations
[Actionable suggestions for architectural improvements]

EOL

# Create summary document
cat <<EOL > "$SUMMARY_FILE"
# Application Summary

## Architecture
This document provides a summary of the application's architecture, key modules, and their relationships.

## Key Modules
- Placeholder for module descriptions.
- Include information about the functionality, dependencies, and interaction with other modules.

## Key Files by Size
- See codebase_stats.txt for a complete listing of files by line count
- The largest files often represent core functionality or areas that might need refactoring

## High-Level Next Steps for LLM
1. Identify and generate module summaries for frontend, backend, and database.
2. Document core workflows and user journeys within the application.
3. Use the LLM relationship prompt (llm_relationship_prompt.txt) to generate a comprehensive relationship analysis.
4. Pay special attention to the largest files and their relationships to other components.

EOL

# Generate module summaries with placeholders for customization
echo "Generating module summaries... Please customize the contents as necessary."
cat <<EOL > "$MODULE_SUMMARY_DIR/frontend_summary.txt"
# Frontend Module Summary
- **Purpose**: Describe the frontend's role in the application.
- **Key Components**: List key components such as main frameworks, libraries, and UI components.
- **Dependencies**: Mention any dependencies on backend services or external APIs.
- **Largest Files**: Identify the largest frontend files and their purposes.
EOL

cat <<EOL > "$MODULE_SUMMARY_DIR/backend_summary.txt"
# Backend Module Summary
- **Purpose**: Describe the backend's role in the application.
- **Key Components**: List key components such as main frameworks, APIs, and data handling.
- **Dependencies**: Mention any database connections and external services it relies on.
- **Largest Files**: Identify the largest backend files and their purposes.
EOL

cat <<EOL > "$MODULE_SUMMARY_DIR/database_summary.txt"
# Database Module Summary
- **Purpose**: Describe the database's role in the application.
- **Key Components**: List database types, schema designs, and any ORM tools used.
- **Dependencies**: Mention the relationships with the backend and data sources.
- **Largest Files**: Identify the largest database-related files and their purposes.
EOL

# Document core workflows with placeholders for customization
echo "Identifying core workflows... Please customize the contents as necessary."
cat <<EOL > "$WORKFLOWS_FILE"
# Core Workflows

## User Journeys
1. **Product Browsing**:
   - Relevant code files: [list of files responsible for navigation, product listing]
   - File sizes: [line counts for each key file]
  
2. **Checkout Process**:
   - Relevant code files: [list of files responsible for cart management, payment handling]
   - File sizes: [line counts for each key file]
  
3. **User Authentication**:
   - Relevant code files: [list of files responsible for login, logout, user session management]
   - File sizes: [line counts for each key file]

### Note:
- The workflows and summaries provided are examples. Please modify them to fit the specific use case and structure of your application repository.
- Pay special attention to large files, as they may represent core functionality or potential refactoring opportunities.
EOL

# Generate vector relationship graph prompt
cat <<EOL > "$VECTOR_GRAPH_FILE"
# Vector Relationship Graph Prompt

Using the following files:
- $STRUCTURE_FILE
- $DEPENDENCY_MAP_FILE
- $STATS_FILE

Generate a **vector relationship graph** of the codebase:
- Nodes represent files or modules
- Edges represent dependencies (imports, requires)
- Weight edges by frequency or importance (based on file size or connections)
- Identify clusters of related modules
- Format the graph in DOT format (Graphviz) for visualization or output as JSON for use in a vector database
EOL

# Completion message
echo "Directory structure and statistics saved to $STRUCTURE_FILE."
echo "Detailed statistics saved to $STATS_FILE."
echo "File dependency map saved to $DEPENDENCY_MAP_FILE."
echo "LLM relationship analysis prompt saved to $LLM_PROMPT_FILE."
echo "Summary document created at $SUMMARY_FILE."
echo "Module summaries created in the $MODULE_SUMMARY_DIR directory."
echo "Core workflows documented in $WORKFLOWS_FILE."
echo "Vector relationship graph prompt saved to $VECTOR_GRAPH_FILE."