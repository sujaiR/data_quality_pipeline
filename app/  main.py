from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.engine import SimpleGraphEngine
from app.tools import TOOLS
from app.workflows.data_quality_workflow import data_quality_graph
import uvicorn
import asyncio

app = FastAPI(title="Minimal Workflow Engine - Data Quality Pipeline")

engine = SimpleGraphEngine()

class GraphCreateRequest(BaseModel):
    graph: Dict[str, Any]

class RunRequest(BaseModel):
    graph_id: Optional[str] = None
    initial_state: Dict[str, Any]

@app.post('/graph/create')
async def create_graph(req: GraphCreateRequest):
    graph_id = engine.create_graph(req.graph)
    return {'graph_id': graph_id}

@app.post('/graph/create/sample')
async def create_sample_graph():
    graph_id = engine.create_graph(data_quality_graph)
    return {'graph_id': graph_id, 'note': 'sample data quality graph created'}

@app.post('/graph/run')
async def run_graph(req: RunRequest):
    gid = req.graph_id
    if gid is None:
        # create ephemeral graph and run it
        gid = engine.create_graph(req.initial_state.get('_graph', data_quality_graph))
    try:
        # support passing CSV text in initial_state['data_csv']
        result = await engine.run_graph(gid, req.initial_state, TOOLS)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail='graph not found')

@app.get('/graph/state/{run_id}')
async def get_state(run_id: str):
    s = engine.get_run_state(run_id)
    if not s:
        raise HTTPException(status_code=404, detail='run_id not found')
    return s

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
