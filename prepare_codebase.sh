#!/bin/bash
set -x  # Enable debugging

# Set output files
STRUCTURE_FILE="codebase_structure.txt"
DEPENDENCY_MAP_FILE="dependency_map.txt"
DOC_NODES_FILE="documentation_nodes.txt"
USER_DOC_MAP_FILE="user_doc_mapping.txt"
VECTOR_GRAPH_FILE="vector_relationship_graph.txt"
LLM_PROMPT_FILE="llm_prompts.txt"
SYSTEM_ARCHITECTURE_FILE="system_architecture.txt"
TECHNICAL_DEBT_FILE="technical_debt.txt"
README_CONTEXT_FILE="readme_context.txt"

# Create prompts directory structure
PROMPTS_DIR="./prompts"
mkdir -p "$PROMPTS_DIR"/{system,technical,dependency,custom}

# Check if project_environment.txt exists and source it if it does
if [ -f "project_environment.txt" ]; then
  echo "Loading environment information from project_environment.txt..."
  # Source the environment info
  source project_environment.txt
else
  echo "No project_environment.txt found. Running capture_env_info.sh to generate it..."
  # Check if capture_env_info.sh exists and run it
  if [ -f "./capture_env_info.sh" ]; then
    bash ./capture_env_info.sh
    source project_environment.txt
  else
    echo "Warning: capture_env_info.sh not found. Environment information will be limited."
  fi
fi

# Define directories to ignore for the file search
IGNORE_DIRS=("node_modules" ".venv" "venv" "vendor" "test_env")

# Create directory for module summaries
mkdir -p module_summaries

# Construct the 'find' command to exclude ignored directories
FIND_CMD="find ."
for dir in "${IGNORE_DIRS[@]}"; do
    FIND_CMD+=" -path ./$dir -prune -o"
done
FIND_CMD+=" -type f \( -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name '*.py' -o -name '*.md' -o -name '*.mdx' -o -name '*.sh' -o -name '*.yaml' -o -name '*.yml' -o -name '*.json' -o -name '*.cfg' -o -name '*.conf' -o -name '*.tfvars' -o -name '*.tf' \) -print | sort"

# Debugging: Show the generated find command
echo "Executing command: $FIND_CMD"

# Execute and store results
eval "$FIND_CMD" > "$STRUCTURE_FILE"

# Check if files were captured
if [ ! -s "$STRUCTURE_FILE" ]; then
    echo "⚠️ Warning: No matching files found. Please check directory paths."
fi

# Count the number of files found.
FILE_COUNT=$(wc -l < "$STRUCTURE_FILE")

# 1. Code Dependency Graph
echo "Generating code dependency graph..."
echo "# Code Dependency Graph" > "$DEPENDENCY_MAP_FILE"
echo "# Generated on $(date)" >> "$DEPENDENCY_MAP_FILE"
echo "# Environment: $OPERATING_SYSTEM" >> "$DEPENDENCY_MAP_FILE"
if [ -n "$PYTHON_VERSION" ]; then
  echo "# Python: $PYTHON_VERSION" >> "$DEPENDENCY_MAP_FILE"
fi
if [ -n "$NODE_VERSION" ]; then
  echo "# Node.js: $NODE_VERSION" >> "$DEPENDENCY_MAP_FILE"
fi
if [ -n "$ANSIBLE_VERSION" ]; then
  echo "# Ansible: $ANSIBLE_VERSION" >> "$DEPENDENCY_MAP_FILE"
fi
echo "" >> "$DEPENDENCY_MAP_FILE"

# Function to extract dependencies, tailored for graph generation
extract_dependencies() {
    local file="$1"
    local file_type="$2"
    
    # Add "./" prefix for consistency
    local current_dir="./"
    file="${current_dir}${file#./}"

    if [[ "$file_type" == "python" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ ^(import|from) ]]; then
                line=$(echo "$line" | sed 's/#.*$//' | tr -s ' ')
                if [[ "$line" != *'"'* && "$line" != *"'"* ]]; then
                    # Capture module/file being imported
                    imported_module=$(echo "$line" | sed -e 's/import //g' -e 's/from //g' -e 's/ .*//g' | tr -d ' ')
                    echo "$file -> $imported_module (Python)" >> "$DEPENDENCY_MAP_FILE"
                fi
            fi
        done < "$file"
    elif [[ "$file_type" == "js" || "$file_type" == "jsx" || "$file_type" == "ts" || "$file_type" == "tsx" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ (import|require) ]]; then
                line=$(echo "$line" | sed 's/\/\/.*$//' | sed 's/\/\*.*\*\///g' | tr -s ' ')
                 if [[ "$line" != *'"'* && "$line" != *"'"* ]]; then
                    # Capture module/file being imported
                    imported_module=$(echo "$line" | sed -n "s/.*\(import\|require\).*\(('|\"\)\([^'\"]*\)\('|\"\).*/\3/p" | tr -d ' ')
                    echo "$file -> $imported_module (JavaScript/TypeScript)" >> "$DEPENDENCY_MAP_FILE"
                fi
            fi
        done < "$file"
    elif [[ "$file_type" == "sh" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ ^(source|.) ]]; then
               line=$(echo "$line" | sed 's/#.*$//' | tr -s ' ')
                if [[ "$line" != *'"'* && "$line" != *"'"* ]]; then
                    imported_module=$(echo "$line" | sed -n "s/source \([^ ]*\).*/\1/p" | tr -d ' ')
                    echo "$file -> $imported_module (Shell)" >> "$DEPENDENCY_MAP_FILE"
                fi
            fi
        done < "$file"
     elif [[ "$file_type" == "yaml" || "$file_type" == "yml" ]]; then
        while IFS= read -r line; do
             if [[ "$line" =~ ^(\ *[a-zA-Z0-9_-]+\:) ]]; then
                echo "$file -> $line (YAML)" >> "$DEPENDENCY_MAP_FILE"
             fi
        done < "$file"
    elif [[ "$file_type" == "tf" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ resource|module|data ]]; then
                line=$(echo "$line" | sed 's/#.*$//' | tr -s ' ')
                echo "$file -> $line (Terraform)" >> "$DEPENDENCY_MAP_FILE"
            fi
        done < "$file"
    fi
}

# Process each file from the structure file
while IFS= read -r file; do
    if [ -f "$file" ]; then
        extension="${file##*.}"
        case "$extension" in
            py)      file_type="python";;
            js|jsx)  file_type="js";;
            ts|tsx)  file_type="ts";;
            sh)      file_type="sh";;
            yaml)    file_type="yaml";;
            yml)     file_type="yml";;
            *)       file_type="other";;
        esac
        if [[ "$file_type" == "python" || "$file_type" == "js" || "$file_type" == "ts" || "$file_type" == "sh" || "$file_type" == "yaml" || "$file_type" == "yml" ]]; then
            extract_dependencies "$file" "$file_type"
        fi
    fi
done < "$STRUCTURE_FILE"

# 2. Documentation Linking
echo "Generating documentation nodes..."
echo "# Documentation Nodes" > "$DOC_NODES_FILE"

# Function to extract function/class signatures (for documentation linking)
extract_doc_nodes() {
    local file="$1"
    local file_type="$2"
    
     # Add "./" prefix for consistency
    local current_dir="./"
    file="${current_dir}${file#./}"

    if [[ "$file_type" == "python" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ ^(def|class) ]]; then
                # Extract function/class name and signature
                signature=$(echo "$line" | sed 's/#.*$//' | tr -s ' ')
                echo "$file: $signature (Python)" >> "$DOC_NODES_FILE"
            fi
        done < "$file"
    elif [[ "$file_type" == "js" || "$file_type" == "jsx" || "$file_type" == "ts" || "$file_type" == "tsx" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ ^(function|class) ]]; then
                signature=$(echo "$line" | sed 's/\/\/.*$//' | sed 's/\/\*.*\*\///g' | tr -s ' ')
                echo "$file: $signature (JavaScript/TypeScript)" >> "$DOC_NODES_FILE"
            fi
        done < "$file"
     elif [[ "$file_type" == "sh" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ ^(function ) ]]; then
                signature=$(echo "$line" | sed 's/#.*$//' | tr -s ' ')
                echo "$file: $signature (Shell)" >> "$DOC_NODES_FILE"
            fi
        done < "$file"
    fi
}

# Process each file to extract documentation nodes
while IFS= read -r file; do
    if [ -f "$file" ]; then
        extension="${file##*.}"
        case "$extension" in
            py)      file_type="python";;
            js|jsx)  file_type="js";;
            ts|tsx)  file_type="ts";;
            sh)      file_type="sh";;
            yaml)    file_type="yaml";;
            yml)     file_type="yml";;
            *)       file_type="other";;
        esac
        if [[ "$file_type" == "python" || "$file_type" == "js" || "$file_type" == "ts" || "$file_type" == "sh" ]]; then
            extract_doc_nodes "$file" "$file_type"
        fi
    fi
done < "$STRUCTURE_FILE"

# 3. User Documentation Mapping
echo "Generating user documentation mapping..."
echo "# User Documentation Mapping" > "$USER_DOC_MAP_FILE"

#  Function to map user documentation (Markdown files) to code elements.
map_user_docs() {
    local file="$1"
     # Add "./" prefix for consistency
    local current_dir="./"
    file="${current_dir}${file#./}"
    
    # Very basic mapping:  Look for code element names in Markdown
    if [[ "$file" =~ \.md$ || "$file" =~ \.mdx$ ]]; then # Only process Markdown files
        while IFS= read -r line; do
            # This is a simplified approach.  A real tool would use AST parsing.
            if [[ "$line" =~ (def |class |function ) ]]; then  # very rough
                echo "$file contains: $line" >> "$USER_DOC_MAP_FILE"
            fi
        done < "$file"
    fi
}

# Process each file to map user documentation
while IFS= read -r file; do
    if [ -f "$file" ]; then
        extension="${file##*.}"
        case "$extension" in
            md|mdx)  file_type="md";;
            *)       file_type="other";;
        esac
        if [[ "$file_type" == "md" ]]; then
            map_user_docs "$file" >> "$USER_DOC_MAP_FILE"
        fi
    fi
done < "$STRUCTURE_FILE"

# Extract key information from README.md
echo "Analyzing README.md for project context..."
echo "# README.md Analysis" > "$README_CONTEXT_FILE"
echo "# Generated on $(date)" >> "$README_CONTEXT_FILE"
echo "" >> "$README_CONTEXT_FILE"

if [ -f "README.md" ]; then
  # Extract project name and description
  echo "## Project Information" >> "$README_CONTEXT_FILE"
  # Look for a title (# Title)
  PROJECT_TITLE=$(grep "^# " README.md | head -1 | sed 's/^# //')
  echo "Project Title: $PROJECT_TITLE" >> "$README_CONTEXT_FILE"
  
  # Extract what appears to be a project description (first paragraph after title)
  PROJECT_DESCRIPTION=$(sed -n '/^# /,/^$/{/^# /d; /^$/d; p}' README.md | head -3)
  echo "Project Description: $PROJECT_DESCRIPTION" >> "$README_CONTEXT_FILE"
  
  # Look for architecture information
  echo -e "\n## Architecture Information" >> "$README_CONTEXT_FILE"
  grep -A 10 -i "architecture\|structure\|design\|overview" README.md >> "$README_CONTEXT_FILE" 2>/dev/null || echo "No explicit architecture information found." >> "$README_CONTEXT_FILE"
  
  # Extract documentation links
  echo -e "\n## Documentation Links" >> "$README_CONTEXT_FILE"
  grep -o "\[.*\](.*)" README.md | grep -i "doc\|guide\|tutorial\|wiki" >> "$README_CONTEXT_FILE" 2>/dev/null || echo "No documentation links found." >> "$README_CONTEXT_FILE"
  
  # Check for setup instructions
  echo -e "\n## Setup Instructions" >> "$README_CONTEXT_FILE"
  grep -A 15 -i "setup\|install\|getting started\|prerequisites" README.md >> "$README_CONTEXT_FILE" 2>/dev/null || echo "No setup instructions found." >> "$README_CONTEXT_FILE"
  
  # Prepare a summary for prompts
  README_SUMMARY=$(echo "$PROJECT_DESCRIPTION" | tr '\n' ' ' | cut -c 1-200)
  
  echo "README.md analysis saved to $README_CONTEXT_FILE"
else
  echo "No README.md found at the root of the project." >> "$README_CONTEXT_FILE"
  # Try to find READMEs in subdirectories
  READMES=$(find . -name "README.md" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*")
  if [ -n "$READMES" ]; then
    echo "Found README.md files in subdirectories: $READMES" >> "$README_CONTEXT_FILE"
    # Process the first README found
    FIRST_README=$(echo "$READMES" | head -1)
    echo "Analyzing $FIRST_README as fallback..." >> "$README_CONTEXT_FILE"
    
    # Extract project name and description
    echo -e "\n## Project Information (from $FIRST_README)" >> "$README_CONTEXT_FILE"
    PROJECT_TITLE=$(grep "^# " "$FIRST_README" | head -1 | sed 's/^# //')
    echo "Project Title: $PROJECT_TITLE" >> "$README_CONTEXT_FILE"
    
    PROJECT_DESCRIPTION=$(sed -n '/^# /,/^$/{/^# /d; /^$/d; p}' "$FIRST_README" | head -3)
    echo "Project Description: $PROJECT_DESCRIPTION" >> "$README_CONTEXT_FILE"
    
    # Prepare a summary for prompts
    README_SUMMARY=$(echo "$PROJECT_DESCRIPTION" | tr '\n' ' ' | cut -c 1-200)
  else
    echo "No README.md files found in the project." >> "$README_CONTEXT_FILE"
    README_SUMMARY="No README.md found in the project."
  fi
fi

# Copy README context file to prompts directory
cp "$README_CONTEXT_FILE" "$PROMPTS_DIR/system/"

# NEW: System Architecture Analysis 
echo "Analyzing system architecture..."
echo "# System Architecture Analysis" > "$SYSTEM_ARCHITECTURE_FILE"
echo "# Generated on $(date)" >> "$SYSTEM_ARCHITECTURE_FILE"
echo "# Environment: $OPERATING_SYSTEM" >> "$SYSTEM_ARCHITECTURE_FILE"
echo "" >> "$SYSTEM_ARCHITECTURE_FILE"

# Identify key system components based on directory structure and file types
echo "## System Components" >> "$SYSTEM_ARCHITECTURE_FILE"

# Count files by type to identify primary languages/frameworks
echo "### Primary Languages/Frameworks" >> "$SYSTEM_ARCHITECTURE_FILE"
echo "Counting files by extension to identify primary technologies..." >> "$SYSTEM_ARCHITECTURE_FILE"
grep -o '\.[^./]*$' "$STRUCTURE_FILE" | sort | uniq -c | sort -nr >> "$SYSTEM_ARCHITECTURE_FILE"

# Identify architectural patterns based on directory names and file content
echo "" >> "$SYSTEM_ARCHITECTURE_FILE"
echo "### Detected Architectural Patterns" >> "$SYSTEM_ARCHITECTURE_FILE"

# Look for common architectural clues in directory names
echo "Directory structure analysis:" >> "$SYSTEM_ARCHITECTURE_FILE"
for pattern in "api" "service" "controller" "model" "view" "component" "middleware" "util" "helper" "config" "test" "frontend" "backend" "client" "server"; do
  count=$(find . -type d -name "*$pattern*" | wc -l)
  if [ "$count" -gt 0 ]; then
    echo "- Found $count directories matching pattern '$pattern'" >> "$SYSTEM_ARCHITECTURE_FILE"
  fi
done

# Check for deployment and infrastructure files
echo "" >> "$SYSTEM_ARCHITECTURE_FILE"
echo "### Infrastructure and Deployment" >> "$SYSTEM_ARCHITECTURE_FILE"
for file in "Dockerfile" "docker-compose.yml" ".github/workflows" "Jenkinsfile" "terraform" "k8s" "helm"; do
  if [ -e "$file" ]; then
    echo "- Found $file" >> "$SYSTEM_ARCHITECTURE_FILE"
  fi
done

# NEW: Technical Debt Analysis
echo "Gathering technical debt indicators..."
TECH_DEBT_DATA_FILE="technical_debt_data.txt"
TECH_DEBT_PROMPT_FILE="$PROMPTS_DIR/technical/technical_debt_prompt.txt"
echo "# Technical Debt Indicators" > "$TECH_DEBT_DATA_FILE"
echo "# Generated on $(date)" >> "$TECH_DEBT_DATA_FILE"
echo "" >> "$TECH_DEBT_DATA_FILE"

# Count files by type for primary languages
echo "## Primary Languages" >> "$TECH_DEBT_DATA_FILE"
LANGUAGE_COUNTS=$(grep -o '\.[^./]*$' "$STRUCTURE_FILE" | sort | uniq -c | sort -nr)
echo "$LANGUAGE_COUNTS" >> "$TECH_DEBT_DATA_FILE"
PRIMARY_LANGUAGES=$(echo "$LANGUAGE_COUNTS" | head -5 | awk '{print $2}' | tr '\n' ', ' | sed 's/,$//' | sed 's/\.//')
LANGUAGE_COUNT=$(echo "$LANGUAGE_COUNTS" | wc -l)

# Look for code comments indicating technical debt
echo -e "\n## TODO, FIXME, and HACK Comments" >> "$TECH_DEBT_DATA_FILE"
TODO_COMMENTS=$(grep -r --include="*.py" --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" --include="*.sh" --include="*.yml" --include="*.yaml" --include="*.tf" "TODO\|FIXME\|HACK" . 2>/dev/null | grep -v "node_modules\|venv\|.git" | sort)
TODO_COUNT=$(echo "$TODO_COMMENTS" | grep -v '^$' | wc -l)
echo "Found $TODO_COUNT TODO/FIXME/HACK comments" >> "$TECH_DEBT_DATA_FILE"
# Sample up to 10 TODO comments
TODO_SAMPLES=$(echo "$TODO_COMMENTS" | head -10)
echo "$TODO_SAMPLES" >> "$TECH_DEBT_DATA_FILE"

# Check for deprecated dependencies if we have package.json or requirements.txt
echo -e "\n## Dependency Analysis" >> "$TECH_DEBT_DATA_FILE"
NODE_DEPS=""
if [ -f "package.json" ]; then
  echo "### Node.js Dependencies" >> "$TECH_DEBT_DATA_FILE"
  NODE_DEPS=$(grep -A 100 "dependencies" package.json | grep -B 100 "}" | grep ":" | head -15)
  echo "$NODE_DEPS" >> "$TECH_DEBT_DATA_FILE"
fi

PYTHON_DEPS=""
if [ -f "requirements.txt" ]; then
  echo -e "\n### Python Dependencies" >> "$TECH_DEBT_DATA_FILE"
  PYTHON_DEPS=$(cat requirements.txt | head -15)
  echo "$PYTHON_DEPS" >> "$TECH_DEBT_DATA_FILE"
fi

# Look for large files that might indicate complexity issues
echo -e "\n## Potentially Complex Files (> 500 lines)" >> "$TECH_DEBT_DATA_FILE"
LARGE_FILES=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/.git/*" -exec wc -l {} \; | awk '$1 > 500' | sort -nr)
LARGE_FILES_COUNT=$(echo "$LARGE_FILES" | grep -v '^$' | wc -l)
echo "Found $LARGE_FILES_COUNT large files (>500 lines)" >> "$TECH_DEBT_DATA_FILE"
LARGE_FILES_SAMPLES=$(echo "$LARGE_FILES" | head -10)
echo "$LARGE_FILES_SAMPLES" >> "$TECH_DEBT_DATA_FILE"

# Check for potential circular dependencies
echo -e "\n## Potential Circular Dependencies" >> "$TECH_DEBT_DATA_FILE"
# This is a very basic check that could be improved
if [ -f "$DEPENDENCY_MAP_FILE" ]; then
  DEPENDENCY_SAMPLES=$(grep " -> " "$DEPENDENCY_MAP_FILE" | head -15)
  IMPORT_COUNT=$(grep -c " -> " "$DEPENDENCY_MAP_FILE")
  # Find modules that are both imported and import others
  HIGH_COUPLING=$(grep " -> " "$DEPENDENCY_MAP_FILE" | awk '{print $1; print $3}' | sort | uniq -c | sort -nr | head -10)
  echo "Found $IMPORT_COUNT import relationships" >> "$TECH_DEBT_DATA_FILE"
  echo -e "\nHighly coupled components:" >> "$TECH_DEBT_DATA_FILE"
  echo "$HIGH_COUPLING" >> "$TECH_DEBT_DATA_FILE"
fi

# Now create the technical debt prompt for LLM
echo "Generating technical debt analysis prompt for LLM..."

cat > "$TECH_DEBT_PROMPT_FILE" << EOL
# Technical Debt Analysis Prompt

## Context
You are analyzing the technical debt in a codebase with the following characteristics:
- ${FILE_COUNT} files across ${LANGUAGE_COUNT} languages/frameworks
- Primary languages: ${PRIMARY_LANGUAGES}
- Environment: ${OPERATING_SYSTEM:-Unknown OS}, Python ${PYTHON_VERSION:-Unknown}, Node.js ${NODE_VERSION:-Unknown}
- Project summary: ${README_SUMMARY:-No project description available}

## Available Data
The following data has been collected to assist your analysis:
1. TODO/FIXME/HACK comments (count: ${TODO_COUNT})
2. Large files exceeding 500 lines (count: ${LARGE_FILES_COUNT})
3. Dependency information (${IMPORT_COUNT} import relationships found)
4. Directory structure patterns and architectural indicators

## Sample Data Points
### TODO/FIXME Examples:
${TODO_SAMPLES}

### Large Files:
${LARGE_FILES_SAMPLES}

### Dependency Data:
${DEPENDENCY_SAMPLES}

### Highly Coupled Components:
${HIGH_COUPLING}

## Instructions
Please analyze the technical debt in this codebase by:

1. **Categorizing the technical debt** into these types:
   - Code quality issues
   - Architectural problems
   - Outdated dependencies 
   - Testing gaps
   - Documentation shortfalls

2. **Identifying potential root causes** of the technical debt:
   - Time pressure and deadlines
   - Knowledge gaps
   - Changing requirements
   - Architectural erosion over time
   - Legacy code integration

3. **Assessing the potential impact** of the technical debt:
   - On system stability
   - On maintainability
   - On performance
   - On security
   - On team productivity

4. **Recommending a prioritized remediation plan** that:
   - Addresses high-impact issues first
   - Considers interdependencies between components
   - Provides realistic, incremental steps
   - Balances short-term fixes with long-term improvements
   - Suggests preventative measures to avoid future debt

5. **Creating a high-level technical debt map** showing:
   - Which components contain the most concerning debt
   - How the debt in one area affects other parts of the system
   - Which areas would provide the highest ROI if addressed

Please format your response as a structured technical debt analysis report with clear sections, actionable insights, and system-level thinking.
EOL

# Generate a minimal technical debt file that points to the prompt
cat > "$TECHNICAL_DEBT_FILE" << EOL
# Technical Debt Analysis
# Generated on $(date)

This file contains basic technical debt indicators. For a comprehensive analysis,
copy the contents of "$TECH_DEBT_PROMPT_FILE" and submit it to an LLM like Claude,
ChatGPT, or use it with Cursor's AI capabilities.

## Summary of Technical Debt Indicators
- TODO/FIXME/HACK comments: ${TODO_COUNT}
- Large files (>500 lines): ${LARGE_FILES_COUNT}
- Import relationships: ${IMPORT_COUNT:-Unknown}
- Primary languages: ${PRIMARY_LANGUAGES}

For full data points, see: ${TECH_DEBT_DATA_FILE}
For LLM analysis prompt, see: ${TECH_DEBT_PROMPT_FILE}

To get a complete analysis, run:
cat ${TECH_DEBT_PROMPT_FILE} | pbcopy  # On macOS
# or
cat ${TECH_DEBT_PROMPT_FILE} | xclip -selection clipboard  # On Linux with xclip
# Then paste into your preferred LLM interface
EOL

# Update project_environment.txt with technical debt indicators
if [ -f "project_environment.txt" ]; then
  echo -e "\n# Technical Debt Indicators" >> project_environment.txt
  echo "TECH_DEBT_TODO_COUNT=\"$TODO_COUNT\"" >> project_environment.txt
  echo "TECH_DEBT_LARGE_FILES_COUNT=\"$LARGE_FILES_COUNT\"" >> project_environment.txt
  echo "TECH_DEBT_PROMPT_FILE=\"$TECH_DEBT_PROMPT_FILE\"" >> project_environment.txt
  echo "TECH_DEBT_DATA_FILE=\"$TECH_DEBT_DATA_FILE\"" >> project_environment.txt
fi

# Generate Dependency Analysis Prompt
echo "Generating dependency analysis prompt for LLM..."
DEPENDENCY_ANALYSIS_FILE="dependency_analysis.txt"
DEPENDENCY_PROMPT_FILE="$PROMPTS_DIR/dependency/dependency_analysis_prompt.txt"

# Get some key metrics for the prompt
MODULE_COUNT=$(grep " -> " "$DEPENDENCY_MAP_FILE" | awk '{print $1}' | sort | uniq | wc -l)
IMPORT_COUNT=$(grep -c " -> " "$DEPENDENCY_MAP_FILE")
# Find highly coupled modules
HIGH_COUPLING=$(grep " -> " "$DEPENDENCY_MAP_FILE" | awk '{print $1}' | sort | uniq -c | sort -nr | head -10)
# Find modules with most incoming dependencies
HIGH_INCOMING=$(grep " -> " "$DEPENDENCY_MAP_FILE" | awk '{print $3}' | sort | uniq -c | sort -nr | head -10)

cat > "$DEPENDENCY_PROMPT_FILE" << EOL
# Dependency Graph Analysis Prompt

## Context
You are analyzing the dependency structure in a codebase with the following characteristics:
- ${FILE_COUNT} files across ${LANGUAGE_COUNT} languages/frameworks
- ${MODULE_COUNT} modules with dependencies
- ${IMPORT_COUNT} total import relationships
- Primary languages: ${PRIMARY_LANGUAGES}
- Environment: ${OPERATING_SYSTEM:-Unknown OS}, Python ${PYTHON_VERSION:-Unknown}, Node.js ${NODE_VERSION:-Unknown}
- Project summary: ${README_SUMMARY:-No project description available}

## Available Data
The dependency map shows how modules depend on each other. Here are some key metrics:

### Modules with most outgoing dependencies (highest coupling):
${HIGH_COUPLING}

### Modules with most incoming dependencies (highest dependency):
${HIGH_INCOMING}

### Sample dependencies:
$(grep " -> " "$DEPENDENCY_MAP_FILE" | head -20)

## Instructions
Please analyze the dependency structure of this codebase by:

1. **Identifying problematic dependency patterns**:
   - Modules with excessive coupling (too many dependencies)
   - Core modules that too many other modules depend on (high risk)
   - Potential circular dependencies or dependency chains
   - Architectural layering violations (if detectable)

2. **Evaluating the modularity of the system**:
   - Is the codebase well-modularized or tightly coupled?
   - Are there clear boundaries between subsystems?
   - Does the dependency structure reflect good architecture?
   - Are there signs of "spaghetti code" in the dependencies?

3. **Recommending improvements to the dependency structure**:
   - Which modules should be refactored to reduce coupling?
   - How could dependencies be better organized?
   - Are there opportunities to introduce abstractions/interfaces?
   - What architectural patterns might help improve the structure?

4. **Creating a dependency health assessment**:
   - Rate the overall health of the dependency structure
   - Identify the highest priority areas for improvement
   - Suggest metrics to track dependency health over time
   - Estimate the long-term maintainability based on dependencies

Please format your response as a structured dependency analysis report with clear sections, 
visualizations (described in text if needed), and specific, actionable recommendations.
EOL

# Generate a minimal dependency analysis file that points to the prompt
cat > "$DEPENDENCY_ANALYSIS_FILE" << EOL
# Dependency Analysis
# Generated on $(date)

This file contains basic dependency metrics. For a comprehensive analysis,
copy the contents of "$DEPENDENCY_PROMPT_FILE" and submit it to an LLM like Claude,
ChatGPT, or use it with Cursor's AI capabilities.

## Summary of Dependency Metrics
- Modules with dependencies: ${MODULE_COUNT}
- Import relationships: ${IMPORT_COUNT}
- Primary languages: ${PRIMARY_LANGUAGES}

For the dependency map, see: ${DEPENDENCY_MAP_FILE}
For LLM analysis prompt, see: ${DEPENDENCY_PROMPT_FILE}

To get a complete analysis, run:
cat ${DEPENDENCY_PROMPT_FILE} | pbcopy  # On macOS
# or
cat ${DEPENDENCY_PROMPT_FILE} | xclip -selection clipboard  # On Linux with xclip
# Then paste into your preferred LLM interface
EOL

# Update project_environment.txt with dependency analysis references
if [ -f "project_environment.txt" ]; then
  echo -e "\n# Dependency Analysis Information" >> project_environment.txt
  echo "DEPENDENCY_PROMPT_FILE=\"$DEPENDENCY_PROMPT_FILE\"" >> project_environment.txt
  echo "DEPENDENCY_ANALYSIS_FILE=\"$DEPENDENCY_ANALYSIS_FILE\"" >> project_environment.txt
  echo "MODULE_COUNT=\"$MODULE_COUNT\"" >> project_environment.txt
  echo "IMPORT_COUNT=\"$IMPORT_COUNT\"" >> project_environment.txt
fi

# Generate a meta-prompt to create custom analysis prompts
echo "Creating meta-prompt for generating custom analysis prompts..."
META_PROMPT_FILE="$PROMPTS_DIR/meta_prompt_generator.txt"

cat > "$META_PROMPT_FILE" << EOL
# Meta-Prompt: Generate Custom Codebase Analysis Prompts

## Context
You've been given information about a codebase with these characteristics:
- ${FILE_COUNT} files across ${LANGUAGE_COUNT} languages/frameworks
- Primary languages: ${PRIMARY_LANGUAGES}
- Environment: ${OPERATING_SYSTEM:-Unknown OS}, Python ${PYTHON_VERSION:-Unknown}, Node.js ${NODE_VERSION:-Unknown}
- Project summary: ${README_SUMMARY:-No project description available}
- Detected architectural patterns: $(grep "Found" "$SYSTEM_ARCHITECTURE_FILE" | head -5 | tr '\n' ', ' | sed 's/,$//')

## Task
Generate a specialized analysis prompt that will help developers understand and improve this codebase. The prompt should be tailored to this specific codebase's characteristics and the developer's goal.

## Developer's Goal
[REPLACE THIS WITH YOUR SPECIFIC GOAL, e.g., "Improve test coverage", "Refactor for better performance", "Prepare for cloud migration"]

## Instructions
1. Create a prompt that guides an LLM to analyze the codebase specifically for the stated goal
2. Include relevant context from the codebase metrics above
3. Structure the prompt with clear sections including:
   - Background information about the codebase
   - Specific questions to address about the goal
   - Instructions for formatting the response
4. Focus on systems thinking principles that consider the entire codebase, not just isolated components
5. Include specific metrics or artifacts the LLM should look for in its analysis

## Output
Provide the complete text of the new analysis prompt, ready to be saved to a file and used with an LLM.
EOL

echo "Meta-prompt generator created at $META_PROMPT_FILE"

# Create a README for the prompts directory
cat > "$PROMPTS_DIR/README.md" << EOL
# Analysis Prompts

This directory contains prompts for analyzing the codebase using LLMs:

- **system/**: Prompts related to overall system architecture
- **technical/**: Prompts for analyzing technical debt and code quality
- **dependency/**: Prompts for analyzing dependencies and module relationships
- **custom/**: Location for your custom analysis prompts

## Usage

1. Select a prompt relevant to your analysis needs
2. Copy its contents to your clipboard: \`cat prompts/technical/technical_debt_prompt.txt | pbcopy\`
3. Paste into an LLM like Claude or ChatGPT
4. Review the analysis and insights

## Creating Custom Prompts

Use the meta-prompt generator to create custom analysis prompts:
\`\`\`
cat prompts/meta_prompt_generator.txt | pbcopy
# Then paste into an LLM, replace the [GOAL] placeholder, and follow the instructions
\`\`\`

## Available Prompts

- **Meta-Prompt Generator**: Generate custom analysis prompts for specific goals
- **Technical Debt Analysis**: Analyze and prioritize technical debt in the codebase
- **Dependency Structure Analysis**: Evaluate modularity and identify problematic dependencies
- **System Architecture Analysis**: Understand overall system design and architecture
EOL

# Create .gitignore entry for the prompts directory
if [ -f ".gitignore" ]; then
    if ! grep -q "^prompts/" ".gitignore"; then
        echo "prompts/" >> ".gitignore"
        echo "Added prompts/ to .gitignore"
    fi
else
    echo "prompts/" > ".gitignore"
    echo "Created .gitignore with prompts/ entry"
fi

# Move LLM prompts to the system directory
LLM_PROMPT_FILE="$PROMPTS_DIR/system/llm_prompts.txt"

# 4. Vector Graph Generation (Modified to include system architecture insights)
echo "Generating vector relationship graph prompt..."
cat > "$LLM_PROMPT_FILE" << 'EOL'
# LLM Prompts for Codebase Analysis

## 1. Code Dependency Graph Generation
Generate a code dependency graph using the following data:
-   `'"$STRUCTURE_FILE"'`: Lists all files.
-   `'"$DEPENDENCY_MAP_FILE"'`: Shows dependencies between files.

## 2. Documentation Linking Analysis
Analyze documentation links using:
-   `'"$STRUCTURE_FILE"'`: Lists all files.
-   `'"$DOC_NODES_FILE"'`: Lists code elements (functions, classes).
-    `'"$USER_DOC_MAP_FILE"'`: Maps documentation to code elements.

## 3. System Architecture Analysis
Apply systems thinking to analyze the application architecture using:
-   `'"$STRUCTURE_FILE"'`: Lists all files
-   `'"$DEPENDENCY_MAP_FILE"'`: Shows dependencies between files
-   `'"$SYSTEM_ARCHITECTURE_FILE"'`: System components and patterns analysis
-   `'"$TECH_DEBT_DATA_FILE"'`: Technical debt indicators

### Task:
Analyze the codebase as a complete system, including:
1. Identify system boundaries and integration points
2. Detect feedback loops and circular dependencies
3. Identify potential bottlenecks and single points of failure
4. Assess emergent behavior that may arise from component interactions
5. Analyze technical debt impact on overall system health

### Output Format:
Provide a systems thinking analysis that includes:
```
{
  "system_boundaries": [
    {"name": "Frontend", "components": ["component1", "component2"]},
    {"name": "Backend", "components": ["component3", "component4"]},
    {"name": "Data Layer", "components": ["component5"]}
  ],
  "integration_points": [
    {"name": "API Gateway", "type": "external_boundary", "risk_level": "medium"},
    {"name": "Database Access", "type": "internal", "risk_level": "high"}
  ],
  "feedback_loops": [
    {"components": ["componentA", "componentB", "componentC"], "type": "circular_dependency", "impact": "high"}
  ],
  "bottlenecks": [
    {"component": "componentX", "reason": "High coupling with 15 other components", "impact": "critical"}
  ],
  "technical_debt_hotspots": [
    {"component": "legacy_module", "type": "obsolete_dependencies", "impact": "high", "remediation_cost": "medium"}
  ]
}
```

## 5. Technical Debt Analysis
For a detailed technical debt analysis, use the prompt in `'"$TECH_DEBT_PROMPT_FILE"'`. 
This prompt will guide you through:
1. Categorizing technical debt types
2. Identifying root causes
3. Assessing impact on the system
4. Creating a prioritized remediation plan
5. Mapping debt across the system

## 6. Dependency Structure Analysis
For a detailed analysis of the dependency structure, use the prompt in `'"$DEPENDENCY_PROMPT_FILE"'`.
This prompt will guide you through:
1. Identifying problematic dependency patterns
2. Evaluating system modularity
3. Recommending structural improvements
4. Creating a dependency health assessment
EOL

echo "Directory structure saved to $STRUCTURE_FILE."
echo "Code dependency graph data saved to $DEPENDENCY_MAP_FILE."
echo "Documentation nodes data saved to $DOC_NODES_FILE."
echo "User documentation mapping data saved to $USER_DOC_MAP_FILE."
echo "System architecture analysis saved to $SYSTEM_ARCHITECTURE_FILE."
echo "Technical debt data saved to $TECH_DEBT_DATA_FILE."
echo "Technical debt analysis prompt saved to $TECH_DEBT_PROMPT_FILE."
echo "Dependency analysis data saved to $DEPENDENCY_ANALYSIS_FILE."
echo "Dependency analysis prompt saved to $DEPENDENCY_PROMPT_FILE."
echo "README.md analysis saved to $README_CONTEXT_FILE."
echo "Meta-prompt generator saved to $META_PROMPT_FILE."
echo "Prompts directory created at $PROMPTS_DIR with README.md"
echo "LLM prompts saved to $LLM_PROMPT_FILE."

# Update project_environment.txt with analysis results
if [ -f "project_environment.txt" ]; then
  echo -e "\n# Codebase Analysis Results" >> project_environment.txt
  echo "FILE_COUNT=\"$FILE_COUNT\"" >> project_environment.txt
  echo "SYSTEM_ARCHITECTURE_FILE=\"$SYSTEM_ARCHITECTURE_FILE\"" >> project_environment.txt
  echo "TECHNICAL_DEBT_FILE=\"$TECHNICAL_DEBT_FILE\"" >> project_environment.txt
  echo "DEPENDENCY_MAP_FILE=\"$DEPENDENCY_MAP_FILE\"" >> project_environment.txt
  echo "README_CONTEXT_FILE=\"$README_CONTEXT_FILE\"" >> project_environment.txt
  echo "PROMPTS_DIR=\"$PROMPTS_DIR\"" >> project_environment.txt
  
  # README.md context
  if [ -n "$PROJECT_TITLE" ]; then
    echo "PROJECT_TITLE=\"$PROJECT_TITLE\"" >> project_environment.txt
  fi
  if [ -n "$README_SUMMARY" ]; then
    echo "PROJECT_DESCRIPTION=\"$README_SUMMARY\"" >> project_environment.txt
  fi
  
  # Count number of TODO/FIXME comments as a technical debt indicator
  TECH_DEBT_COUNT=$(grep -c "TODO\|FIXME\|HACK" "$TECHNICAL_DEBT_FILE")
  echo "TECHNICAL_DEBT_INDICATORS=\"$TECH_DEBT_COUNT\"" >> project_environment.txt
  
  echo "Updated project_environment.txt with codebase analysis results."
fi

echo "✅ Codebase analysis complete!"
echo "📊 To use the analysis prompts with an LLM, see $PROMPTS_DIR/README.md"
