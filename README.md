# Multi-Agent AI Orchestration Platform

Built a modular **Multi-Agent AI Orchestration Platform** project that showcases a **planner → researcher → executor → analyzer → formatter** workflow using FastAPI, Streamlit, tool calling, memory snapshots, task dependencies, execution logs. Featuring task decomposition, tool calling, task graphs, execution tracing, and memory-backed workflow state.

## Features
- Multi-agent orchestration pipeline
- Full backend API with FastAPI
- Interactive Streamlit dashboard
- Tool calling for search, finance analysis, and Python execution
- Task dependency graph
- Execution logs stored in SQLite
- Memory snapshots per run
- Smoke test included

## Architecture
```text
User Query
  ↓
Planner Agent
  ↓
Researcher Agent → Search Tool
  ↓
Executor Agent → Finance Tool / Python Exec Tool
  ↓
Analyzer Agent
  ↓
Formatter Agent
  ↓
Final Output + Logs + Dashboard
```

## Project Structure
```text
multi-agent-ai/
├── backend/
│   ├── agents/
│   ├── core/
│   ├── memory/
│   ├── orchestrator/
│   ├── schemas/
│   ├── tools/
│   └── main.py
├── dashboard/
│   └── app.py
├── tests/
│   └── test_smoke.py
├── requirements.txt
└── README.md
```

## Run Locally
```bash
cd multi-agent-ai
python -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

### Start backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### Start dashboard
Open another terminal in the same folder:
```bash
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
streamlit run dashboard/app.py
```

## Endpoints
- `GET /health`
- `POST /run`
- `GET /runs/{run_id}`
- `GET /logs/{run_id}`
- `WS /ws/logs/{run_id}`

## Example Request
```json
{
  "query": "Analyze Tesla stock"
}
```

## Notes
- The system works in **mock-safe mode by default** so it runs even without OpenAI keys.
- Search uses a lightweight live Wikipedia summary call when available and falls back gracefully.
- Finance analysis uses demo price series unless you extend it with a real market API.

## Test
```bash
pytest -q
```
