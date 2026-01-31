"""
Simple tests for RAG Configuration without heavy dependencies.
"""

# Test the config directly without importing the pipeline
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "src")

from aideck.rag.config import (
    RAGChunkingConfig,
    RAGConfig,
    RAGEmbeddingConfig,
    RAGLoaderConfig,
    RAGRetrievalConfig,
    RAGVectorDBConfig,
    get_advanced_rag_config,
    get_fast_rag_config,
    get_simple_rag_config,
)


class TestRAGLoaderConfig:
    """Test RAG loader configuration."""

    def test_default_config(self):
        """Test default loader configuration."""
        config = RAGLoaderConfig()

        assert config.encoding == "utf-8"
        assert config.auto_detect_encoding is True
        assert config.extract_images is False
        assert config.preserve_layout is True
        assert config.delimiter == ","
        assert config.metadata_extraction is True

    def test_custom_config(self):
        """Test custom loader configuration."""
        config = RAGLoaderConfig(
            encoding="utf-16", extract_images=True, delimiter=";", has_header=False
        )

        assert config.encoding == "utf-16"
        assert config.extract_images is True
        assert config.delimiter == ";"
        assert config.has_header is False


class TestRAGChunkingConfig:
    """Test RAG chunking configuration."""

    def test_default_config(self):
        """Test default chunking configuration."""
        config = RAGChunkingConfig()

        assert config.chunk_size == 1024
        assert config.chunk_overlap == 200
        assert config.min_chunk_size == 100
        assert config.strategy == "recursive"
        assert config.respect_sentence_boundary is True

    def test_custom_config(self):
        """Test custom chunking configuration."""
        config = RAGChunkingConfig(
            chunk_size=512,
            chunk_overlap=50,
            strategy="semantic",
            semantic_threshold=0.8,
        )

        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.strategy == "semantic"
        assert config.semantic_threshold == 0.8


class TestRAGEmbeddingConfig:
    """Test RAG embedding configuration."""

    def test_default_config(self):
        """Test default embedding configuration."""
        config = RAGEmbeddingConfig()

        assert config.provider == "openai"
        assert config.batch_size == 32
        assert config.max_retries == 3
        assert config.cache_embeddings is True

    def test_custom_config(self):
        """Test custom embedding configuration."""
        config = RAGEmbeddingConfig(
            provider="huggingface",
            model_name="all-MiniLM-L6-v2",
            device="cpu",
            batch_size=16,
        )

        assert config.provider == "huggingface"
        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.device == "cpu"
        assert config.batch_size == 16


class TestRAGVectorDBConfig:
    """Test RAG vector database configuration."""

    def test_default_config(self):
        """Test default vector database configuration."""
        config = RAGVectorDBConfig()

        assert config.provider == "chroma"
        assert config.database_name == "aideck_rag"
        assert config.index_type == "hnsw"
        assert config.distance_metric == "cosine"
        assert config.persist_directory == "./data/vectordb"

    def test_custom_config(self):
        """Test custom vector database configuration."""
        config = RAGVectorDBConfig(
            provider="pinecone",
            host="api.pinecone.io",
            port=443,
            api_key="test-key",
            index_type="ivf",
        )

        assert config.provider == "pinecone"
        assert config.host == "api.pinecone.io"
        assert config.port == 443
        assert config.api_key == "test-key"
        assert config.index_type == "ivf"


class TestRAGRetrievalConfig:
    """Test RAG retrieval configuration."""

    def test_default_config(self):
        """Test default retrieval configuration."""
        config = RAGRetrievalConfig()

        assert config.top_k == 5
        assert config.similarity_threshold == 0.7
        assert config.enable_reranking is False
        assert config.enable_hybrid_search is False

    def test_custom_config(self):
        """Test custom retrieval configuration."""
        config = RAGRetrievalConfig(
            top_k=10,
            similarity_threshold=0.8,
            enable_reranking=True,
            enable_hybrid_search=True,
            keyword_weight=0.4,
        )

        assert config.top_k == 10
        assert config.similarity_threshold == 0.8
        assert config.enable_reranking is True
        assert config.enable_hybrid_search is True
        assert config.keyword_weight == 0.4


class TestRAGConfig:
    """Test main RAG configuration."""

    def test_default_config(self):
        """Test default RAG configuration."""
        config = RAGConfig()

        assert config.name == "aideck_rag"
        assert config.use_case == "rag_retrieval"
        assert config.quality_preference == "balanced"
        assert config.parallel_processing is True
        assert config.max_workers == 4

    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "name": "test_rag",
            "chunking": {"chunk_size": 512, "strategy": "semantic"},
            "embedding": {"provider": "huggingface"},
        }

        config = RAGConfig.from_dict(config_dict)

        assert config.name == "test_rag"
        assert config.chunking.chunk_size == 512
        assert config.chunking.strategy == "semantic"
        assert config.embedding.provider == "huggingface"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = RAGConfig(name="test_rag")
        config_dict = config.to_dict()

        assert config_dict["name"] == "test_rag"
        assert "chunking" in config_dict
        assert "embedding" in config_dict
        assert "vectordb" in config_dict

    def test_file_operations(self):
        """Test saving and loading configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test JSON
            json_path = Path(temp_dir) / "config.json"

            config = RAGConfig(name="test_rag")
            config.save_to_file(json_path)

            assert json_path.exists()

            loaded_config = RAGConfig.from_file(json_path)
            assert loaded_config.name == "test_rag"

            # Test YAML
            yaml_path = Path(temp_dir) / "config.yaml"
            config.save_to_file(yaml_path)

            assert yaml_path.exists()

            loaded_config = RAGConfig.from_file(yaml_path)
            assert loaded_config.name == "test_rag"


class TestPredefinedConfigs:
    """Test predefined configurations."""

    def test_simple_rag_config(self):
        """Test simple RAG configuration."""
        config = get_simple_rag_config()

        assert config.name == "simple_rag"
        assert config.chunking.chunk_size == 512
        assert config.chunking.strategy == "recursive"
        assert config.embedding.provider == "openai"
        assert config.vectordb.provider == "chroma"
        assert config.retrieval.top_k == 3

    def test_advanced_rag_config(self):
        """Test advanced RAG configuration."""
        config = get_advanced_rag_config()

        assert config.name == "advanced_rag"
        assert config.chunking.chunk_size == 1024
        assert config.chunking.strategy == "semantic"
        assert config.retrieval.enable_reranking is True
        assert config.retrieval.enable_hybrid_search is True
        assert config.parallel_processing is True
        assert config.max_workers == 8

    def test_fast_rag_config(self):
        """Test fast RAG configuration."""
        config = get_fast_rag_config()

        assert config.name == "fast_rag"
        assert config.chunking.chunk_size == 256
        assert config.chunking.strategy == "character"
        assert config.embedding.provider == "fastembed"
        assert config.vectordb.provider == "faiss"
        assert config.quality_preference == "fast"
