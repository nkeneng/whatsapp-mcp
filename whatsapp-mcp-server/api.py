# main.py for WhatsApp MCP API server
import os
import sys
import importlib.util
from fastapi import FastAPI, HTTPException, Depends, Header
import json

# Simple API key authentication that won't appear in OpenAPI
def get_api_key(x_api_key: str = Header(..., alias="X-API-Key", include_in_schema=False)):
    API_KEY = os.getenv("API_KEY", "mysecretkey")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp MCP API",
    version="1.0.0",
    description="API wrapper over the WhatsApp MCP tools"
)

# Dynamically load MCP server module
server_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "whatsapp-mcp-server", "main.py")
)
spec = importlib.util.spec_from_file_location("server_main", server_path)
server_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_main)

# API endpoints exposing MCP tools
@app.get("/search_contacts")
def search_contacts(query: str, _: str = Depends(get_api_key)):
    return server_main.search_contacts(query)

@app.get("/list_messages")
def list_messages(
    after: str = None,
    before: str = None,
    sender_phone_number: str = None,
    chat_jid: str = None,
    query: str = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1,
    _: str = Depends(get_api_key)
):
    return server_main.list_messages(
        after, before, sender_phone_number, chat_jid, query,
        limit, page, include_context, context_before, context_after
    )

@app.get("/list_chats")
def list_chats(
    query: str = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active",
    _: str = Depends(get_api_key)
):
    return server_main.list_chats(query, limit, page, include_last_message, sort_by)

@app.get("/get_chat")
def get_chat(chat_jid: str, include_last_message: bool = True, _: str = Depends(get_api_key)):
    return server_main.get_chat(chat_jid, include_last_message)

@app.get("/get_direct_chat_by_contact")
def get_direct_chat_by_contact(sender_phone_number: str, _: str = Depends(get_api_key)):
    return server_main.get_direct_chat_by_contact(sender_phone_number)

@app.get("/get_contact_chats")
def get_contact_chats(jid: str, limit: int = 20, page: int = 0, _: str = Depends(get_api_key)):
    return server_main.get_contact_chats(jid, limit, page)

@app.get("/get_last_interaction")
def get_last_interaction(jid: str, _: str = Depends(get_api_key)):
    return server_main.get_last_interaction(jid)

@app.get("/get_message_context")
def get_message_context(message_id: str, before: int = 5, after: int = 5, _: str = Depends(get_api_key)):
    return server_main.get_message_context(message_id, before, after)

@app.post("/send_message")
def send_message(recipient: str, message: str, _: str = Depends(get_api_key)):
    return server_main.send_message(recipient, message)

@app.post("/send_file")
def send_file(recipient: str, media_path: str, _: str = Depends(get_api_key)):
    return server_main.send_file(recipient, media_path)

@app.post("/send_audio_message")
def send_audio_message(recipient: str, media_path: str, _: str = Depends(get_api_key)):
    return server_main.send_audio_message(recipient, media_path)

@app.post("/download_media")
def download_media(message_id: str, chat_jid: str, _: str = Depends(get_api_key)):
    return server_main.download_media(message_id, chat_jid)

# Generate OpenAPI specification on startup
@app.on_event("startup")
def generate_openapi():
    spec = app.openapi()
    openapi_path = os.path.join(os.path.dirname(__file__), "openapi.json")
    with open(openapi_path, "w") as f:
        json.dump(spec, f, indent=2)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)