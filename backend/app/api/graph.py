from fastapi import APIRouter

from app.core.graph_engine import build_memory_graph

router = APIRouter()


@router.get("/memory-graph")
async def memory_graph():
    graph = build_memory_graph()

    return {
        "status": "ok",
        "graph": graph
    }