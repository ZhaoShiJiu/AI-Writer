"""Redis caching for V4 workflow — LLM response cache + state checkpointing."""

import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class WorkflowCache:
    """Caches LLM responses and workflow states in Redis."""

    def __init__(self):
        self._redis = None

    async def _get_redis(self):
        if self._redis is not None:
            return self._redis
        try:
            import redis.asyncio as aioredis
            from app.config import settings

            self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
            await self._redis.ping()
            logger.info("Redis connected for V4 workflow cache")
        except Exception as e:
            logger.warning("Redis unavailable for V4 cache: %s", e)
            self._redis = None
        return self._redis

    @staticmethod
    def _llm_cache_key(system_prompt: str, user_prompt: str, model: str) -> str:
        content = f"{system_prompt}|||{user_prompt}|||{model}"
        h = hashlib.sha256(content.encode()).hexdigest()[:32]
        return f"v4:llm:{h}"

    @staticmethod
    def _state_cache_key(novel_id: int, chapter_id: int) -> str:
        return f"v4:state:{novel_id}:{chapter_id}"

    async def get_llm_response(self, system_prompt: str, user_prompt: str, model: str) -> str | None:
        """Get cached LLM response."""
        r = await self._get_redis()
        if not r:
            return None
        key = self._llm_cache_key(system_prompt, user_prompt, model)
        try:
            cached = await r.get(key)
            if cached:
                logger.info("V4 Cache: LLM response hit")
                return cached
        except Exception:
            pass
        return None

    async def set_llm_response(self, system_prompt: str, user_prompt: str, model: str, response: str) -> None:
        """Cache LLM response."""
        r = await self._get_redis()
        if not r:
            return
        key = self._llm_cache_key(system_prompt, user_prompt, model)
        try:
            from app.config import settings
            await r.setex(key, settings.redis_cache_ttl, response)
        except Exception:
            pass

    async def save_state(self, novel_id: int, chapter_id: int, state: dict) -> None:
        """Save workflow state checkpoint."""
        r = await self._get_redis()
        if not r:
            return
        key = self._state_cache_key(novel_id, chapter_id)
        try:
            # Convert non-serializable values
            clean = {}
            for k, v in state.items():
                if k.startswith("_"):
                    continue
                try:
                    json.dumps(v)
                    clean[k] = v
                except (TypeError, ValueError):
                    clean[k] = str(v)
            await r.setex(key, 1800, json.dumps(clean, default=str))
        except Exception:
            pass

    async def load_state(self, novel_id: int, chapter_id: int) -> dict | None:
        """Load workflow state checkpoint."""
        r = await self._get_redis()
        if not r:
            return None
        key = self._state_cache_key(novel_id, chapter_id)
        try:
            data = await r.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    async def cache_graph_data(self, novel_id: int, graph_data: dict) -> None:
        """Cache story graph query result."""
        r = await self._get_redis()
        if not r:
            return
        key = f"v4:graph:{novel_id}"
        try:
            await r.setex(key, 600, json.dumps(graph_data, default=str))
        except Exception:
            pass

    async def get_cached_graph_data(self, novel_id: int) -> dict | None:
        """Get cached graph data."""
        r = await self._get_redis()
        if not r:
            return None
        key = f"v4:graph:{novel_id}"
        try:
            data = await r.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None


# Module-level singleton
workflow_cache = WorkflowCache()
