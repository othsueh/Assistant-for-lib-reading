from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from codebase_assistant import CodeAssistant, load_system_prompt
import os
import asyncio
import json

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Add both localhost variations
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Be more specific about allowed methods
    allow_headers=["Content-Type", "Accept", "Authorization"],  # Be more specific about allowed headers
    expose_headers=["Content-Type"]  # Expose specific headers to the frontend
)

# Directory for storing dialog histories
DIALOGS_DIR = "chat_history"
os.makedirs(DIALOGS_DIR, exist_ok=True)

# Initialize assistant (do this at startup)
assistant = CodeAssistant(
    json_path="project_structure.json",
    markdown_dir="../ellama_codebase/",
    model="claude-3-sonnet-20240229",
    load_faiss_from="project_faiss"
)

# save faiss index
if not os.path.exists("project_faiss"):
    assistant.save_faiss("project_faiss")

# Load system prompt
system_prompt = load_system_prompt()

# Load existing dialogs
def load_dialogs():
    for filename in os.listdir(DIALOGS_DIR):
        if filename.endswith('.json'):
            dialog_id = filename[:-5]  # Remove .json extension
            with open(os.path.join(DIALOGS_DIR, filename), 'r') as f:
                assistant.dialogs[dialog_id] = json.load(f)

# Save dialog to file
def save_dialog(dialog_id: str, messages: list):
    with open(os.path.join(DIALOGS_DIR, f"{dialog_id}.json"), 'w') as f:
        json.dump(messages, f)

load_dialogs()

# Request models
class ChatRequest(BaseModel):
    message: str
    dialog_id: str = "default"  # Optional dialog ID for multiple conversations

class DialogRequest(BaseModel):
    name: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = assistant.chat(request.message, system_prompt, request.dialog_id)
        # Save dialog after each message
        save_dialog(request.dialog_id, assistant.dialogs[request.dialog_id])
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    try:
        full_response = ""
        
        async def generate():
            nonlocal full_response  # Access the outer variable
            async for chunk in assistant.chat_stream(request.message, system_prompt, request.dialog_id):
                if chunk:
                    full_response += chunk  # Accumulate the response
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Save dialog after streaming is complete
            assistant.dialogs[request.dialog_id].extend([
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": full_response}
            ])
            save_dialog(request.dialog_id, assistant.dialogs[request.dialog_id])
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        print(f"Streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dialogs")
async def get_dialogs():
    """Get list of all dialogs"""
    return {
        "dialogs": [
            {
                "id": dialog_id,
                "messages": messages
            }
            for dialog_id, messages in assistant.dialogs.items()
        ]
    }

@app.post("/api/dialogs/new")
async def create_dialog(request: DialogRequest):
    """Create a new dialog"""
    print(f"Received request to create dialog: {request.name}")  # Debug print
    dialog_id = request.name.lower().replace(" ", "_")
    print(f"Generated dialog_id: {dialog_id}")  # Debug print
    if dialog_id not in assistant.dialogs:
        assistant.dialogs[dialog_id] = []
        save_dialog(dialog_id, [])
        print(f"Created new dialog: {dialog_id}")  # Debug print
        return {
            "status": "success",
            "dialog_id": dialog_id,
            "message": f"Created new dialog: {dialog_id}"
        }
    else:
        print(f"Dialog {dialog_id} already exists")  # Debug print
        raise HTTPException(status_code=400, detail="Dialog already exists")
