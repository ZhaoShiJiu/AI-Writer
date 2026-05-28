import logging
import os
import traceback
from typing import Any

import dashscope
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from litellm import completion_with_retries, embedding
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    choices: list[dict[str, Any]]


@app.post("/chat/completions")
def api_completions(request: ChatRequest):
    logger.info(f"Request: model={request.model}, messages_count={len(request.messages)}")

    try:
        messages = [m.model_dump() for m in request.messages]
        response = completion_with_retries(model=request.model, messages=messages)
        logger.info(f"Response received from model {request.model}")
        return response
    except Exception as e:
        logger.error(f"LLM call failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")


class EmbeddingRequest(BaseModel):
    model: str
    input: str | list[str]


@app.post("/embeddings")
def api_embeddings(request: EmbeddingRequest):
    inputs = request.input if isinstance(request.input, list) else [request.input]
    logger.info(f"Embedding request: model={request.model}, count={len(inputs)}")

    if request.model.startswith("dashscope/"):
        return _dashscope_embed(request.model, inputs)

    try:
        response = embedding(model=request.model, input=request.input)
        return response
    except Exception as e:
        logger.error(f"Embedding call failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Embedding call failed: {str(e)}")


def _dashscope_embed(model: str, texts: list[str]):
    model_name = model.replace("dashscope/", "")
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="DASHSCOPE_API_KEY not configured")

    resp = dashscope.TextEmbedding.call(
        model=model_name,
        input=texts,
        text_type="document",
        api_key=api_key,
    )

    if resp.status_code != 200:
        logger.error(f"DashScope embedding failed: {resp.code} {resp.message}")
        raise HTTPException(status_code=502, detail=f"DashScope: {resp.message}")

    data = [
        {"index": item["text_index"], "embedding": item["embedding"]}
        for item in resp.output["embeddings"]
    ]
    return {"object": "list", "data": data, "model": model_name}


@app.get("/health")
def health():
    return {"status": "ok"}
