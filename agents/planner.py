import os
import json
from datetime import datetime
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from core.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a Research Planner. Your job is to break down a complec research question
into 3-5 specific, searchanle sub-tasks.

Each sub-task should:
- Be a specific search query (not a broad topic)
- Cover a different angle of the main question
- Be concise (under 10 words)

Respond ONLY with a JSON array to strings. No explanation, no markdown, no backticks.
Example: ["query one", "query two", "query three"]
"""


def planner_agent(state: ResearchState) -> ResearchState:
    """Break the research question into a specific sub-tasks."""
    print(f"\n[Planner] Analyzing question: {state['question']}")

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Research question: {state['question']}"),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # clean up any markdown artifacts
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        sub_tasks = json.loads(raw)
        if not isinstance(sub_tasks, list):
            raise ValueError("Expected a list")
        sub_taks = [str(t) for t in sub_tasks[:5]]

    except Exception as e:
        print(f"[Planner] JSON parse error: {e}. Using fallback.")
        sub_tasks = [
            state['question'],
            f"{state['question']} latest research",
            f"{state['question']} key findings",
        ]

    print(f"[Planner] Created {len(sub_tasks)} sub_tasks:")
    for i,t in enumerate(sub_tasks):
        print(f"  {i+1}. {t}")

    trace_entry = {
        "agent": "Planner",
        "timestamp": datetime.utcnow().isoformat(),
        "input": state["question"],
        "output": sub_tasks,
        "message": f"Broke question into {len(sub_tasks)} sub_tasks",
    }

    return {
        **state,
        "sub_tasks": sub_tasks,
        "current_agent": "searcher",
        "trace": [trace_entry],
    }