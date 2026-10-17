import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import settings, BASE_DIR
from app.tools import TOOLS_METADATA
from app.tools.notes import (
    create_or_update_note,
    read_note,
    delete_note,
    _sanitize_filename,
)
from app.agent.core import AgentRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agent.main")

app = FastAPI(title="Aniruddh Web Agent", version="1.0.0")

# Request / Response Schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = 0.3

class SettingsUpdateRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None

class NoteCreateRequest(BaseModel):
    title: str
    content: str


# API Routes
@app.get("/api/status")
async def get_status():
    key = settings.get_api_key()
    masked_key = f"{key[:6]}...{key[-4:]}" if len(key) >= 12 else ("Configured" if key else "")
    return {
        "status": "online",
        "has_api_key": bool(key),
        "masked_key": masked_key,
        "model": settings.model,
        "available_models": [
            {"id": "gemini-3.8-flash", "name": "Gemini 3.8 Flash (Recommended)", "tag": "Fast & Smart"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "tag": "Ultra Fast"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "tag": "Reliable"},
        ],
        "notes_count": len(list(settings.notes_dir.glob("*.md"))),
    }

@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    if req.api_key is not None:
        settings.set_api_key(req.api_key)
    if req.model is not None:
        settings.set_model(req.model)
    return {"status": "updated", "has_api_key": bool(settings.get_api_key()), "model": settings.model}

@app.get("/api/tools")
async def get_tools():
    return {"tools": TOOLS_METADATA}

@app.get("/api/notes")
async def list_notes_api():
    notes = []
    for p in sorted(settings.notes_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        size_kb = max(1, p.stat().st_size // 1024)
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            # Get preview snippet (skip title line)
            lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
            preview = lines[0][:120] if lines else "Empty note"
        except Exception:
            preview = ""

        notes.append({
            "title": p.stem,
            "filename": p.name,
            "preview": preview,
            "size_kb": size_kb,
            "updated_at": mtime,
        })
    return {"notes": notes}

@app.get("/api/notes/{title}")
async def get_note_api(title: str):
    content = read_note(title)
    if content.startswith("Note '") and content.endswith("not found."):
        raise HTTPException(status_code=404, detail=content)
    return {"title": title, "content": content}

@app.post("/api/notes")
async def create_note_api(req: NoteCreateRequest):
    result = create_or_update_note(req.title, req.content)
    return {"status": "ok", "message": result}

@app.delete("/api/notes/{title}")
async def delete_note_api(title: str):
    result = delete_note(title)
    return {"status": "ok", "message": result}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    api_key = req.api_key or settings.get_api_key()
    model = req.model or settings.model

    messages_data = [{"role": m.role, "content": m.content} for m in req.messages]
    runner = AgentRunner(api_key=api_key, model=model)

    return StreamingResponse(
        runner.run_stream(messages=messages_data, temperature=req.temperature or 0.3),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# Static files & UI
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Aniruddh Web Agent is running. static/index.html not found."}
