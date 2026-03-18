import os
from datetime import datetime
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from core.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a Research Writer. Synthesize the collected research into a 
comprehensive, well-structured report.

Format the report in Markdown with:
- ## Executive Summary (2-3 sentences)
- ## Key Findings (bullet points with the most important insights)
- ## Detailed Analysis (3-4 paragraphs covering different aspects)
- ## Conclusions (what this means, practical implications)

Write in a clear, professional tone. Cite sources inline as [Source Title].
Base your report ONLY on the provided research summaries."""


def writer_agent(state: ResearchState) -> ResearchState:
    """Synthesize all research into a final structured report."""
    print(f"\n[Writer] Generating final report...")

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.4,
        max_tokens=1700,
    )

    summaries_text = "\n\n".join([
        f"[{s['title']}]: {s['summary']}"
        for s in state["summaries"]
    ])

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Research Question: {state['question']}

Research Quality Score: {state['quality_score']}/10
Critic Notes: {state['critique']}

Research Summaries:
{summaries_text}"""),
    ]

    response = llm.invoke(messages)
    final_report = response.content.strip()

    # Append sources section
    if state["sources"]:
        sources_md = "\n\n## Sources\n"
        for i, src in enumerate(state["sources"]):
            if src["url"]:
                sources_md += f"{i+1}. [{src['title']}]({src['url']})\n"
        final_report += sources_md

    print(f"[Writer] Report generated ({len(final_report)} characters)")

    trace_entry = {
        "agent": "Writer",
        "timestamp": datetime.utcnow().isoformat(),
        "input": f"{len(state['summaries'])} summaries + critique",
        "output": f"Report: {len(final_report)} characters",
        "message": "Final research report generated successfully",
    }

    return {
        **state,
        "final_report": final_report,
        "current_agent": "complete",
        "trace": [trace_entry],
    }