from typing import Callable, Dict, Any, List, Optional
import uuid
import asyncio

RunState = Dict[str, Any]
NodeFn = Callable[[RunState], Any]

class SimpleGraphEngine:
    def __init__(self):
        self.graphs = {}  # graph_id -> graph definition
        self.runs = {}    # run_id -> run info

    def create_graph(self, graph_def: Dict[str, Any]) -> str:
        graph_id = str(uuid.uuid4())
        # expect graph_def: {'nodes': {'name': {'fn': 'tool_name', 'next': '...'}}, 'start': 'profile'}
        self.graphs[graph_id] = graph_def
        return graph_id

    async def _run_node(self, node_name: str, node_def: Dict[str, Any], state: RunState, tools_registry: Dict[str, NodeFn], run_log: List[str]):
        fn_name = node_def.get('fn')
        tool = tools_registry.get(fn_name)
        run_log.append(f"Running node={node_name}, fn={fn_name}")
        if asyncio.iscoroutinefunction(tool):
            res = await tool(state)
        else:
            # run in threadpool to avoid blocking
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, tool, state)
        # tool may return dict updates
        if isinstance(res, dict):
            state.update(res)
        run_log.append(f"Finished node={node_name}, produced={res}")
        return state

    async def run_graph(self, graph_id: str, initial_state: RunState, tools_registry: Dict[str, NodeFn]) -> Dict[str, Any]:
        graph = self.graphs.get(graph_id)
        if not graph:
            raise KeyError("graph not found")
        state = dict(initial_state)
        run_id = str(uuid.uuid4())
        run_log = []
        self.runs[run_id] = {'state': state, 'log': run_log, 'status': 'running'}
        start_node = graph.get('start')
        current = start_node
        visited = 0
        # naive loop protection
        while current:
            visited += 1
            if visited > 100:
                run_log.append("Max iterations reached, stopping")
                break
            node_def = graph['nodes'].get(current)
            if not node_def:
                run_log.append(f"Node definition for {current} not found, stopping")
                break
            state = await self._run_node(current, node_def, state, tools_registry, run_log)
            # determine next
            # support conditional next as dict: {'cond': 'lambda', 'true': 'a', 'false': 'b'}
            next_def = node_def.get('next')
            if not next_def:
                current = None
                break
            if isinstance(next_def, str):
                current = next_def
            elif isinstance(next_def, dict):
                # simple conditional evaluation based on state keys
                cond_key = next_def.get('cond_key')
                op = next_def.get('op', 'gt')
                value = next_def.get('value')
                true_branch = next_def.get('true')
                false_branch = next_def.get('false')
                val = state.get(cond_key)
                take_true = False
                try:
                    if op == 'gt':
                        take_true = float(val) > float(value)
                    elif op == 'lt':
                        take_true = float(val) < float(value)
                    elif op == 'eq':
                        take_true = val == value
                    elif op == 'gt_eq':
                        take_true = float(val) >= float(value)
                except Exception:
                    take_true = False
                current = true_branch if take_true else false_branch
            else:
                current = None
        self.runs[run_id]['state'] = state
        self.runs[run_id]['status'] = 'finished'
        return {'run_id': run_id, 'final_state': state, 'log': run_log}

    def get_run_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self.runs.get(run_id)
