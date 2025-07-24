# WhatsApp MCP Docker Services Documentation

This document provides detailed information about each Docker service in the WhatsApp MCP (Model Context Protocol) application stack.

## Overview

The WhatsApp MCP application consists of three main services that work together to provide WhatsApp functionality:

1. **WhatsApp Bridge Service** (Go) - Core WhatsApp protocol handler
2. **MCP Server** (Python) - Model Context Protocol interface
3. **API Server** (Python) - REST API wrapper

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Server    │    │   MCP Server    │    │ WhatsApp Bridge │
│   (Python)      │    │   (Python)      │    │     (Go)        │
│   Port: 8000    │    │   Port: 4200    │    │   Port: 8080    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌─────────────────┐
                        │   WhatsApp      │
                        │   Protocol      │
                        └─────────────────┘
```

---

## 🌉 WhatsApp Bridge Service

### **Purpose**
The core service that handles WhatsApp protocol communication using the `whatsmeow` Go library. It acts as a bridge between the application and WhatsApp's servers.

### **Service Details**
- **Language**: Go 1.24
- **Port**: `8080`
- **Container Name**: `whatsapp-bridge`
- **Base Image**: `alpine:latest`
- **Build Context**: Root directory with `./Dockerfiles/bridge`

### **Key Features**
- Direct WhatsApp protocol implementation using `whatsmeow`
- Message sending and receiving
- Media download capabilities
- SQLite database for message storage
- QR code authentication for WhatsApp Web
- Health check endpoint at `/health`

### **Endpoints**
- `GET /health` - Health check endpoint
- `POST /api/send` - Send text or media messages
- `POST /api/download` - Download media by message ID and chat JID

### **Environment Variables**
- `CGO_ENABLED=1` - Required for SQLite support

### **Volumes**
- `./data/store:/app/store` - Database storage (messages.db, whatsapp.db)
- `./data/media:/app/media` - Media files storage

### **Dependencies**
- SQLite3 for data persistence
- curl for health checks
- WhatsApp session data for authentication

### **Health Check**
- **Command**: `curl -f http://localhost:8080/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

---

## 🐍 MCP Server (Python)

### **Purpose**
Implements the Model Context Protocol (MCP) interface, providing structured tools for AI agents to interact with WhatsApp functionality.

### **Service Details**
- **Language**: Python 3.11
- **Port**: `4200`
- **Container Name**: `mcp-server`
- **Base Image**: `python:3.11-slim`
- **Build Context**: Root directory with `./Dockerfiles/mcp`

### **Key Features**
- FastMCP framework implementation
- Audio processing with FFmpeg
- Message search and filtering
- Contact management
- Chat operations
- Media handling (including audio conversion)

### **MCP Tools Available**
- `search_contacts` - Search WhatsApp contacts
- `list_messages` - List messages with filtering
- `list_chats` - List available chats
- `get_chat` - Get specific chat information
- `get_direct_chat_by_contact` - Find direct chat by phone number
- `get_contact_chats` - Get all chats for a contact
- `get_last_interaction` - Get last interaction with contact
- `get_message_context` - Get context around specific messages
- `send_message` - Send text messages
- `send_file` - Send media files
- `send_audio_message` - Send audio messages (with conversion)
- `download_media` - Download media files

### **Environment Variables**
- `WHATSAPP_API_BASE_URL=http://whatsapp-bridge:8080/api` - Bridge service URL
- `MESSAGES_DB_PATH=/app/data/store/messages.db` - Database path

### **Volumes**
- `./data:/app/data` - Data directory for databases and media

### **Dependencies**
- **whatsapp-bridge**: Must be healthy before starting
- FFmpeg for audio processing
- UV package manager for Python dependencies

### **Health Check**
- **Command**: `curl -f http://localhost:4200/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 5 seconds
- **Retries**: 3

---

## 🚀 API Server (Python)

### **Purpose**
Provides a REST API wrapper around the MCP tools, enabling HTTP-based access to WhatsApp functionality with API key authentication.

### **Service Details**
- **Language**: Python 3.11
- **Port**: `8000`
- **Container Name**: `api-server`
- **Base Image**: `python:3.11-slim`
- **Build Context**: Root directory with `./Dockerfiles/api`

### **Key Features**
- FastAPI framework
- API key authentication via `X-API-Key` header
- OpenAPI/Swagger documentation
- RESTful endpoints for all MCP tools
- Dynamic loading of MCP server functionality

### **API Endpoints**
All endpoints require `X-API-Key` header for authentication:

- `GET /search_contacts` - Search contacts
- `GET /list_messages` - List messages
- `GET /list_chats` - List chats
- `GET /get_chat` - Get specific chat
- `GET /get_direct_chat_by_contact` - Get direct chat by contact
- `GET /get_contact_chats` - Get contact chats
- `GET /get_last_interaction` - Get last interaction
- `GET /get_message_context` - Get message context
- `POST /send_message` - Send text message
- `POST /send_file` - Send file
- `POST /send_audio_message` - Send audio message
- `POST /download_media` - Download media

### **Environment Variables**
- `WHATSAPP_API_BASE_URL=http://whatsapp-bridge:8080/api` - Bridge service URL
- `API_KEY=${API_KEY:-mysecretkey}` - API authentication key (default: "mysecretkey")

### **Authentication**
- **Method**: API Key via header
- **Header**: `X-API-Key`
- **Default Key**: `mysecretkey`
- **Override**: Set `API_KEY` environment variable

### **Dependencies**
- **whatsapp-bridge**: Must be healthy before starting
- UV package manager for Python dependencies

### **Health Check**
- **Command**: `curl -f http://localhost:8000/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 5 seconds
- **Retries**: 3

---

## 🔧 Networking

### **Internal Network**
- **Name**: `whatsapp-network`
- **Driver**: `bridge`
- **Purpose**: Internal communication between services

### **Service Communication**
- **API Server** → **WhatsApp Bridge**: HTTP calls to `whatsapp-bridge:8080`
- **MCP Server** → **WhatsApp Bridge**: HTTP calls to `whatsapp-bridge:8080`
- All services can communicate internally via service names

### **External Access**
- **WhatsApp Bridge**: Not exposed externally (internal only)
- **MCP Server**: Port `4200` (if needed for direct MCP protocol access)
- **API Server**: Port `8000` (primary external interface)

---

## 📁 Data Persistence

### **Volumes**
- `./data/store/` - SQLite databases
  - `messages.db` - Message history and metadata
  - `whatsapp.db` - WhatsApp session and contact data
- `./data/media/` - Downloaded media files
- `whatsapp-data` - Named volume for additional data

### **Database Structure**
- **WhatsApp Bridge**: Manages WhatsApp protocol data
- **MCP/API Servers**: Read-only access to message database

---

## 🚦 Service Startup Order

1. **WhatsApp Bridge** starts first
2. Health check ensures bridge is ready
3. **MCP Server** starts after bridge is healthy
4. **API Server** starts after bridge is healthy

---

## 🔍 Monitoring & Health

### **Health Check Endpoints**
- Bridge: `http://whatsapp-bridge:8080/health`
- MCP: `http://mcp-server:4200/health`
- API: `http://api-server:8000/health`

### **Logs**
- All services use Docker logging
- Access logs: `docker-compose logs [service-name]`

---

## 🛠️ Development & Deployment

### **Override Configuration**
Use `docker-compose.override.yml` for:
- Custom environment variables
- Additional networks
- Development-specific configurations
- Port mappings

### **Environment Variables**
Set these in your environment or `.env` file:
- `API_KEY` - Custom API key for authentication
- Additional service-specific variables as needed

### **Commands**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs <service-name>

# Stop services
docker-compose down

# Restart single service
docker-compose restart <service-name>
```

---

## 🔐 Security Notes

- **API Key**: Change default API key in production
- **Network**: Use external networks for production isolation
- **Files**: Ensure proper file permissions for mounted volumes
- **WhatsApp**: QR code authentication required on first run
