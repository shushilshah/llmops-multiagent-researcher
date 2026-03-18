# Multi-Agent Research Assistant

An autonomous AI research system where **5 specialized agents** collaborate to answer any research question with real web sources, quality critique, and a structured report.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Langchain](https://img.shields.io/badge/Langchain-0.2-green)
![Groq](https://img.shields.io/badge/LLM-Groq%201.5-orange)
![Tavily](https://img.shields.io/badge/Search-Tavily-purple)
![MongoDB](https://img.shields.io/badge/Memory-MongoDB-green)

---

## Agent Pipeline

```
User Question
      │
      ▼
┌─────────────┐
│   Planner   │ → breaks question into 3-5 search queries
└──────┬──────┘
       ▼
┌─────────────┐
│   Searcher  │ → Tavily web search (real sources)
└──────┬──────┘
       ▼
┌─────────────┐
│   Reader    │ → Groq summarizes each source
└──────┬──────┘
       ▼
┌─────────────┐
│   Critic    │ → scores quality (1-10), detects gaps
└──────┬──────┘
       ▼
┌─────────────┐
│   Writer    │ → structured markdown report
└──────┬──────┘
       ▼
┌─────────────┐
│   MongoDB   │ → persists session + feedback
└─────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Orchestration | LangGraph |
| LLM | Groq llama-3.3-70b-versatile |
| Web Search | Tavily API |
| Memory | MongoDB Atlas |
| API | FastAPI |
| UI | Streamlit + Gradio (HF Spaces) |
| Containerization | Docker |

---

## Quickstart

```bash
git clone https://github.com/shushilshah/multi-agent-research-assistant.git
cd multi-agent-research-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # fill in your API keys
```

### Run locally
```bash
# Terminal 1 — API
uvicorn api.main:app --reload --port 8000

# Terminal 2 — UI
streamlit run ui/app.py
```

### Test the pipeline directly
```bash
python core/orchestrator.py
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key |
| `TAVILY_API_KEY` | Tavily search API key |
| `MONGODB_URI` | MongoDB Atlas connection string |

---

## Live Demo

[Hugging Face Space →](https://huggingface.co/spaces/Sentogya/multi-agent-research)

---

## Author

**Shushil Shah** — Data Scientist & ML Engineer  
[LinkedIn](https://linkedin.com/in/shushilshah) · [GitHub](https://github.com/shushilshah)