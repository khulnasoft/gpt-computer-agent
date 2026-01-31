"""
RAG Configuration Module

This module provides comprehensive configuration management for RAG (Retrieval-Augmented Generation) systems,
including loaders, chunkers, embeddings, and vector databases.
"""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class RAGLoaderConfig(BaseModel):
    """Configuration for document loaders in RAG pipeline."""

    # Text processing options
    encoding: str = Field(default="utf-8", description="Text encoding for file loading")
    auto_detect_encoding: bool = Field(
        default=True, description="Auto-detect file encoding"
    )

    # PDF specific
    extract_images: bool = Field(default=False, description="Extract images from PDFs")
    preserve_layout: bool = Field(default=True, description="Preserve PDF layout")

    # CSV specific
    delimiter: str = Field(default=",", description="CSV delimiter")
    quote_char: str = Field(default='"', description="CSV quote character")
    has_header: bool = Field(default=True, description="CSV has header row")

    # HTML specific
    extract_links: bool = Field(default=True, description="Extract links from HTML")
    extract_images: bool = Field(default=False, description="Extract images from HTML")
    clean_html: bool = Field(default=True, description="Clean HTML tags")

    # General options
    metadata_extraction: bool = Field(
        default=True, description="Extract metadata from documents"
    )
    chunk_metadata: bool = Field(default=True, description="Add chunk-level metadata")


class RAGChunkingConfig(BaseModel):
    """Configuration for text chunking strategies."""

    # Basic chunking parameters
    chunk_size: int = Field(default=1024, description="Target chunk size in characters")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    min_chunk_size: int | None = Field(default=100, description="Minimum chunk size")

    # Strategy selection
    strategy: str = Field(
        default="recursive",
        description="Chunking strategy: recursive, character, semantic, markdown, html, json, python",
    )

    # Advanced options
    semantic_threshold: float = Field(
        default=0.7, description="Semantic similarity threshold"
    )
    respect_sentence_boundary: bool = Field(
        default=True, description="Respect sentence boundaries"
    )
    respect_paragraph_boundary: bool = Field(
        default=True, description="Respect paragraph boundaries"
    )

    # Content type specific
    markdown_headers: bool = Field(
        default=True, description="Split on markdown headers"
    )
    html_tags: list[str] = Field(
        default=["p", "div", "section"], description="HTML tags to split on"
    )
    json_objects: bool = Field(default=True, description="Split on JSON objects")
    python_functions: bool = Field(
        default=True, description="Split on Python functions"
    )


class RAGEmbeddingConfig(BaseModel):
    """Configuration for embedding providers."""

    # Provider selection
    provider: str = Field(
        default="openai",
        description="Embedding provider: openai, azure_openai, huggingface, fastembed, ollama, gemini",
    )

    # Model configuration
    model_name: str | None = Field(default=None, description="Specific model name")
    dimension: int | None = Field(default=None, description="Embedding dimension")

    # OpenAI/Azure specific
    api_key: str | None = Field(default=None, description="API key for cloud providers")
    api_base: str | None = Field(default=None, description="API base URL")
    deployment_name: str | None = Field(
        default=None, description="Azure deployment name"
    )

    # HuggingFace specific
    device: str = Field(default="auto", description="Device: auto, cpu, cuda")
    model_kwargs: dict[str, Any] = Field(
        default_factory=dict, description="Model kwargs"
    )

    # Batch processing
    batch_size: int = Field(
        default=32, description="Batch size for embedding generation"
    )
    max_retries: int = Field(
        default=3, description="Maximum retries for failed requests"
    )

    # Caching
    cache_embeddings: bool = Field(default=True, description="Cache embeddings locally")
    cache_dir: str | None = Field(default=None, description="Cache directory")


class RAGVectorDBConfig(BaseModel):
    """Configuration for vector database providers."""

    # Provider selection
    provider: str = Field(
        default="chroma",
        description="Vector DB provider: chroma, faiss, pinecone, qdrant, milvus, weaviate, pgvector",
    )

    # Connection settings
    host: str | None = Field(default=None, description="Database host")
    port: int | None = Field(default=None, description="Database port")
    database_name: str = Field(
        default="aideck_rag", description="Database/collection name"
    )

    # Authentication
    api_key: str | None = Field(default=None, description="API key for cloud providers")
    username: str | None = Field(default=None, description="Username")
    password: str | None = Field(default=None, description="Password")

    # Index configuration
    index_type: str = Field(default="hnsw", description="Index type: hnsw, ivf, flat")
    distance_metric: str = Field(
        default="cosine", description="Distance metric: cosine, euclidean, manhattan"
    )

    # Performance settings
    ef_construction: int = Field(
        default=200, description="HNSW ef_construction parameter"
    )
    ef_search: int = Field(default=50, description="HNSW ef_search parameter")
    max_connections: int = Field(
        default=16, description="HNSW max_connections parameter"
    )

    # Local storage
    persist_directory: str | None = Field(
        default="./data/vectordb", description="Local persistence directory"
    )


class RAGRetrievalConfig(BaseModel):
    """Configuration for retrieval and search."""

    # Search parameters
    top_k: int = Field(default=5, description="Number of documents to retrieve")
    similarity_threshold: float = Field(
        default=0.7, description="Minimum similarity threshold"
    )

    # Reranking
    enable_reranking: bool = Field(default=False, description="Enable result reranking")
    reranker_model: str | None = Field(default=None, description="Reranker model name")
    rerank_top_k: int = Field(default=10, description="Number of docs to rerank")

    # Filtering
    metadata_filters: dict[str, Any] = Field(
        default_factory=dict, description="Metadata filters"
    )
    date_range_filter: dict[str, str] | None = Field(
        default=None, description="Date range filter"
    )

    # Hybrid search
    enable_hybrid_search: bool = Field(
        default=False, description="Enable hybrid vector+keyword search"
    )
    keyword_weight: float = Field(
        default=0.3, description="Weight for keyword search in hybrid"
    )

    # Diversity
    enable_diversity: bool = Field(default=False, description="Enable diverse results")
    diversity_threshold: float = Field(default=0.8, description="Diversity threshold")


class RAGConfig(BaseModel):
    """Complete RAG system configuration."""

    # Basic configuration
    name: str = Field(default="aideck_rag", description="RAG system name")
    description: str | None = Field(default=None, description="RAG system description")

    # Component configurations
    loader: RAGLoaderConfig = Field(default_factory=RAGLoaderConfig)
    chunking: RAGChunkingConfig = Field(default_factory=RAGChunkingConfig)
    embedding: RAGEmbeddingConfig = Field(default_factory=RAGEmbeddingConfig)
    vectordb: RAGVectorDBConfig = Field(default_factory=RAGVectorDBConfig)
    retrieval: RAGRetrievalConfig = Field(default_factory=RAGRetrievalConfig)

    # System settings
    use_case: str = Field(
        default="rag_retrieval",
        description="Use case: rag_retrieval, semantic_search, qa",
    )
    quality_preference: str = Field(
        default="balanced", description="Quality preference: fast, balanced, quality"
    )

    # Processing settings
    parallel_processing: bool = Field(
        default=True, description="Enable parallel processing"
    )
    max_workers: int = Field(default=4, description="Maximum number of worker threads")
    chunk_batch_size: int = Field(
        default=100, description="Batch size for chunk processing"
    )

    # Storage and caching
    cache_dir: str = Field(default="./data/cache", description="Cache directory")
    persist_processed_data: bool = Field(
        default=True, description="Persist processed data"
    )

    # Monitoring and logging
    enable_logging: bool = Field(default=True, description="Enable detailed logging")
    log_level: str = Field(default="INFO", description="Log level")
    enable_metrics: bool = Field(
        default=False, description="Enable performance metrics"
    )

    class Config:
        extra = "allow"

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "RAGConfig":
        """Create RAGConfig from dictionary."""
        return cls(**config_dict)

    @classmethod
    def from_file(cls, config_path: str | Path) -> "RAGConfig":
        """Load RAGConfig from JSON or YAML file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        if config_path.suffix.lower() in [".yaml", ".yml"]:
            import yaml

            with open(config_path) as f:
                config_dict = yaml.safe_load(f)
        elif config_path.suffix.lower() == ".json":
            import json

            with open(config_path) as f:
                config_dict = json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

        return cls.from_dict(config_dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert RAGConfig to dictionary."""
        return self.model_dump()

    def save_to_file(self, config_path: str | Path) -> None:
        """Save RAGConfig to JSON or YAML file."""
        config_path = Path(config_path)
        config_dict = self.to_dict()

        if config_path.suffix.lower() in [".yaml", ".yml"]:
            import yaml

            with open(config_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        elif config_path.suffix.lower() == ".json":
            import json

            with open(config_path, "w") as f:
                json.dump(config_dict, f, indent=2)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

    def update_from_env(self) -> "RAGConfig":
        """Update configuration from environment variables."""
        # Update embedding config from env
        if os.getenv("OPENAI_API_KEY"):
            self.embedding.api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("AZURE_OPENAI_API_KEY"):
            self.embedding.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if os.getenv("AZURE_OPENAI_ENDPOINT"):
            self.embedding.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")

        # Update vector DB config from env
        if os.getenv("PINECONE_API_KEY"):
            self.vectordb.api_key = os.getenv("PINECONE_API_KEY")
        if os.getenv("QDRANT_URL"):
            self.vectordb.host = os.getenv("QDRANT_URL")

        return self


# Pre-configured RAG configurations for common use cases
def get_simple_rag_config() -> RAGConfig:
    """Get a simple RAG configuration for quick start."""
    return RAGConfig(
        name="simple_rag",
        chunking=RAGChunkingConfig(
            chunk_size=512, chunk_overlap=50, strategy="recursive"
        ),
        embedding=RAGEmbeddingConfig(
            provider="openai", model_name="text-embedding-3-small"
        ),
        vectordb=RAGVectorDBConfig(
            provider="chroma", persist_directory="./data/simple_rag"
        ),
        retrieval=RAGRetrievalConfig(top_k=3, similarity_threshold=0.7),
    )


def get_advanced_rag_config() -> RAGConfig:
    """Get an advanced RAG configuration with all features enabled."""
    return RAGConfig(
        name="advanced_rag",
        chunking=RAGChunkingConfig(
            chunk_size=1024,
            chunk_overlap=200,
            strategy="semantic",
            semantic_threshold=0.7,
            respect_sentence_boundary=True,
            respect_paragraph_boundary=True,
        ),
        embedding=RAGEmbeddingConfig(
            provider="openai",
            model_name="text-embedding-3-large",
            batch_size=32,
            cache_embeddings=True,
        ),
        vectordb=RAGVectorDBConfig(
            provider="chroma",
            index_type="hnsw",
            distance_metric="cosine",
            ef_construction=200,
            ef_search=50,
        ),
        retrieval=RAGRetrievalConfig(
            top_k=10,
            similarity_threshold=0.8,
            enable_reranking=True,
            enable_hybrid_search=True,
            enable_diversity=True,
        ),
        parallel_processing=True,
        max_workers=8,
    )


def get_fast_rag_config() -> RAGConfig:
    """Get a fast RAG configuration optimized for speed."""
    return RAGConfig(
        name="fast_rag",
        chunking=RAGChunkingConfig(
            chunk_size=256, chunk_overlap=25, strategy="character"
        ),
        embedding=RAGEmbeddingConfig(
            provider="fastembed", model_name="all-MiniLM-L6-v2", batch_size=64
        ),
        vectordb=RAGVectorDBConfig(provider="faiss", index_type="flat"),
        retrieval=RAGRetrievalConfig(top_k=5, similarity_threshold=0.6),
        quality_preference="fast",
        parallel_processing=True,
        max_workers=4,
    )
