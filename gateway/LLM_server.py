import logging
import os
import traceback
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from litellm import completion_with_retries
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


@app.get("/health")
def health():
    return {"status": "ok"}
