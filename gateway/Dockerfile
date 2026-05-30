FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn litellm tenacity dashscope

COPY LLM_server.py .

CMD ["uvicorn", "LLM_server:app", "--host", "0.0.0.0", "--port", "8001"]