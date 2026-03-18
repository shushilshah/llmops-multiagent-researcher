import streamlit as st
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 Multi-Agent Research Assistant")
st.caption(
    "Autonomous AI agents that search, read, critique, and synthesize research in real time")

# ── Sidebar ──
with st.sidebar:
    st.header("🕒 Recent Sessions")
    try:
        resp = requests.get(f"{API_URL}/sessions", timeout=5)
        if resp.status_code == 200:
            sessions = resp.json().get("sessions", [])
            if sessions:
                for s in sessions[:8]:
                    q = s.get("question", "")[:50]
                    score = s.get("quality_score", "?")
                    if st.button(f"📄 {q}... (score: {score}/10)", use_container_width=True):
                        st.session_state["load_session"] = s.get("session_id")
            else:
                st.caption("No sessions yet")
    except:
        st.caption("API offline")

    st.divider()
    st.markdown("""
    **How it works:**
    
    1. 🧠 **Planner** breaks your question into sub-tasks
    2. 🔍 **Searcher** finds real web sources via Tavily
    3. 📖 **Reader** summarizes each source with Gemini
    4. ⚖️ **Critic** scores research quality (1-10)
    5. ✍️ **Writer** generates structured report
    6. 💾 **MongoDB** stores every session
    """)
    st.divider()
    st.markdown("**Stack:** LangGraph · Gemini · Tavily · MongoDB · FastAPI")

# ── Main ──
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Ask a Research Question")
    question = st.text_area(
        "Enter your question",
        placeholder="e.g. What are the latest breakthroughs in cancer immunotherapy in 2025?",
        height=100,
    )

    example_questions = [
        "What are the latest AI breakthroughs in 2025?",
        "How is climate change affecting Nepal?",
        "What is the future of electric vehicles?",
        "How does transformer architecture work in LLMs?",
    ]

    st.caption("Try an example:")
    cols = st.columns(2)
    for i, q in enumerate(example_questions):
        if cols[i % 2].button(q, use_container_width=True):
            question = q

    run_btn = st.button("🚀 Start Research", type="primary", use_container_width=True,
                        disabled=not question.strip())

with col2:
    st.header("Agent Pipeline")
    agents = [
        ("🧠", "Planner", "Breaks question into sub-tasks"),
        ("🔍", "Searcher", "Searches web via Tavily"),
        ("📖", "Reader", "Summarizes sources"),
        ("⚖️", "Critic", "Scores quality"),
        ("✍️", "Writer", "Generates report"),
        ("💾", "Memory", "Saves to MongoDB"),
    ]
    for emoji, name, desc in agents:
        st.markdown(f"{emoji} **{name}** — {desc}")

# ── Results ──
if run_btn and question.strip():
    st.divider()

    progress_bar = st.progress(0, text="Starting research pipeline...")
    status_text = st.empty()

    trace_container = st.expander(
        "🔍 Live Agent Reasoning Trace", expanded=True)
    trace_placeholder = trace_container.empty()

    with st.spinner("Agents working..."):
        try:
            status_text.info("🧠 Planner is analyzing your question...")
            progress_bar.progress(10, "Planner running...")

            response = requests.post(
                f"{API_URL}/research",
                json={"question": question},
                timeout=180,
            )

            if response.status_code == 200:
                data = response.json()
                progress_bar.progress(100, "Complete!")
                status_text.success(
                    f"Research complete! Quality score: {data['quality_score']}/10")

                # Show trace
                trace_md = ""
                for step in data["trace"]:
                    agent = step.get("agent", "")
                    msg = step.get("message", "")
                    ts = step.get("timestamp", "")[:19].replace("T", " ")
                    trace_md += f"**[{ts}] {agent}:** {msg}\n\n"
                trace_placeholder.markdown(trace_md)

                # Tabs for results
                tab1, tab2, tab3 = st.tabs(
                    ["📄 Report", "📊 Analysis", "🔗 Sources"])

                with tab1:
                    st.markdown(data["final_report"])
                    st.download_button(
                        "⬇️ Download Report",
                        data=data["final_report"],
                        file_name=f"research_{data['session_id'][:8]}.md",
                        mime="text/markdown",
                    )

                with tab2:
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Quality Score",
                                 f"{data['quality_score']}/10")
                    col_b.metric("Sources Found", data["total_sources"])
                    col_c.metric("Agent Steps", data["agent_steps"])

                    st.subheader("Sub-tasks")
                    for i, t in enumerate(data["sub_tasks"]):
                        st.write(f"{i+1}. {t}")

                    st.subheader("Critic's Assessment")
                    st.info(data["critique"])

                with tab3:
                    for src in data["sources"]:
                        if src.get("url"):
                            st.markdown(f"- [{src['title']}]({src['url']})")

                # Feedback
                st.divider()
                st.subheader("Rate this research")
                rating = st.slider("How useful was this report?", 1, 5, 4)
                comment = st.text_input("Any comments? (optional)")
                if st.button("Submit Feedback"):
                    fb_resp = requests.post(f"{API_URL}/feedback", json={
                        "session_id": data["session_id"],
                        "rating": rating,
                        "comment": comment,
                    })
                    if fb_resp.status_code == 200:
                        st.success("Feedback saved!")

            else:
                st.error(
                    f"Error: {response.json().get('detail', 'Unknown error')}")

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to API. Make sure FastAPI is running on port 8000.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
