# VectorStore Best Practices

This document outlines best practices for working with the VectorStore component in the MCP Codebase Insight project.

## Metadata Structure

To ensure consistency and prevent `KeyError` exceptions, always follow these metadata structure guidelines:

### Required Fields

Always include these fields in your metadata when adding vectors:

- `type`: The type of content (e.g., "code", "documentation", "pattern")
- `language`: Programming language if applicable (e.g., "python", "javascript")
- `title`: Short descriptive title
- `description`: Longer description of the content

### Accessing Metadata

Always use the `.get()` method with a default value when accessing metadata fields:

```python
# Good - safe access pattern
result.metadata.get("type", "code")

# Bad - can cause KeyError
result.metadata["type"]
```

## Initialization and Cleanup

Follow these best practices for proper initialization and cleanup:

1. Always `await vector_store.initialize()` before using a VectorStore
2. Always `await vector_store.cleanup()` in test teardown/finally blocks
3. Use unique collection names in tests to prevent conflicts
4. Check `vector_store.initialized` status before operations

Example:

```python
try:
    store = VectorStore(url, embedder, collection_name=unique_name)
    await store.initialize()
    # Use the store...
finally:
    await store.cleanup()
    await store.close()
```

## Vector Names and Dimensions

- Use consistent vector dimensions (384 for all-MiniLM-L6-v2)
- Be careful when overriding the vector_name parameter
- Ensure embedder and vector store are compatible

## Error Handling

- Check for component availability before use
- Handle initialization errors gracefully
- Log failures with meaningful messages

## Testing Guidelines

1. Use isolated test collections with unique names
2. Clean up all test data after tests
3. Verify metadata structure in tests
4. Use standardized test data fixtures
5. Test both positive and negative paths

By following these guidelines, you can avoid common issues like the "KeyError: 'type'" problem that was occurring in the codebase. 