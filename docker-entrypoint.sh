#!/bin/bash

# Start WhatsApp bridge in background
cd /app/whatsapp-bridge
echo "Starting WhatsApp Bridge..."
go run main.go &
BRIDGE_PID=$!

# Wait a moment for the bridge to start
sleep 5

# Start MCP server
cd /app/whatsapp-mcp-server
echo "Starting MCP Server..."
uv run api.py &
MCP_PID=$!

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    kill $BRIDGE_PID $MCP_PID
    exit 0
}

# Trap SIGTERM and SIGINT
trap shutdown SIGTERM SIGINT

# Wait for either process to exit
wait $BRIDGE_PID $MCP_PID
