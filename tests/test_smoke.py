from backend.orchestrator.engine import Orchestrator
import asyncio


def test_orchestrator_smoke():
    state = asyncio.run(Orchestrator().run(run_id="test-run", query="Analyze Tesla stock"))
    assert state.status == "COMPLETED"
    assert state.final_output is not None
    assert len(state.tasks) == 5
