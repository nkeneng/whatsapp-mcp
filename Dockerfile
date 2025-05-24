# Stage 1: Python application with UV
FROM python:3.11-slim AS python-base
# Install UV
RUN pip install uv
WORKDIR /app/whatsapp-mcp-server
COPY whatsapp-mcp-server/ .
RUN uv sync

# Stage 2: Final runtime image
FROM python:3.11-slim
# Install Go runtime and ffmpeg for audio conversion
RUN apt-get update && apt-get install -y \
    golang-go \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

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
