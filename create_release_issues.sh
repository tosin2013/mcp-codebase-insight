#!/bin/bash
# Script to create GitHub issues for completing the release
# Run this with: ./create_release_issues.sh

REPO="tosin2013/mcp-codebase-insight"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

echo "Creating GitHub issues for release completion..."
echo ""

# Issue 1: Complete Documentation Management System
gh issue create \
  --repo "$REPO" \
  --title "Complete Documentation Management System" \
  --label "enhancement,documentation" \
  --body "## Description
Complete the documentation management system to support comprehensive codebase documentation.

## Tasks
- [ ] Implement proper text search in \`DocumentationManager\` (\`core/documentation.py:199\`)
- [ ] Add support for multiple documentation formats (Markdown, RST, HTML)
- [ ] Implement version tracking for documentation updates
- [ ] Add cross-reference resolution between docs
- [ ] Create documentation validation and linting tools

## Context
Currently marked as 'In Progress' in README.md. The DocumentationManager has a TODO for implementing proper text search functionality.

## Acceptance Criteria
- Text search is fully functional across all documentation
- Documentation can be imported from multiple formats
- Version history is tracked and queryable
- Cross-references are automatically validated
- Comprehensive tests are added

## Priority
High - Core feature for release

## References
- \`src/mcp_codebase_insight/core/documentation.py\`
- \`docs/features/documentation.md\`"

echo "✓ Issue 1: Documentation Management System"

# Issue 2: Advanced Pattern Detection
gh issue create \
  --repo "$REPO" \
  --title "Implement Advanced Pattern Detection" \
  --label "enhancement" \
  --body "## Description
Enhance pattern detection capabilities with advanced code analysis features.

## Tasks
- [ ] Implement pattern extraction logic in TaskManager (\`core/tasks.py:356\`)
- [ ] Add architectural pattern recognition (MVC, MVVM, Microservices, etc.)
- [ ] Create anti-pattern detection system
- [ ] Add code smell identification
- [ ] Implement design pattern suggestions
- [ ] Add pattern confidence scoring

## Context
Currently marked as 'In Progress' in README.md. The TaskManager has a TODO for implementing pattern extraction logic.

## Acceptance Criteria
- Pattern extraction is fully implemented and tested
- System can identify at least 10 common architectural patterns
- Anti-patterns are detected with actionable suggestions
- Pattern detection has >80% accuracy on test codebases
- Performance impact is <100ms per file analyzed

## Priority
High - Core feature for release

## References
- \`src/mcp_codebase_insight/core/tasks.py\`
- \`docs/features/code-analysis.md\`"

echo "✓ Issue 2: Advanced Pattern Detection"

# Issue 3: Performance Optimization
gh issue create \
  --repo "$REPO" \
  --title "Performance Optimization for Production Release" \
  --label "enhancement" \
  --body "## Description
Optimize performance for production workloads and large codebases.

## Tasks
- [ ] Profile vector store operations and optimize query performance
- [ ] Implement connection pooling for Qdrant client
- [ ] Add batch processing for embedding generation
- [ ] Optimize cache hit rates with intelligent prefetching
- [ ] Implement query result pagination for large result sets
- [ ] Add request rate limiting and throttling
- [ ] Optimize memory usage for large file processing
- [ ] Add performance benchmarks and regression tests

## Context
Currently marked as 'In Progress' in README.md. Need to ensure system can handle production-scale codebases efficiently.

## Acceptance Criteria
- Vector store queries complete in <500ms for 90th percentile
- System can process codebases with 10,000+ files
- Memory usage stays under 2GB for typical workloads
- Cache hit rate >70% for repeated queries
- All operations have proper timeout handling
- Performance benchmarks show 2x improvement over current baseline

## Priority
High - Required for production release

## References
- \`src/mcp_codebase_insight/core/vector_store.py\`
- \`src/mcp_codebase_insight/core/cache.py\`
- \`docs/vector_store_best_practices.md\`"

echo "✓ Issue 3: Performance Optimization"

# Issue 4: Integration Testing Suite
gh issue create \
  --repo "$REPO" \
  --title "Complete Integration Testing Suite" \
  --label "enhancement" \
  --body "## Description
Expand integration testing to cover all critical workflows and edge cases.

## Tasks
- [ ] Add end-to-end tests for complete analysis workflows
- [ ] Test Qdrant connection failure scenarios and recovery
- [ ] Add tests for concurrent request handling
- [ ] Test cache invalidation and consistency
- [ ] Add integration tests for ADR management workflows
- [ ] Test SSE event streaming under load
- [ ] Add chaos engineering tests (network failures, timeouts)
- [ ] Create integration test documentation

## Context
Currently marked as 'In Progress' in README.md. Need comprehensive integration tests before production release.

## Acceptance Criteria
- Integration test coverage >80% for critical paths
- All failure scenarios have corresponding tests
- Tests pass consistently in CI/CD pipeline
- Test suite runs in <5 minutes
- Documentation explains how to run and extend integration tests

## Priority
High - Required for release confidence

## References
- \`tests/integration/\`
- \`tests/conftest.py\`
- \`run_tests.py\`
- \`docs/testing_guide.md\`"

echo "✓ Issue 4: Integration Testing Suite"

# Issue 5: Debugging Utilities Enhancement
gh issue create \
  --repo "$REPO" \
  --title "Enhance Debugging Utilities and Error Tracking" \
  --label "enhancement" \
  --body "## Description
Complete the debugging utilities system with comprehensive error tracking and diagnostics.

## Tasks
- [ ] Implement comprehensive error tracking system (from README planned section)
- [ ] Add structured error reporting with stack traces and context
- [ ] Create debug mode with verbose logging
- [ ] Add request tracing across components
- [ ] Implement error aggregation and pattern detection
- [ ] Add health check endpoints for all components
- [ ] Create debugging dashboard or CLI tool
- [ ] Add integration with external monitoring systems (optional)

## Context
Currently marked as 'In Progress' in README.md with comprehensive error tracking in 'Planned' section.

## Acceptance Criteria
- All errors are tracked with unique IDs and full context
- Debug mode provides actionable troubleshooting information
- Request tracing works across all async operations
- Health checks accurately reflect component status
- Error patterns are identified and reported
- Documentation includes debugging guide

## Priority
Medium - Improves operational support

## References
- \`src/mcp_codebase_insight/core/debug.py\`
- \`src/mcp_codebase_insight/core/health.py\`
- \`docs/troubleshooting/common-issues.md\`"

echo "✓ Issue 5: Debugging Utilities Enhancement"

# Issue 6: Extended API Documentation
gh issue create \
  --repo "$REPO" \
  --title "Create Extended API Documentation" \
  --label "documentation" \
  --body "## Description
Create comprehensive API documentation for all endpoints and tools.

## Tasks
- [ ] Document all MCP tools with examples
- [ ] Create OpenAPI/Swagger specification for REST endpoints
- [ ] Add interactive API documentation (Swagger UI)
- [ ] Document all configuration options and environment variables
- [ ] Create code examples for common use cases
- [ ] Add API versioning documentation
- [ ] Create SDK/client library documentation
- [ ] Add troubleshooting section for API errors

## Context
Currently in 'Planned' section of README.md. Need complete API docs before release.

## Acceptance Criteria
- All endpoints are documented with request/response examples
- OpenAPI spec is complete and validated
- Interactive documentation is accessible at /docs endpoint
- At least 10 code examples covering common scenarios
- Documentation includes rate limits, authentication, and error codes

## Priority
High - Required for user adoption

## References
- \`docs/api.md\`
- \`server.py\`
- \`docs/cookbook.md\`"

echo "✓ Issue 6: Extended API Documentation"

# Issue 7: Custom Pattern Plugins
gh issue create \
  --repo "$REPO" \
  --title "Implement Custom Pattern Plugin System" \
  --label "enhancement" \
  --body "## Description
Create a plugin system allowing users to define custom code patterns and analysis rules.

## Tasks
- [ ] Design plugin API and interface
- [ ] Implement plugin loader and registry
- [ ] Create plugin validation and sandboxing
- [ ] Add plugin configuration system
- [ ] Create example plugins (Python, JavaScript, Go patterns)
- [ ] Add plugin testing framework
- [ ] Create plugin development guide
- [ ] Implement plugin marketplace/repository support (optional)

## Context
Currently in 'Planned' section of README.md. Extensibility is key for adoption.

## Acceptance Criteria
- Plugin API is stable and well-documented
- Plugins can define custom patterns and analysis rules
- Plugin system is secure and cannot affect core stability
- At least 3 example plugins are provided
- Plugin development guide includes tutorial and best practices

## Priority
Medium - Nice to have for v1.0, critical for v2.0

## References
- \`src/mcp_codebase_insight/core/knowledge.py\`
- \`docs/features/code-analysis.md\`"

echo "✓ Issue 7: Custom Pattern Plugins"

# Issue 8: Advanced Caching Strategies
gh issue create \
  --repo "$REPO" \
  --title "Implement Advanced Caching Strategies" \
  --label "enhancement" \
  --body "## Description
Enhance caching system with advanced strategies for better performance and cache efficiency.

## Tasks
- [ ] Implement cache warming on server startup
- [ ] Add intelligent cache prefetching based on access patterns
- [ ] Implement distributed caching support (Redis integration)
- [ ] Add cache invalidation strategies (TTL, LRU, LFU)
- [ ] Implement cache analytics and reporting
- [ ] Add cache size limits and eviction policies
- [ ] Create cache performance benchmarks
- [ ] Add cache configuration hot-reloading

## Context
Currently in 'Planned' section of README.md. Better caching improves performance significantly.

## Acceptance Criteria
- Cache hit rate improves by at least 20%
- Cache warming completes in <30 seconds
- Distributed caching works with Redis
- Cache analytics provide actionable insights
- Configuration changes don't require restart

## Priority
Medium - Performance improvement

## References
- \`src/mcp_codebase_insight/core/cache.py\`
- \`docs/vector_store_best_practices.md\`"

echo "✓ Issue 8: Advanced Caching Strategies"

# Issue 9: Deployment Guides
gh issue create \
  --repo "$REPO" \
  --title "Create Comprehensive Deployment Guides" \
  --label "documentation" \
  --body "## Description
Create deployment guides for various environments and platforms.

## Tasks
- [ ] Create Docker Compose deployment guide
- [ ] Add Kubernetes deployment manifests and guide
- [ ] Create cloud platform guides (AWS, GCP, Azure)
- [ ] Add monitoring and observability setup guide
- [ ] Create backup and disaster recovery procedures
- [ ] Add scaling and load balancing guide
- [ ] Create security hardening checklist
- [ ] Add CI/CD pipeline examples

## Context
Currently in 'Planned' section of README.md. Users need clear deployment paths.

## Acceptance Criteria
- Deployment guides cover at least 4 platforms
- Each guide includes step-by-step instructions
- Example configuration files are provided
- Monitoring integration is documented
- Security best practices are included
- Troubleshooting section for common deployment issues

## Priority
High - Required for production adoption

## References
- \`Dockerfile\`
- \`docker-compose.yml\` (to be created)
- \`docs/getting-started/docker-setup.md\`"

echo "✓ Issue 9: Deployment Guides"

# Issue 10: Pre-release Testing and Bug Fixes
gh issue create \
  --repo "$REPO" \
  --title "Pre-release Testing and Bug Fixes" \
  --label "bug" \
  --body "## Description
Conduct comprehensive pre-release testing and fix any discovered bugs.

## Tasks
- [ ] Run full test suite across all supported Python versions (3.10, 3.11, 3.12, 3.13)
- [ ] Perform manual testing of all major workflows
- [ ] Test on multiple operating systems (Linux, macOS, Windows)
- [ ] Load testing with realistic codebase sizes
- [ ] Security audit of code and dependencies
- [ ] Review and update all dependencies to latest stable versions
- [ ] Fix any critical or high-priority bugs
- [ ] Create release notes and CHANGELOG

## Context
Final step before release. Need to ensure stability and quality.

## Acceptance Criteria
- All tests pass on supported platforms
- No critical or high-priority bugs remain
- Security audit passes with no high-severity issues
- Dependencies are up to date
- Release notes document all changes
- Performance meets defined benchmarks

## Priority
Critical - Release blocker

## References
- \`run_tests.py\`
- \`CHANGELOG.md\`
- \`.github/workflows/\` (CI/CD pipelines)"

echo "✓ Issue 10: Pre-release Testing"

# Issue 11: Update README to Stable Status
gh issue create \
  --repo "$REPO" \
  --title "Update README for Stable Release" \
  --label "documentation" \
  --body "## Description
Update README.md to reflect stable release status and complete feature set.

## Tasks
- [ ] Remove 'WIP' and 'Development in Progress' warnings
- [ ] Update feature status (move items from 'In Progress' to 'Completed')
- [ ] Add badges (version, build status, coverage, license)
- [ ] Update installation instructions with PyPI package info
- [ ] Add 'Features' section highlighting key capabilities
- [ ] Update examples with production-ready code
- [ ] Add 'Community' and 'Support' sections
- [ ] Include performance benchmarks
- [ ] Add screenshot or demo GIF (if applicable)

## Context
README is the first thing users see. It should reflect a stable, production-ready project.

## Acceptance Criteria
- All WIP warnings are removed
- Feature list is accurate and complete
- Installation instructions work for new users
- README includes all standard sections for OSS projects
- Documentation links are valid and up-to-date

## Priority
High - Release blocker

## References
- \`README.md\`"

echo "✓ Issue 11: Update README"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Successfully created 11 GitHub issues for release completion!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View all issues at: https://github.com/$REPO/issues"
echo ""
echo "Issue Summary:"
echo "  - 5 'In Progress' features to complete"
echo "  - 4 'Planned' features to implement"
echo "  - 2 release-blocker tasks"
echo ""
echo "Next steps:"
echo "  1. Prioritize and assign issues"
echo "  2. Create milestones for v1.0 release"
echo "  3. Set up project board for tracking"
echo ""
