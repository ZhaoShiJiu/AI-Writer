FROM python:3.14-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libc-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN HTTP_PROXY=$HTTP_PROXY HTTPS_PROXY=$HTTPS_PROXY pip install --no-cache-dir -r requirements.txt

RUN apt-get purge -y gcc libc-dev && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
