from __future__ import annotations
import requests
import streamlit as st
import pandas as pd
from graphviz import Digraph

API_URL = st.sidebar.text_input("Backend URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Multi-Agent AI Dashboard", layout="wide")
st.title("🧠 Multi-Agent AI Orchestration Dashboard")
st.caption("Planner → Researcher → Executor → Analyzer → Formatter")


def task_graph(tasks: list[dict]) -> Digraph:
    dot = Digraph()
    color_map = {
        "PENDING": "gray",
        "RUNNING": "deepskyblue",
        "COMPLETED": "green",
        "FAILED": "red",
    }
    for task in tasks:
        label = f"{task['agent']}\n{task['title']}\n{task['status']}"
        dot.node(task["id"], label=label, color=color_map.get(task["status"], "white"))
    for task in tasks:
        for dep in task.get("depends_on", []):
            dot.edge(dep, task["id"])
    return dot


with st.form("run-form"):
    query = st.text_area(
        "Enter a task",
        value="Analyze Tesla stock",
        help="Try: Analyze Tesla stock | Summarize AI orchestration | Research machine learning",
        height=120,
    )
    submit = st.form_submit_button("Run Workflow")

if submit:
    with st.spinner("Running multi-agent workflow..."):
        response = requests.post(f"{API_URL}/run", json={"query": query}, timeout=30)
        response.raise_for_status()
        st.session_state["run"] = response.json()
        st.session_state["run_id"] = response.json()["run_id"]

run = st.session_state.get("run")
run_id = st.session_state.get("run_id")

if run:
    st.success(f"Run completed: {run['status']} | Run ID: {run_id}")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Workflow Graph")
        st.graphviz_chart(task_graph(run["tasks"]))

    with col2:
        st.subheader("Final Output")
        st.markdown(run.get("final_output") or "No output")

    t1, t2, t3 = st.tabs(["Tasks", "Logs", "Tool Calls"])

    with t1:
        df = pd.DataFrame([
            {
                "agent": t["agent"],
                "title": t["title"],
                "status": t["status"],
                "depends_on": ", ".join(t.get("depends_on", [])),
            }
            for t in run["tasks"]
        ])
        st.dataframe(df, use_container_width=True)

    with t2:
        logs = requests.get(f"{API_URL}/logs/{run_id}", timeout=15).json()
        for log in logs:
            st.code(f"[{log['timestamp']}] [{log['source']}] {log['message']}", language="text")

    with t3:
        for task in run["tasks"]:
            calls = task.get("tool_calls", [])
            if calls:
                st.markdown(f"### {task['agent'].title()}")
                for call in calls:
                    st.json(call)
else:
    st.info("Submit a task to see the full orchestration flow.")
