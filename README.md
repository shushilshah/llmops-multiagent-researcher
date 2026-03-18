---
title: Multi Agent Research Assistant
emoji: 🔬
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: true
---

# 🔬 Multi-Agent Research Assistant

An autonomous AI system where **5 specialized agents** collaborate to research any topic — finding real web sources, summarizing them, critiquing quality, and synthesizing a structured report.

---

## How it works

Enter any research question and watch 5 agents work in sequence:

| Agent | Role |
|-------|------|
| 🧠 **Planner** | Breaks your question into 3-5 specific search queries |
| 🔍 **Searcher** | Finds real web sources via Tavily Search API |
| 📖 **Reader** | Summarizes each source using Gemini 2.0 Flash |
| ⚖️ **Critic** | Scores research quality (1-10) and detects gaps |
| ✍️ **Writer** | Synthesizes everything into a structured markdown report |

Every session is stored in **MongoDB Atlas** for history and feedback tracking.

---

## Tech Stack

- **Agent Orchestration** — LangGraph
- **LLM** — Google Gemini 2.0 Flash
- **Web Search** — Tavily API
- **Memory** — MongoDB Atlas
- **UI** — Gradio
- **API** — FastAPI
- **Containerization** — Docker

---

## Example Questions

- What are the latest breakthroughs in large language models in 2025?
- How is climate change affecting agriculture in Nepal?
- What is the future of quantum computing?
- How do transformer architectures work?
- What skills do data scientists need in 2026?

---

## Author

**Shushil Shah** — Data Scientist & ML Engineer

[LinkedIn](https://linkedin.com/in/shushilshah) · [GitHub](https://github.com/shushilshah) · [Churn Prediction Demo](https://huggingface.co/spaces/Sentogya/churn-prediction)