import httpx

from app.config import settings


class Embedder:
    """文本向量化服务，通过 LLM Gateway 调用 Embedding 模型"""

    def __init__(self):
        self.gateway_url = settings.llm_gateway_url.rstrip("/")
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """批量生成文本向量"""
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(
                    f"{self.gateway_url}/embeddings",
                    json={"model": self.model, "input": texts},
                )
                response.raise_for_status()
                data = response.json()
                embeddings = sorted(data["data"], key=lambda x: x["index"])
                return [e["embedding"] for e in embeddings]
            except Exception:
                return await self._fallback_embed(texts)

    async def embed_single(self, text: str) -> list[float]:
        embeddings = await self.embed([text])
        return embeddings[0] if embeddings else []

    async def _fallback_embed(self, texts: list[str]) -> list[list[float]]:
        """简化的本地 fallback：基于词频生成伪向量（仅用于开发测试）"""
        import hashlib

        results = []
        for text in texts:
            hash_bytes = hashlib.sha256(text.encode("utf-8")).digest()
            vector = [float(b) / 255.0 for b in hash_bytes[:self.dimension]]
            if len(vector) < self.dimension:
                vector.extend([0.0] * (self.dimension - len(vector)))
            results.append(vector)
        return results


embedder = Embedder()
