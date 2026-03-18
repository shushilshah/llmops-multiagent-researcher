import os
from datetime import datetime
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from core.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

MAX_SOURCES = int(os.getenv("MAX_SOURCES_PER_QUERY", 3))

SYSTEM_PROMPT = """You are a Research Reader. Summarize the provided source content in 2-3 
sentences. Focus on the most relevant facts, statistics, and insights.
Be concise and objective. Do not add information not present in the source."""


def reader_agent(state: ResearchState) -> ResearchState:
    """Summarize each search result using Gemini."""
    print(f"\n[Reader] Summarizing {len(state['search_results'])} sources...")

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )

    # Group results by sub-task and take top MAX_SOURCES per task
    by_task = {}
    for r in state["search_results"]:
        task = r["sub_task"]
        if task not in by_task:
            by_task[task] = []
        if len(by_task[task]) < MAX_SOURCES:
            by_task[task].append(r)

    summaries = []
    sources = []

    for task, results in by_task.items():
        for i, result in enumerate(results):
            if not result["content"]:
                continue

            print(f"  Summarizing: {result['title'][:50]}...")

            try:
                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=f"Sub-task: {task}\n\nSource content:\n{result['content']}"),
                ]
                response = llm.invoke(messages)
                summary = response.content.strip()
            except Exception as e:
                print(f"  [Reader] Error: {e}")
                summary = result["content"][:300] + "..."

            summaries.append({
                "sub_task": task,
                "title": result["title"],
                "url": result["url"],
                "summary": summary,
                "score": result["score"],
            })

            if result["url"]:
                sources.append({
                    "title": result["title"],
                    "url": result["url"],
                    "sub_task": task,
                })

    print(f"[Reader] Generated {len(summaries)} summaries")

    trace_entry = {
        "agent": "Reader",
        "timestamp": datetime.utcnow().isoformat(),
        "input": f"{len(state['search_results'])} raw results",
        "output": f"{len(summaries)} summaries generated",
        "message": f"Summarized {len(summaries)} sources using Gemini",
    }

    return {
        **state,
        "summaries": summaries,
        "sources": sources,
        "current_agent": "critic",
        "trace": [trace_entry],
    }