# ADR 001: Use Docker for Qdrant Deployment

## Status

Accepted

## Context

We need to run Qdrant as our vector database for storing and searching embeddings. Initially, we considered using Homebrew for installation on macOS, but there are several factors to consider:

1. **Cross-platform compatibility**: While Homebrew works well on macOS, it's not available on other platforms.
2. **Isolation**: Running Qdrant directly on the host system can lead to potential conflicts with other services.
3. **Version management**: Docker makes it easier to manage and upgrade Qdrant versions.
4. **Data persistence**: We need a reliable way to persist vector data across restarts.
5. **Resource management**: Docker provides better control over resource allocation and limits.

## Decision

We will use Docker to run Qdrant instead of installing it directly on the host system. Specifically:

1. Run Qdrant using the official Docker image (`qdrant/qdrant:latest`)
2. Map ports 6333 (REST API) and 6334 (gRPC) to the host system
3. Use a Docker volume to persist data in the `qdrant_storage` directory
4. Configure consistent volume mounting for macOS performance

The Docker run command will be:
```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:consistent \
  qdrant/qdrant:latest
```

## Consequences

### Positive

1. **Portability**: The solution works consistently across different operating systems
2. **Isolation**: Qdrant runs in its own container without affecting the host system
3. **Easy updates**: Simple to upgrade Qdrant by pulling new Docker images
4. **Data persistence**: Vector data is safely stored in a mounted volume
5. **Resource control**: Better management of CPU, memory, and storage resources
6. **Development/Production parity**: Same deployment method can be used in all environments

### Negative

1. **Dependencies**: Requires Docker to be installed and running
2. **Resource overhead**: Docker adds some overhead compared to native installation
3. **Learning curve**: Team members need basic Docker knowledge
4. **Storage management**: Need to handle Docker volume backups and cleanup

### Neutral

1. **Configuration**: Environment variables and connection settings remain the same
2. **Performance**: No significant impact on query performance
3. **Monitoring**: Can use both Docker and Qdrant's native monitoring tools

## Implementation Notes

1. Update installation script to check for Docker instead of Homebrew
2. Add Docker-related files to .gitignore (qdrant_storage/)
3. Document Docker commands in README.md
4. Consider adding Docker Compose for multi-container setups in the future

## References

- [Qdrant Docker Documentation](https://qdrant.tech/documentation/guides/installation/#docker)
- [Docker Volume Performance](https://docs.docker.com/storage/volumes/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
