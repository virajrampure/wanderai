"""FastAPI server: run with  uvicorn app.main:app --reload"""
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .rag import KnowledgeBase
from .planner import plan_trip
from .chat import chat

app = FastAPI(title="WanderAI", description="AI agent for tourism guide and trip planning")
kb = KnowledgeBase()
STATIC = Path(__file__).resolve().parent.parent / "static"


class PlanRequest(BaseModel):
    destination: str
    days: int = Field(3, ge=1, le=10)
    budget: int = Field(20000, ge=500)
    travelers: int = Field(1, ge=1, le=20)
    interests: List[str] = []


class ChatRequest(BaseModel):
    question: str
    destination: Optional[str] = None


@app.get("/api/destinations")
def destinations():
    return {"destinations": kb.destinations(), "categories": sorted({a["category"] for d in kb.data.values() for a in d["attractions"]})}


@app.post("/api/plan")
def plan(req: PlanRequest):
    try:
        return plan_trip(kb, req.destination, req.days, req.budget, req.travelers, req.interests)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    return chat(kb, req.question, req.destination)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
