from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://novel_writer:novel_write_2024@localhost:5432/novel_write"
    redis_url: str = "redis://:redis_write_2024@localhost:6379"
    llm_gateway_url: str = "http://localhost:8001"

    context_max_chars: int = 4000
    continuation_target_chars: int = 400

    # V2: ChromaDB vector store
    chroma_host: str = "localhost"
    chroma_port: int = 8002

    # V2: Embedding model
    embedding_model: str = "dashscope/text-embedding-v4"
    embedding_dimension: int = 1024

    # V4: Neo4j graph database
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "novel_write_2024"
    neo4j_database: str = "neo4j"

    # V4: Redis cache TTL
    redis_cache_ttl: int = 3600

    # V4: Feature flags
    feature_neo4j_enabled: bool = True
    feature_v4_enabled: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
