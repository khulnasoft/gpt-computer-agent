"""
Tests for RAG Pipeline
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from aideck.rag.config import get_simple_rag_config
from aideck.rag.pipeline import RAGPipeline, create_simple_rag, quick_search
from aideck.schemas.data_models import Chunk, Document, RAGSearchResult


class TestRAGPipeline:
    """Test RAG pipeline functionality."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample RAG configuration."""
        return get_simple_rag_config()

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing."""
        return [
            Document(
                content="This is a test document about artificial intelligence.",
                metadata={"source": "test1.txt", "type": "text"},
            ),
            Document(
                content="Machine learning is a subset of artificial intelligence.",
                metadata={"source": "test2.txt", "type": "text"},
            ),
        ]

    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing."""
        return [
            Chunk(
                content="This is a test document about artificial intelligence.",
                metadata={"source": "test1.txt", "chunk_id": 0},
                embedding=[0.1, 0.2, 0.3],
            ),
            Chunk(
                content="Machine learning is a subset of artificial intelligence.",
                metadata={"source": "test2.txt", "chunk_id": 0},
                embedding=[0.2, 0.3, 0.4],
            ),
        ]

    def test_pipeline_initialization(self, sample_config):
        """Test pipeline initialization."""
        pipeline = RAGPipeline(config=sample_config)

        assert pipeline.config == sample_config
        assert pipeline.is_initialized is False
        assert pipeline.is_processed is False
        assert len(pipeline.sources) == 0

    def test_pipeline_with_sources(self, sample_config):
        """Test pipeline initialization with sources."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")

            pipeline = RAGPipeline(config=sample_config, sources=[test_file])

            assert len(pipeline.sources) == 1
            assert str(pipeline.sources[0]) == str(test_file)

    def test_resolve_sources(self, sample_config):
        """Test source resolution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test1.txt").write_text("Content 1")
            (temp_path / "test2.md").write_text("Content 2")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "test3.txt").write_text("Content 3")

            pipeline = RAGPipeline(config=sample_config)

            # Test single file
            sources = pipeline._resolve_sources(temp_path / "test1.txt")
            assert len(sources) == 1

            # Test directory
            sources = pipeline._resolve_sources(temp_path)
            assert len(sources) >= 3  # Should find all supported files

    @pytest.mark.asyncio
    async def test_initialize(self, sample_config):
        """Test pipeline initialization."""
        with patch("aideck.rag.pipeline.create_embedding_provider") as mock_embedding:
            with patch("aideck.rag.pipeline._get_provider_classes") as mock_vectordb:
                # Mock embedding provider
                mock_embedding.return_value = Mock()

                # Mock vector database
                mock_vectordb.return_value = {"chroma": Mock()}

                pipeline = RAGPipeline(config=sample_config)
                await pipeline.initialize()

                assert pipeline.is_initialized is True
                assert pipeline.embedding_provider is not None
                assert pipeline.vector_db is not None

    @pytest.mark.asyncio
    async def test_add_documents(self, sample_config):
        """Test adding documents to pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "new_test.txt"
            test_file.write_text("New content")

            pipeline = RAGPipeline(config=sample_config)

            # Mock initialization
            pipeline.is_initialized = True
            pipeline.loaders = []
            pipeline.chunkers = []

            with patch(
                "aideck.rag.pipeline.create_intelligent_loaders"
            ) as mock_loaders:
                with patch(
                    "aideck.rag.pipeline.create_intelligent_splitters"
                ) as mock_chunkers:
                    mock_loaders.return_value = [Mock()]
                    mock_chunkers.return_value = [Mock()]

                    await pipeline.add_documents([test_file])

                    assert len(pipeline.sources) == 1
                    assert pipeline.is_processed is False

    @pytest.mark.asyncio
    async def test_process_documents(
        self, sample_config, sample_documents, sample_chunks
    ):
        """Test document processing."""
        pipeline = RAGPipeline(config=sample_config)

        # Mock components
        mock_loader = Mock()
        mock_loader.batch.return_value = sample_documents
        mock_loader.abatch.return_value = sample_documents

        mock_chunker = Mock()
        mock_chunker.documents.return_value = sample_chunks
        mock_chunker.adocuments.return_value = sample_chunks

        mock_embedding_provider = Mock()
        mock_embedding_provider.embed_documents.return_value = [
            [0.1, 0.2, 0.3],
            [0.2, 0.3, 0.4],
        ]
        mock_embedding_provider.aembed_documents.return_value = [
            [0.1, 0.2, 0.3],
            [0.2, 0.3, 0.4],
        ]

        mock_vectordb = Mock()
        mock_vectordb.aadd_documents = AsyncMock()

        # Set up pipeline
        pipeline.is_initialized = True
        pipeline.sources = ["test.txt"]
        pipeline.loaders = [mock_loader]
        pipeline.chunkers = [mock_chunker]
        pipeline.embedding_provider = mock_embedding_provider
        pipeline.vector_db = mock_vectordb

        await pipeline.process_documents()

        assert pipeline.is_processed is True
        assert len(pipeline.documents) == 2
        assert len(pipeline.chunks) == 2
        mock_vectordb.aadd_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_search(self, sample_config, sample_chunks):
        """Test document search."""
        pipeline = RAGPipeline(config=sample_config)

        # Mock components
        mock_embedding_provider = Mock()
        mock_embedding_provider.aembed_query.return_value = [0.1, 0.2, 0.3]

        mock_vectordb = Mock()
        mock_results = [
            RAGSearchResult(
                content="Test result", metadata={"source": "test.txt"}, score=0.8
            )
        ]
        mock_vectordb.asimilarity_search.return_value = mock_results

        # Set up pipeline
        pipeline.is_processed = True
        pipeline.embedding_provider = mock_embedding_provider
        pipeline.vector_db = mock_vectordb

        results = await pipeline.search("test query")

        assert len(results) == 1
        assert results[0].content == "Test result"
        assert results[0].score == 0.8

    @pytest.mark.asyncio
    async def test_generate_response(self, sample_config):
        """Test response generation."""
        pipeline = RAGPipeline(config=sample_config)

        # Mock search results
        mock_results = [
            RAGSearchResult(
                content="AI is a field of computer science.",
                metadata={"source": "test.txt"},
                score=0.9,
            )
        ]

        response = await pipeline.generate_response("What is AI?", context=mock_results)

        assert "response" in response
        assert "sources" in response
        assert "confidence" in response
        assert len(response["sources"]) == 1
        assert response["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_stream_search(self, sample_config, sample_chunks):
        """Test streaming search."""
        pipeline = RAGPipeline(config=sample_config)

        # Mock components
        mock_embedding_provider = Mock()
        mock_embedding_provider.aembed_query.return_value = [0.1, 0.2, 0.3]

        mock_vectordb = Mock()
        mock_results = [
            RAGSearchResult(content="Result 1", metadata={}, score=0.8),
            RAGSearchResult(content="Result 2", metadata={}, score=0.7),
        ]
        mock_vectordb.asimilarity_search.return_value = mock_results

        # Set up pipeline
        pipeline.is_processed = True
        pipeline.embedding_provider = mock_embedding_provider
        pipeline.vector_db = mock_vectordb

        results = []
        async for result in pipeline.stream_search("test query"):
            results.append(result)

        assert len(results) == 2
        assert results[0].content == "Result 1"
        assert results[1].content == "Result 2"

    def test_get_statistics(self, sample_config):
        """Test getting pipeline statistics."""
        pipeline = RAGPipeline(config=sample_config)
        pipeline.sources = ["test1.txt", "test2.txt"]
        pipeline.documents = [Mock(), Mock(), Mock()]
        pipeline.chunks = [Mock(), Mock(), Mock(), Mock(), Mock()]
        pipeline.loaders = [Mock(), Mock()]
        pipeline.chunkers = [Mock]
        pipeline.is_initialized = True
        pipeline.is_processed = True

        stats = pipeline.get_statistics()

        assert stats["sources_count"] == 2
        assert stats["documents_count"] == 3
        assert stats["chunks_count"] == 5
        assert stats["loaders_count"] == 2
        assert stats["chunkers_count"] == 1
        assert stats["is_initialized"] is True
        assert stats["is_processed"] is True

    @pytest.mark.asyncio
    async def test_clear(self, sample_config):
        """Test clearing pipeline data."""
        pipeline = RAGPipeline(config=sample_config)

        # Mock vector database
        mock_vectordb = Mock()
        mock_vectordb.aclear = AsyncMock()

        pipeline.documents = [Mock(), Mock()]
        pipeline.chunks = [Mock(), Mock(), Mock()]
        pipeline.vector_db = mock_vectordb
        pipeline.is_processed = True

        await pipeline.clear()

        assert len(pipeline.documents) == 0
        assert len(pipeline.chunks) == 0
        assert pipeline.is_processed is False
        mock_vectordb.aclear.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_and_load_state(self, sample_config):
        """Test saving and loading pipeline state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "pipeline_state.json"

            # Create pipeline with sources
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")

            pipeline = RAGPipeline(config=sample_config, sources=[test_file])

            # Mock initialization
            pipeline.is_initialized = True

            await pipeline.save_state(state_file)
            assert state_file.exists()

            # Load state
            with patch("src.aideck.rag.pipeline.RAGPipeline.initialize") as mock_init:
                mock_init.return_value = None

                loaded_pipeline = await RAGPipeline.load_state(state_file)

                assert loaded_pipeline.config.name == pipeline.config.name
                assert len(loaded_pipeline.sources) == 1
                mock_init.assert_called_once()


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_create_simple_rag(self):
        """Test creating simple RAG pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")

            with patch(
                "src.aideck.rag.pipeline.RAGPipeline.process_documents"
            ) as mock_process:
                mock_process.return_value = None

                pipeline = await create_simple_rag([test_file])

                assert pipeline.config.name == "simple_rag"
                mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_quick_search(self):
        """Test quick search function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Test content")

            with patch("aideck.rag.pipeline.create_simple_rag") as mock_create:
                mock_pipeline = Mock()
                mock_pipeline.search.return_value = [
                    RAGSearchResult(content="Result", metadata={}, score=0.8)
                ]
                mock_create.return_value = mock_pipeline

                results = await quick_search("test query", [test_file])

                assert len(results) == 1
                assert results[0].content == "Result"
                mock_create.assert_called_once_with([test_file])
