# ADR Management

Architecture Decision Records (ADRs) are documents that capture important architectural decisions made along with their context and consequences. MCP Codebase Insight provides comprehensive tools for managing ADRs.

## Overview

The ADR management feature:
- Creates and maintains ADR documents
- Tracks decision history and status
- Links ADRs to code implementations
- Provides templates and workflows
- Enables searching and analysis of past decisions

## Features

### 1. ADR Creation

Create new ADRs with structured templates:

```python
# Example: Creating a new ADR
response = await client.post(
    "http://localhost:3000/api/adrs",
    json={
        "title": "Use GraphQL for API",
        "status": "PROPOSED",
        "context": {
            "problem": "Need efficient data fetching",
            "constraints": [
                "Multiple client applications",
                "Complex data relationships"
            ]
        },
        "options": [
            {
                "title": "GraphQL",
                "pros": [
                    "Flexible data fetching",
                    "Strong typing",
                    "Built-in documentation"
                ],
                "cons": [
                    "Learning curve",
                    "Complex server setup"
                ]
            },
            {
                "title": "REST",
                "pros": [
                    "Simple and familiar",
                    "Mature ecosystem"
                ],
                "cons": [
                    "Over/under fetching",
                    "Multiple endpoints"
                ]
            }
        ],
        "decision": "We will use GraphQL",
        "consequences": [
            "Need to train team on GraphQL",
            "Better client performance",
            "Simplified API evolution"
        ]
    }
)

adr = response.json()
print(f"Created ADR: {adr['id']}")
```

### 2. ADR Lifecycle Management

Track and update ADR status:

```python
# Update ADR status
response = await client.patch(
    f"http://localhost:3000/api/adrs/{adr_id}",
    json={
        "status": "ACCEPTED",
        "metadata": {
            "approved_by": "Architecture Board",
            "approved_date": "2024-03-26"
        }
    }
)
```

### 3. ADR Search and Analysis

Search through existing ADRs:

```python
# Search ADRs
response = await client.get(
    "http://localhost:3000/api/adrs/search",
    params={
        "query": "authentication",
        "status": "ACCEPTED",
        "date_from": "2023-01-01"
    }
)

results = response.json()
for adr in results["adrs"]:
    print(f"- {adr['title']} ({adr['status']})")
```

### 4. Code Implementation Tracking

Link ADRs to code implementations:

```python
# Link ADR to code
response = await client.post(
    f"http://localhost:3000/api/adrs/{adr_id}/implementations",
    json={
        "files": ["src/graphql/schema.ts", "src/graphql/resolvers/"],
        "pull_request": "https://github.com/org/repo/pull/123",
        "status": "IN_PROGRESS"
    }
)
```

## Usage

### Basic ADR Workflow

1. **Create ADR**
   ```bash
   # Using CLI
   mcp-codebase-insight adr new \
       --title "Use GraphQL for API" \
       --template graphql-decision
   ```

2. **Review and Collaborate**
   ```bash
   # Get ADR details
   curl http://localhost:3000/api/adrs/{adr_id}
   
   # Add comments
   curl -X POST http://localhost:3000/api/adrs/{adr_id}/comments \
       -d '{"text": "Consider Apollo Federation for microservices"}'
   ```

3. **Update Status**
   ```bash
   # Update status
   curl -X PATCH http://localhost:3000/api/adrs/{adr_id} \
       -d '{"status": "ACCEPTED"}'
   ```

4. **Track Implementation**
   ```bash
   # Add implementation details
   curl -X POST http://localhost:3000/api/adrs/{adr_id}/implementations \
       -d '{
           "files": ["src/graphql/"],
           "status": "COMPLETED",
           "metrics": {
               "coverage": 95,
               "performance_impact": "+12%"
           }
       }'
   ```

### ADR Templates

Create custom ADR templates:

```yaml
# templates/adr/microservice-decision.yaml
name: "Microservice Decision Template"
sections:
  - title: "Service Boundaries"
    required: true
    prompts:
      - "What domain does this service handle?"
      - "What are the integration points?"
  
  - title: "Data Ownership"
    required: true
    prompts:
      - "What data does this service own?"
      - "How is data shared with other services?"
  
  - title: "Technical Stack"
    required: true
    subsections:
      - "Language & Framework"
      - "Database"
      - "Message Queue"
      - "Deployment Platform"
```

## Configuration

### ADR Settings

```yaml
adr:
  # Storage settings
  storage:
    path: "./docs/adrs"
    format: "markdown"
    naming_convention: "YYYY-MM-DD-title"
  
  # Workflow settings
  workflow:
    require_approval: true
    approvers: ["arch-board"]
    auto_number: true
    
  # Templates
  templates:
    path: "./templates/adr"
    default: "basic-decision"
    
  # Implementation tracking
  implementation:
    require_evidence: true
    track_metrics: true
```

### Integration Settings

```yaml
integrations:
  github:
    enabled: true
    repo: "org/repo"
    pr_template: "adr-implementation"
    labels: ["architecture", "adr"]
  
  jira:
    enabled: true
    project: "ARCH"
    issue_type: "Architecture Decision"
```

## Best Practices

1. **ADR Creation**
   - Use clear, descriptive titles
   - Include sufficient context
   - Document all considered options
   - Be explicit about consequences

2. **Review Process**
   - Involve stakeholders early
   - Document discussions
   - Consider technical and business impact
   - Set clear acceptance criteria

3. **Implementation**
   - Link to concrete evidence
   - Track metrics and impact
   - Update status regularly
   - Document deviations

4. **Maintenance**
   - Review periodically
   - Update affected ADRs
   - Archive superseded decisions
   - Maintain traceability

## API Reference

### ADR Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/adrs` | GET | List all ADRs |
| `/api/adrs` | POST | Create new ADR |
| `/api/adrs/{id}` | GET | Get ADR details |
| `/api/adrs/{id}` | PATCH | Update ADR |
| `/api/adrs/search` | GET | Search ADRs |
| `/api/adrs/{id}/implementations` | POST | Add implementation |
| `/api/adrs/{id}/comments` | POST | Add comment |

### Response Format

```json
{
    "id": "uuid",
    "title": "string",
    "status": "string",
    "context": {
        "problem": "string",
        "constraints": ["string"]
    },
    "options": [{
        "title": "string",
        "pros": ["string"],
        "cons": ["string"]
    }],
    "decision": "string",
    "consequences": ["string"],
    "metadata": {
        "created_at": "datetime",
        "updated_at": "datetime",
        "created_by": "string",
        "approved_by": "string"
    },
    "implementations": [{
        "files": ["string"],
        "status": "string",
        "metrics": {}
    }]
}
```

## Troubleshooting

### Common Issues

1. **Template Not Found**
   ```bash
   # Check template directory
   ls -l templates/adr/
   
   # Verify template path in config
   cat config.yaml | grep template
   ```

2. **Permission Issues**
   ```bash
   # Fix ADR directory permissions
   chmod -R 755 docs/adrs/
   ```

3. **Integration Errors**
   ```bash
   # Check integration status
   curl http://localhost:3000/api/status/integrations
   ```

## Next Steps

- [ADR Templates Guide](adr/templates.md)
- [Integration Setup](../integration/index.md)
- [Workflow Customization](adr/workflow.md)
- [Metrics and Reporting](adr/metrics.md) 