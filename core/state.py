from typing import TypedDict, List, Optional, Annotated
import operator

class ResearchState(TypedDict):
    """Shared state passed between all agents in the graph."""

    # input
    question: str
    session_id: str

    # planner
    sub_tasks: List[str]

    #Searcher output
    search_results: List[dict]

    # Reader output
    summaries: List[dict]

    # Critic output
    critique: str
    quality_score: int
    needs_more_research: bool

    #writer output
    final_report: str
    sources: List[dict]

    # Trace every agent appends its reasoning
    trace: Annotated[List[dict], operator.add]

    # status
    current_agent: str
    error: Optional[str]
