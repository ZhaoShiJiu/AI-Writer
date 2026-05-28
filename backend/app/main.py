from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import novels, chapters, ai, memory


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Novel Write API", version="2.0.0", lifespan=lifespan)

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


@app.get("/api/health")
async def health():
    return {"status": "ok"}
