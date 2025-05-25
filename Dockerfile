# Multi-stage build for Go and Python applications

# Stage 1: Python application with UV
FROM python:3.11-slim AS python-base
# Install UV
RUN pip install uv
WORKDIR /app/whatsapp-mcp-server
COPY whatsapp-mcp-server/ .
RUN uv sync

# Stage 2: Final runtime image
FROM python:3.11-slim
# Install Go 1.23, build tools for CGO, and ffmpeg for audio conversion
RUN apt-get update && apt-get install -y \
    wget \
    ffmpeg \
    gcc \
    libc6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Go 1.23 manually
RUN wget -O go.tar.gz https://go.dev/dl/go1.23.4.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go.tar.gz \
    && rm go.tar.gz

# Add Go to PATH and enable CGO
ENV PATH=/usr/local/go/bin:$PATH
ENV GOPATH=/go
ENV GOBIN=/go/bin
ENV CGO_ENABLED=1

# Install UV in final image
RUN pip install uv

# Create app directories
WORKDIR /app
COPY whatsapp-bridge/ /app/whatsapp-bridge/
COPY --from=python-base /app/whatsapp-mcp-server /app/whatsapp-mcp-server

# Create shared store directory for databases
RUN mkdir -p /app/whatsapp-bridge/store

# Download Go dependencies
WORKDIR /app/whatsapp-bridge
RUN go mod download

# Set environment variables
ENV PYTHONPATH=/app/whatsapp-mcp-server
ENV WHATSAPP_BRIDGE_PATH=/app/whatsapp-bridge

# Expose ports
EXPOSE 8080 8000

# Create startup script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
