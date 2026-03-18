import os
from datetime import datetime
from tavily import TavilyClient
from core.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

MAX_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", 5))


def searcher_agent(state: ResearchState) -> ResearchState:
    """Search the web for each sub-task using Tavily."""
    print(f"\n[Searcher] Running {len(state['sub_tasks'])} searches...")

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    all_results = []

    for i, task in enumerate(state["sub_tasks"]):
        print(f"  [{i+1}/{len(state['sub_tasks'])}] Searching: {task}")
        try:
            response = client.search(
                query=task,
                max_results=MAX_RESULTS,
                search_depth="advanced",
                include_answer=True,
            )

            results = []
            for r in response.get("results", []):
                results.append({
                    "sub_task": task,
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:1200],  # limit content length
                    "score": r.get("score", 0),
                })

            # Also include Tavily's direct answer if available
            if response.get("answer"):
                results.insert(0, {
                    "sub_task": task,
                    "title": "Tavily Direct Answer",
                    "url": "",
                    "content": response["answer"],
                    "score": 1.0,
                })

            all_results.extend(results)
            print(f"     Found {len(results)} results")

        except Exception as e:
            print(f"  [Searcher] Error searching '{task}': {e}")

    print(f"[Searcher] Total results collected: {len(all_results)}")

    trace_entry = {
        "agent": "Searcher",
        "timestamp": datetime.utcnow().isoformat(),
        "input": state["sub_tasks"],
        "output": f"{len(all_results)} results from {len(state['sub_tasks'])} searches",
        "message": f"Found {len(all_results)} sources across {len(state['sub_tasks'])} queries",
    }

    return {
        **state,
        "search_results": all_results,
        "current_agent": "reader",
        "trace": [trace_entry],
    }