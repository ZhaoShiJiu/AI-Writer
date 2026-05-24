FROM python:3.14-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app

RUN HTTP_PROXY=$HTTP_PROXY HTTPS_PROXY=$HTTPS_PROXY pip install --no-cache-dir fastapi uvicorn litellm tenacity

COPY LLM_server.py .

CMD ["uvicorn", "LLM_server:app", "--host", "0.0.0.0", "--port", "8001"]
