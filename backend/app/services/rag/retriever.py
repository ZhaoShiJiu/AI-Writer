import uuid

from app.config import settings
from app.services.rag.embedder import embedder


class Retriever:
    """叙事检索引擎 — 基于 ChromaDB 的向量检索"""

    def __init__(self):
        self.collection_name = "novel_memory"
        self._client = None

    def _get_client(self):
        if self._client is None:
            import chromadb
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )
        return self._client

    def _get_collection(self, novel_id: int):
        client = self._get_client()
        name = f"{self.collection_name}_{novel_id}"
        try:
            return client.get_collection(name)
        except Exception:
            return client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )

    def _delete_collection(self, novel_id: int):
        try:
            client = self._get_client()
            client.delete_collection(f"{self.collection_name}_{novel_id}")
        except Exception:
            pass

    async def index_summary(
        self,
        novel_id: int,
        summary_id: int,
        text: str,
        metadata: dict | None = None,
    ) -> str:
        """将摘要索引到向量数据库"""
        embedding = await embedder.embed_single(text)
        if not embedding:
            return ""

        doc_id = f"summary_{summary_id}"
        collection = self._get_collection(novel_id)

        meta = metadata or {}
        meta["summary_id"] = summary_id

        collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[meta],
        )
        return doc_id

    async def index_chapter(
        self,
        novel_id: int,
        chapter_id: int,
        chunks: list[dict],
    ) -> list[str]:
        """将章节切块索引到向量数据库"""
        if not chunks:
            return []

        texts = [c["content"] for c in chunks]
        embeddings_list = await embedder.embed(texts)
        if not embeddings_list:
            return []

        collection = self._get_collection(novel_id)
        ids = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
            doc_id = f"ch_{chapter_id}_{i}"
            ids.append(doc_id)
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk["content"]],
                metadatas=[{
                    "chapter_id": chapter_id,
                    "chapter_title": chunk.get("chapter_title", ""),
                    "chunk_index": i,
                }],
            )
        return ids

    async def retrieve(
        self,
        novel_id: int,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """通用检索：按查询文本检索最相关的内容"""
        query_embedding = await embedder.embed_single(query)
        if not query_embedding:
            return self._keyword_fallback(novel_id, query, top_k)

        collection = self._get_collection(novel_id)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                retrieved.append({
                    "content": doc,
                    "metadata": meta,
                    "score": 1.0 - dist,  # cosine distance → similarity
                })
        return retrieved

    async def retrieve_by_character(
        self, novel_id: int, character_name: str, top_k: int = 5
    ) -> list[dict]:
        """按角色检索相关剧情"""
        return await self.retrieve(
            novel_id,
            f"涉及{character_name}的剧情和事件",
            top_k,
        )

    async def retrieve_by_emotion(
        self, novel_id: int, emotion: str, top_k: int = 3
    ) -> list[dict]:
        """按情绪检索相似场景"""
        return await self.retrieve(
            novel_id,
            f"氛围{emotion}的场景",
            top_k,
        )

    async def retrieve_by_world(
        self, novel_id: int, world_query: str, top_k: int = 3
    ) -> list[dict]:
        """按世界观要素检索"""
        return await self.retrieve(
            novel_id,
            f"世界观设定：{world_query}",
            top_k,
        )

    async def retrieve_by_event(
        self, novel_id: int, event_query: str, top_k: int = 5
    ) -> list[dict]:
        """按事件检索相关剧情"""
        return await self.retrieve(
            novel_id,
            f"事件：{event_query}",
            top_k,
        )

    def _keyword_fallback(self, novel_id: int, query: str, top_k: int) -> list[dict]:
        """当向量检索不可用时的关键词 fallback（返回空，由上层决定如何处理）"""
        return []

    def clear_novel(self, novel_id: int):
        """清除小说的所有向量索引"""
        self._delete_collection(novel_id)


retriever = Retriever()
