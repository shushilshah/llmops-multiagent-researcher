import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.orchestrator import run_research
from core.memory import get_recent_sessions, load_session, save_feedback

app = FastAPI(
    title="Multi-Agent Research Assistant API",
    description="AI-powered research using autonomous agents — Planner, Searcher, Reader, Critic, Writer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    question: str
    session_id: str = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    comment: str = ""


@app.get("/")
def root():
    return {
        "message": "Multi-Agent Research Assistant API",
        "docs": "/docs",
        "endpoints": ["/research", "/sessions", "/session/{id}", "/feedback"],
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/research")
def research(request: ResearchRequest):
    """Run the full multi-agent research pipeline."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    session_id = request.session_id or str(uuid.uuid4())

    try:
        result = run_research(request.question, session_id)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "session_id": session_id,
            "question": request.question,
            "final_report": result["final_report"],
            "sources": result["sources"],
            "quality_score": result["quality_score"],
            "critique": result["critique"],
            "sub_tasks": result["sub_tasks"],
            "trace": result["trace"],
            "total_sources": len(result["sources"]),
            "agent_steps": len(result["trace"]),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
def get_sessions():
    """Get recent research sessions."""
    try:
        sessions = get_recent_sessions(limit=20)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Get a specific research session."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/feedback")
def feedback(request: FeedbackRequest):
    """Save user feedback for a session."""
    try:
        save_feedback(request.session_id, request.rating, request.comment)
        return {"status": "feedback saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))