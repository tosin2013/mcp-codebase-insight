# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (needed for pydantic)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY scripts/ scripts/

# Copy configuration files
COPY .env.example .env

# Create necessary directories
RUN mkdir -p \
    docs/adrs \
    knowledge \
    cache \
    logs

# Set permissions
RUN chmod +x scripts/start_mcp_server.sh

# Expose port
EXPOSE 3000

# Set entrypoint
ENTRYPOINT ["scripts/start_mcp_server.sh"]

# Set default command
CMD ["--host", "0.0.0.0", "--port", "3000"]
