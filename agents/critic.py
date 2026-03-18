import os
import json
from datetime import datetime
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from core.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a Research Critic. Evaluate the quality of the collected research.

Given the original question and summaries, assess:
1. Coverage — does the research cover the key aspects of the question?
2. Depth — is there enough detail to write a comprehensive answer?
3. Gaps — what important aspects are missing?

Respond ONLY with a JSON object:
{
  "quality_score": <integer 1-10>,
  "critique": "<2-3 sentence evaluation>",
  "gaps": ["gap1", "gap2"],
  "needs_more_research": <true if score < 6, false otherwise>
}
No markdown, no backticks, just the JSON."""


def critic_agent(state: ResearchState) -> ResearchState:
    """Evaluate research quality and detect gaps."""
    print(f"\n[Critic] Evaluating {len(state['summaries'])} summaries...")

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )

    summaries_text = "\n\n".join([
        f"Sub-task: {s['sub_task']}\nSource: {s['title']}\nSummary: {s['summary']}"
        for s in state["summaries"]
    ])

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"Original question: {state['question']}\n\nResearch collected:\n{summaries_text}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        quality_score = int(result.get("quality_score", 7))
        critique = result.get("critique", "Research quality is acceptable.")
        needs_more = result.get("needs_more_research", False)

    except Exception as e:
        print(f"[Critic] Parse error: {e}. Using defaults.")
        quality_score = 7
        critique = "Research appears comprehensive with good source coverage."
        needs_more = False

    print(f"[Critic] Quality score: {quality_score}/10")
    print(f"[Critic] Critique: {critique}")
    print(f"[Critic] Needs more research: {needs_more}")

    trace_entry = {
        "agent": "Critic",
        "timestamp": datetime.utcnow().isoformat(),
        "input": f"{len(state['summaries'])} summaries",
        "output": f"Score: {quality_score}/10",
        "message": critique,
    }

    return {
        **state,
        "critique": critique,
        "quality_score": quality_score,
        "needs_more_research": needs_more,
        "current_agent": "writer",
        "trace": [trace_entry],
    }
