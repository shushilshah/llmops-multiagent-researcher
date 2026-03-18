import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "research_assistant")

def get_db():
    """Get MongoDB database connection with fallback."""
    from pymongo import MongoClient
    client = MongoClient(
        os.getenv("MONGODB_URI"),
        tlsCAFile=certifi.where(),   # ✅ ONLY THIS
        serverSelectionTimeoutMS=10000
)
    return client[MONGODB_DB]
 
 
def save_session(session_id: str, question: str, state: dict) -> None:
    """Save a research session to MongoDB. Fails silently if unavailable."""
    if not MONGODB_URI:
        print("[Memory] No MONGODB_URI set, skipping save")
        return
    try:
        db = get_db()
        db.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "session_id": session_id,
                    "question": question,
                    "sub_tasks": state.get("sub_tasks", []),
                    "summaries": state.get("summaries", []),
                    "critique": state.get("critique", ""),
                    "quality_score": state.get("quality_score", 0),
                    "final_report": state.get("final_report", ""),
                    "sources": state.get("sources", []),
                    "trace": state.get("trace", []),
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        print(f"[Memory] Session {session_id} saved to MongoDB")
    except Exception as e:
        print(f"[Memory] MongoDB save failed (non-critical): {e}")
 
 
def load_session(session_id: str) -> dict | None:
    """Load a research session from MongoDB."""
    if not MONGODB_URI:
        return None
    try:
        db = get_db()
        session = db.sessions.find_one({"session_id": session_id}, {"_id": 0})
        return session
    except Exception as e:
        print(f"[Memory] MongoDB load failed: {e}")
        return None
 
 
def get_recent_sessions(limit: int = 10) -> list:
    """Get most recent research sessions."""
    if not MONGODB_URI:
        return []
    try:
        db = get_db()
        sessions = list(
            db.sessions.find(
                {},
                {"session_id": 1, "question": 1, "quality_score": 1, "updated_at": 1, "_id": 0}
            ).sort("updated_at", -1).limit(limit)
        )
        return sessions
    except Exception as e:
        print(f"[Memory] MongoDB query failed: {e}")
        return []
 
 
def save_feedback(session_id: str, rating: int, comment: str = "") -> None:
    """Save user feedback for a session."""
    if not MONGODB_URI:
        return
    try:
        db = get_db()
        db.feedback.insert_one({
            "session_id": session_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.utcnow(),
        })
        print(f"[Memory] Feedback saved for session {session_id}")
    except Exception as e:
        print(f"[Memory] Feedback save failed: {e}")
 