"""Story Graph Service — Neo4j graph operations for characters, events, factions, foreshadowings."""

import logging

from app.services.graph.client import get_graph_client

logger = logging.getLogger(__name__)


class StoryGraphService:
    """Maintains and queries the Neo4j story graph."""

    def __init__(self):
        self.client = get_graph_client()

    def _enabled(self) -> bool:
        from app.config import settings
        return settings.feature_neo4j_enabled

    # ---- Sync from PostgreSQL ----

    async def sync_characters(self, novel_id: int, characters: list[dict]) -> None:
        """Upsert character nodes from character_memory data."""
        if not self._enabled():
            return
        for char in characters:
            # Handle both dict and ORM object
            if hasattr(char, "character_name"):
                name = char.character_name
                mj = char.memory_json or {}
            else:
                name = char.get("character_name", "")
                mj = char.get("memory_json", {})
            realm = mj.get("realm", "")
            personality = mj.get("personality", [])
            notes = mj.get("notes", "")
            await self.client.run_write(
                """
                MERGE (c:Character {novel_id: $novel_id, name: $name})
                SET c.realm = $realm,
                    c.personality = $personality,
                    c.notes = $notes
                """,
                {"novel_id": novel_id, "name": name, "realm": realm,
                 "personality": personality, "notes": notes},
            )

    async def sync_character_relations(self, novel_id: int, characters: list[dict]) -> None:
        """Create RELATED_TO edges from character relationship data."""
        if not self._enabled():
            return
        for char in characters:
            if hasattr(char, "character_name"):
                name = char.character_name
                mj = char.memory_json or {}
            else:
                name = char.get("character_name", "")
                mj = char.get("memory_json", {})
            relationships = mj.get("relationships", [])
            for rel in relationships:
                target = rel.get("target", "")
                relation = rel.get("relation", "")
                if target:
                    await self.client.run_write(
                        """
                        MATCH (a:Character {novel_id: $novel_id, name: $name})
                        MATCH (b:Character {novel_id: $novel_id, name: $target})
                        MERGE (a)-[r:RELATED_TO {relation: $relation}]->(b)
                        """,
                        {"novel_id": novel_id, "name": name, "target": target, "relation": relation},
                    )

    async def sync_events(self, novel_id: int, summaries: list[dict]) -> None:
        """Upsert event nodes from chapter summaries."""
        if not self._enabled():
            return
        for s in summaries:
            name = s.get("summary", "")[:100]
            chapter_id = s.get("chapter_id")
            events = s.get("important_events", [])
            for evt in events:
                evt_name = evt if isinstance(evt, str) else evt.get("name", str(evt))
                await self.client.run_write(
                    """
                    MERGE (e:Event {novel_id: $novel_id, name: $name})
                    SET e.chapter_id = $chapter_id,
                        e.description = $description
                    """,
                    {"novel_id": novel_id, "name": evt_name[:200],
                     "chapter_id": chapter_id, "description": name},
                )

    async def sync_factions_and_locations(self, novel_id: int, world_state: dict) -> None:
        """Upsert faction/location nodes from world_state."""
        if not self._enabled():
            return
        for faction in world_state.get("major_factions", []):
            await self.client.run_write(
                "MERGE (f:Faction {novel_id: $novel_id, name: $name})",
                {"novel_id": novel_id, "name": faction},
            )
        for loc in world_state.get("locations", []):
            loc_name = loc.get("name", "") if isinstance(loc, dict) else str(loc)
            loc_desc = loc.get("description", "") if isinstance(loc, dict) else ""
            await self.client.run_write(
                """
                MERGE (l:Location {novel_id: $novel_id, name: $name})
                SET l.description = $description
                """,
                {"novel_id": novel_id, "name": loc_name, "description": loc_desc},
            )

    # ---- Queries ----

    async def get_character_network(self, novel_id: int, depth: int = 2) -> dict:
        """Return character relationship subgraph."""
        if not self._enabled():
            return {"nodes": [], "edges": []}
        records = await self.client.run_read(
            """
            MATCH (c:Character {novel_id: $novel_id})-[r:RELATED_TO*1..$depth]-(other:Character {novel_id: $novel_id})
            RETURN DISTINCT c, r, other
            LIMIT 100
            """,
            {"novel_id": novel_id, "depth": depth},
        )
        # Simplified return — full graph data built by get_story_graph_data
        return {"raw": records}

    async def get_event_timeline(self, novel_id: int, limit: int = 50) -> list[dict]:
        """Return ordered event timeline."""
        if not self._enabled():
            return []
        records = await self.client.run_read(
            """
            MATCH (e:Event {novel_id: $novel_id})
            RETURN e.name AS name, e.chapter_id AS chapter_id, e.description AS description
            ORDER BY e.chapter_id
            LIMIT $limit
            """,
            {"novel_id": novel_id, "limit": limit},
        )
        return records

    async def get_story_graph_data(self, novel_id: int) -> dict:
        """Return complete graph data (nodes + edges) for frontend visualization."""
        if not self._enabled():
            return {"nodes": [], "edges": []}

        nodes = []
        edges = []

        # Characters
        char_records = await self.client.run_read(
            "MATCH (c:Character {novel_id: $novel_id}) RETURN c.name AS id, c.realm AS realm, c.personality AS personality",
            {"novel_id": novel_id},
        )
        for r in char_records:
            nodes.append({"id": r["id"], "label": r["id"], "node_type": "character",
                          "properties": {"realm": r.get("realm", ""), "personality": r.get("personality", [])}})

        # Character relations
        rel_records = await self.client.run_read(
            """
            MATCH (a:Character {novel_id: $novel_id})-[r:RELATED_TO]->(b:Character {novel_id: $novel_id})
            RETURN a.name AS source, b.name AS target, r.relation AS relation
            """,
            {"novel_id": novel_id},
        )
        for r in rel_records:
            edges.append({"source": r["source"], "target": r["target"],
                          "edge_type": r.get("relation", "related"), "properties": {}})

        # Events
        evt_records = await self.client.run_read(
            "MATCH (e:Event {novel_id: $novel_id}) RETURN e.name AS id, e.chapter_id AS chapter_id",
            {"novel_id": novel_id},
        )
        for r in evt_records:
            nodes.append({"id": r["id"], "label": r["id"], "node_type": "event",
                          "properties": {"chapter_id": r.get("chapter_id")}})

        # Factions
        fac_records = await self.client.run_read(
            "MATCH (f:Faction {novel_id: $novel_id}) RETURN f.name AS id",
            {"novel_id": novel_id},
        )
        for r in fac_records:
            nodes.append({"id": r["id"], "label": r["id"], "node_type": "faction", "properties": {}})

        # Locations
        loc_records = await self.client.run_read(
            "MATCH (l:Location {novel_id: $novel_id}) RETURN l.name AS id, l.description AS description",
            {"novel_id": novel_id},
        )
        for r in loc_records:
            nodes.append({"id": r["id"], "label": r["id"], "node_type": "location",
                          "properties": {"description": r.get("description", "")}})

        return {"nodes": nodes, "edges": edges}

    async def query_graph_for_context(self, novel_id: int, keyword: str) -> list[dict]:
        """Search graph nodes by keyword for context injection."""
        if not self._enabled():
            return []
        records = await self.client.run_read(
            """
            MATCH (n)
            WHERE (n:Character OR n:Event OR n:Faction) AND n.novel_id = $novel_id
              AND (n.name CONTAINS $keyword OR n.description CONTAINS $keyword)
            RETURN n.name AS name, labels(n) AS types, n.description AS description
            LIMIT 10
            """,
            {"novel_id": novel_id, "keyword": keyword},
        )
        return records


# Module-level singleton
story_graph_service = StoryGraphService()
