
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parent.parent

# Load the main project's .env before importing ai_engine
load_dotenv(ROOT_DIR / ".env", override=True)

sys.path.insert(0, str(ROOT_DIR))

from ai_engine import generate_story

app = FastAPI(title="StoryLearn AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StoryRequest(BaseModel):
    topic: str

@app.get("/")
def home():
    return {"message": "StoryLearn AI API is running!"}

@app.post("/api/generate-story")
def create_story(request: StoryRequest):
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    try:
        result = generate_story(topic)
        return {"topic": topic, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

