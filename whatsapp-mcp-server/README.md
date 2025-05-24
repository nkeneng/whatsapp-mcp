# WhatsApp MCP API

This project provides a FastAPI server wrapping the WhatsApp MCP tools from `whatsapp-mcp-server`.

## Features

- Exposes WhatsApp MCP methods via HTTP endpoints
- Simple API key authentication using `X-API-Key` header
- Generates `openapi.yaml` spec on startup

## Requirements

- Python 3.9+
- Dependencies specified in `requirements.txt`

## Setup

```bash
# Navigate to the API folder
cd whatsapp-mcp-api

# (Optional) Create venv and activate
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key (default: "mysecretkey")
export API_KEY=mysecretkey

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `openapi.yaml` file will be generated in this folder when the server starts.

## Usage

Include the header `X-API-Key: <your_api_key>` in all requests.

Example:
```
curl -H "X-API-Key: mysecretkey" "http://localhost:8000/search_contacts?query=John"
```
