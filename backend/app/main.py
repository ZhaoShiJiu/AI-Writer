import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import novels, chapters, ai, memory, style, narrative, emotion, v4

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Startup: initialize Neo4j schema if enabled
    try:
        from app.services.graph.schema import ensure_schema
        await ensure_schema()
    except Exception as e:
        logger.warning("Neo4j schema init skipped: %s", e)

    # Startup: warm up Redis connection
    try:
        from app.services.workflow.cache import workflow_cache
        await workflow_cache._get_redis()
    except Exception:
        pass

    yield

    # Shutdown: close Neo4j driver
    try:
        from app.services.graph.client import get_graph_client
        client = get_graph_client()
        await client.close()
    except Exception:
        pass


app = FastAPI(title="Novel Write API", version="4.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(novels.router, prefix="/api")
app.include_router(chapters.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(memory.router)
app.include_router(style.router)
app.include_router(narrative.router)
app.include_router(emotion.router)
app.include_router(v4.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "4.0.0"}
