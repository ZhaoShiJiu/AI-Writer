"""Neo4j schema initialization — constraints and indexes."""

from app.services.graph.client import get_graph_client


NEO4J_CONSTRAINTS = [
    # Character nodes
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Character) REQUIRE c.name IS UNIQUE",
    # Event nodes
    "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Event) REQUIRE (e.novel_id, e.name) IS UNIQUE",
    # Location nodes
    "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE (l.novel_id, l.name) IS UNIQUE",
    # Faction nodes
    "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Faction) REQUIRE (f.novel_id, f.name) IS UNIQUE",
    # Foreshadowing nodes
    "CREATE CONSTRAINT IF NOT EXISTS FOR (fs:Foreshadowing) REQUIRE (fs.novel_id, fs.name) IS UNIQUE",
]

NEO4J_INDEXES = [
    # Speed up lookups by novel_id
    "CREATE INDEX IF NOT EXISTS FOR (c:Character) ON (c.novel_id)",
    "CREATE INDEX IF NOT EXISTS FOR (e:Event) ON (e.novel_id)",
    "CREATE INDEX IF NOT EXISTS FOR (l:Location) ON (l.novel_id)",
    "CREATE INDEX IF NOT EXISTS FOR (f:Faction) ON (f.novel_id)",
    # Speed up event ordering
    "CREATE INDEX IF NOT EXISTS FOR (e:Event) ON (e.chapter_id)",
    # Speed up foreshadowing status lookup
    "CREATE INDEX IF NOT EXISTS FOR (fs:Foreshadowing) ON (fs.status)",
]


async def ensure_schema() -> None:
    """Run on startup to ensure Neo4j constraints and indexes exist.
    Feature-gated: does nothing if neo4j is disabled."""
    from app.config import settings

    if not settings.feature_neo4j_enabled:
        return

    client = get_graph_client()
    # run_write will connect lazily on first call
    try:
        for stmt in NEO4J_CONSTRAINTS + NEO4J_INDEXES:
            await client.run_write(stmt)
    except Exception:
        pass  # Schema already exists or Neo4j community constraints conflict
