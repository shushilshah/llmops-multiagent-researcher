import uuid
from langgraph.graph import StateGraph, END
from core.state import ResearchState
from core.memory import save_session, load_session
from agents.planner import planner_agent
from agents.searcher import searcher_agent
from agents.reader import reader_agent
from agents.critic import critic_agent
from agents.writer import writer_agent


def should_continue(state: ResearchState) -> str:
    """Route after critic — if quality too low, could re-search. For now always proceed."""
    if state.get("needs_more_research") and len(state.get("trace", [])) < 8:
        return "searcher"
    return "writer"


def build_graph():
    """Build and compile the LangGraph research pipeline."""
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_agent)
    graph.add_node("searcher", searcher_agent)
    graph.add_node("reader", reader_agent)
    graph.add_node("critic", critic_agent)
    graph.add_node("writer", writer_agent)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "searcher")
    graph.add_edge("searcher", "reader")
    graph.add_edge("reader", "critic")
    graph.add_conditional_edges("critic", should_continue, {
        "searcher": "searcher",
        "writer": "writer",
    })
    graph.add_edge("writer", END)

    return graph.compile()


def run_research(question: str, session_id: str = None) -> dict:
    """
    Run the full multi-agent research pipeline.
    Returns the final state with report, sources, and trace.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    print(f"\n{'='*60}")
    print(f"RESEARCH SESSION: {session_id}")
    print(f"QUESTION: {question}")
    print(f"{'='*60}")

    initial_state = ResearchState(
        question=question,
        session_id=session_id,
        sub_tasks=[],
        search_results=[],
        summaries=[],
        critique="",
        quality_score=0,
        needs_more_research=False,
        final_report="",
        sources=[],
        trace=[],
        current_agent="planner",
        error=None,
    )

    app = build_graph()

    try:
        final_state = app.invoke(initial_state)
        save_session(session_id, question, final_state)
        print(f"\n[Orchestrator] Research complete. Session saved.")
        return final_state

    except Exception as e:
        print(f"[Orchestrator] Error: {e}")
        initial_state["error"] = str(e)
        return initial_state


if __name__ == "__main__":
    result = run_research(
        "What are the latest breakthroughs in large language models in 2025?")
    print("\n" + "="*60)
    print("FINAL REPORT:")
    print("="*60)
    print(result["final_report"])
    print(f"\nQuality Score: {result['quality_score']}/10")
    print(f"Sources: {len(result['sources'])}")
    print(f"Agent steps: {len(result['trace'])}")
