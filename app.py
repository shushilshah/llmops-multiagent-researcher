import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from core.orchestrator import run_research


def research(question: str):
    if not question.strip():
        return "Please enter a research question.", "", "", "", ""

    try:
        result = run_research(question)

        if result.get("error"):
            return f"Error: {result['error']}", "", "", "", ""

        # Format agent trace
        trace_md = ""
        for step in result.get("trace", []):
            agent = step.get("agent", "")
            msg = step.get("message", "")
            ts = step.get("timestamp", "")[:19].replace("T", " ")
            trace_md += f"**[{ts}] {agent}:** {msg}\n\n"

        # Format sources
        sources_md = ""
        for i, src in enumerate(result.get("sources", [])):
            if src.get("url"):
                sources_md += f"{i+1}. [{src['title']}]({src['url']})\n"
            else:
                sources_md += f"{i+1}. {src.get('title', 'Unknown')}\n"

        # Sub-tasks
        subtasks_md = ""
        for i, t in enumerate(result.get("sub_tasks", [])):
            subtasks_md += f"{i+1}. {t}\n"

        # Quality
        score = result.get("quality_score", 0)
        critique = result.get("critique", "")
        quality_md = f"**Score: {score}/10**\n\n{critique}"

        return (
            result.get("final_report", "No report generated."),
            trace_md or "No trace available.",
            sources_md or "No sources found.",
            subtasks_md or "No sub-tasks.",
            quality_md,
        )

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return error_msg, "", "", "", ""


with gr.Blocks(title="Multi-Agent Research Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🔬 Multi-Agent Research Assistant
    
    Five autonomous AI agents collaborate to answer any research question:
    
    **🧠 Planner** → **🔍 Searcher** → **📖 Reader** → **⚖️ Critic** → **✍️ Writer**
    
    Powered by **LangGraph · Gemini 2.0 Flash · Tavily · MongoDB**
    """)

    with gr.Row():
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="Research Question",
                placeholder="e.g. What are the latest breakthroughs in large language models in 2025?",
                lines=3,
            )
            submit_btn = gr.Button("🚀 Start Research", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("""
            **Try these questions:**
            """)
            examples = [
                "Latest AI breakthroughs in 2025?",
                "Future of data science careers?",
                "How does RAG work in LLMs?",
                "Climate change impact on Nepal?",
            ]
            for ex in examples:
                gr.Button(ex, size="sm").click(
                    fn=lambda q=ex: q,
                    outputs=question_input
                )

    with gr.Tabs():
        with gr.Tab("📄 Final Report"):
            report_output = gr.Markdown(label="Research Report")

        with gr.Tab("🔍 Agent Trace"):
            trace_output = gr.Markdown(label="Agent Reasoning Steps")

        with gr.Tab("📋 Sub-Tasks"):
            subtasks_output = gr.Markdown(label="Search Queries Used")

        with gr.Tab("🔗 Sources"):
            sources_output = gr.Markdown(label="Web Sources")

        with gr.Tab("⚖️ Quality Score"):
            quality_output = gr.Markdown(label="Critic Evaluation")

    submit_btn.click(
        fn=research,
        inputs=[question_input],
        outputs=[
            report_output,
            trace_output,
            sources_output,
            subtasks_output,
            quality_output,
        ],
    )

    gr.Markdown("""
    ---
    Built by [Shushil Shah](https://linkedin.com/in/shushilshah) · 
    [GitHub](https://github.com/shushilshah) · 
    [Churn Prediction Demo](https://huggingface.co/spaces/Sentogya/churn-prediction)
    """)

if __name__ == "__main__":
    demo.launch()