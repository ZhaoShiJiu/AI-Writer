"""Neo4j async client wrapper — singleton pattern, feature-gated."""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class GraphClient:
    """Async Neo4j client wrapper. Feature-gated: returns empty/no-op when disabled."""

    def __init__(self):
        self._driver = None
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    async def _ensure_driver(self):
        if self._driver is not None:
            return
        if not settings.feature_neo4j_enabled:
            return
        try:
            from neo4j import AsyncGraphDatabase

            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            # Verify connectivity
            async with self._driver.session(database=settings.neo4j_database) as session:
                await session.run("RETURN 1")
            self._connected = True
            logger.info("Neo4j connected: %s", settings.neo4j_uri)
        except Exception as e:
            logger.warning("Neo4j unavailable (feature will be disabled): %s", e)
            self._driver = None
            self._connected = False

    async def run_read(self, query: str, params: dict | None = None) -> list[dict]:
        """Run a read query and return list of record dicts."""
        if not settings.feature_neo4j_enabled:
            return []
        await self._ensure_driver()
        if not self._driver:
            return []

        try:
            async with self._driver.session(database=settings.neo4j_database) as session:
                result = await session.run(query, params or {})
                records = await result.data()
                return records
        except Exception as e:
            logger.warning("Neo4j read error: %s", e)
            return []

    async def run_write(self, query: str, params: dict | None = None) -> list[dict]:
        """Run a write query and return list of record dicts."""
        if not settings.feature_neo4j_enabled:
            return []
        await self._ensure_driver()
        if not self._driver:
            return []

        try:
            async with self._driver.session(database=settings.neo4j_database) as session:
                result = await session.run(query, params or {})
                records = await result.data()
                return records
        except Exception as e:
            logger.warning("Neo4j write error: %s", e)
            return []

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None
            self._connected = False


# Module-level singleton
_graph_client: GraphClient | None = None


def get_graph_client() -> GraphClient:
    global _graph_client
    if _graph_client is None:
        _graph_client = GraphClient()
    return _graph_client
