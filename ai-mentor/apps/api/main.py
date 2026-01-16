"""
main.py - FastAPI Entry Point for AI Life Coach Brain

Endpoints:
- GET  /health            - Health check
- POST /chat              - Send a message to the AI mentor
- GET  /onboarding/questions  - Get diagnostic questions
- POST /onboarding/submit     - Submit onboarding answers
- POST /journal/entry         - Log awareness journal entry
"""

import os
import json
from typing import Optional, List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from brain import run_agent
from onboarding import (
    DRIVER_QUESTIONS, 
    SCRIPT_PATTERN_QUESTIONS,
    OnboardingSubmission,
    process_onboarding,
    DiagnosisResult
)

load_dotenv()

# --- App Setup ---
app = FastAPI(
    title="AI Life Coach Brain",
    version="3.0.0",
    description="Pavel Bilskiy Methodology - Stateful AI Mentor with Diagnostic Onboarding"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---
class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    user_id: str


class JournalEntry(BaseModel):
    user_id: str
    event_description: str
    negative_interpretation: Optional[str] = None
    healthy_interpretation: Optional[str] = None
    emotion_before: Optional[str] = None
    emotion_after: Optional[str] = None


# --- Endpoints ---
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Life Coach Brain",
        "version": "3.0.0",
        "methodology": "Pavel Bilskiy (SelfMade Man)"
    }


# === ONBOARDING ENDPOINTS ===
@app.get("/onboarding/questions")
def get_onboarding_questions():
    """Get all diagnostic questions for the 'Mirror' onboarding."""
    return {
        "driver_questions": DRIVER_QUESTIONS,
        "script_questions": SCRIPT_PATTERN_QUESTIONS,
        "total_questions": len(DRIVER_QUESTIONS) + len(SCRIPT_PATTERN_QUESTIONS)
    }


@app.post("/onboarding/submit", response_model=DiagnosisResult)
async def submit_onboarding(submission: OnboardingSubmission):
    """
    Process onboarding answers and create user diagnosis.
    Returns the user's Driver, Script Pattern, and Core Wound.
    """
    try:
        result = process_onboarding(submission)
        
        # TODO: Save to Supabase profiles table
        # supabase.rpc("update_diagnosis", {...})
        
        print(f"[ONBOARDING] User {submission.user_id}: Driver={result.driver}, Pattern={result.script_pattern}")
        
        return result
    
    except Exception as e:
        print(f"[ERROR] Onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === CHAT ENDPOINT ===
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main chat endpoint.
    Sends user message through the LangGraph agent workflow.
    The agent uses the user's diagnosis to personalize responses.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if not req.user_id.strip():
        raise HTTPException(status_code=400, detail="User ID is required")
    
    try:
        response = run_agent(
            user_id=req.user_id,
            message=req.message
        )
        
        return ChatResponse(
            response=response,
            user_id=req.user_id
        )
    
    except Exception as e:
        print(f"[ERROR] Chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


# === AWARENESS JOURNAL ENDPOINTS ===
@app.post("/journal/entry")
async def log_journal_entry(entry: JournalEntry):
    """
    Log an awareness journal entry.
    The AI can help transform negative interpretations to healthy ones.
    """
    try:
        # If no healthy interpretation provided, ask AI to generate one
        if entry.negative_interpretation and not entry.healthy_interpretation:
            prompt = f"""The user experienced: {entry.event_description}
Their negative interpretation was: {entry.negative_interpretation}

Generate a healthy reframe of this situation (2-3 sentences). 
Use Pavel Bilskiy's methodology: Focus on self-acceptance, not blame."""
            
            healthy_response = run_agent(
                user_id=entry.user_id,
                message=prompt
            )
            entry.healthy_interpretation = healthy_response
        
        # TODO: Save to Supabase awareness_journal table
        
        return {
            "status": "logged",
            "event": entry.event_description,
            "negative": entry.negative_interpretation,
            "healthy": entry.healthy_interpretation
        }
    
    except Exception as e:
        print(f"[ERROR] Journal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/journal/prompts")
def get_journal_prompts():
    """Get evening reflection prompts for the awareness journal."""
    return {
        "prompts": [
            "What happened today that triggered a negative emotion?",
            "What did you say to yourself about it?",
            "Was that thought 100% true, or could there be another interpretation?",
            "What would you tell a friend in the same situation?"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
