"""
RAG Pipeline Module

This module provides a complete RAG (Retrieval-Augmented Generation) pipeline that orchestrates
document loading, chunking, embedding, and retrieval for intelligent question answering.
"""

import logging
import time
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from ..embeddings.base import EmbeddingProvider
from ..embeddings.factory import create_embedding_provider
from ..loaders.base import BaseLoader
from ..loaders.factory import create_intelligent_loaders
from ..schemas.data_models import Chunk, Document, RAGSearchResult
from ..text_splitter.base import BaseChunker
from ..text_splitter.factory import create_intelligent_splitters
from ..vectordb import _get_provider_classes
from ..vectordb.base import BaseVectorDBProvider
from .config import RAGConfig, get_simple_rag_config

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    A comprehensive RAG pipeline for document processing and retrieval.

    This class provides a high-level interface for:
    1. Loading documents from various sources
    2. Chunking documents into manageable pieces
    3. Generating embeddings for chunks
    4. Storing embeddings in vector databases
    5. Retrieving relevant documents for queries
    6. Generating responses with retrieved context
    """

    def __init__(
        self,
        config: RAGConfig | None = None,
        sources: str | Path | list[str | Path] | None = None,
        **kwargs,
    ):
        """
        Initialize the RAG pipeline.

        Args:
            config: RAG configuration object. If None, uses simple config.
            sources: Document sources to process. Can be file paths, directories, or text content.
            **kwargs: Additional configuration overrides.
        """
        self.config = config or get_simple_rag_config()
        self.config.update_from_env()

        # Override config with kwargs
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Initialize components
        self.loaders: list[BaseLoader] = []
        self.chunkers: list[BaseChunker] = []
        self.embedding_provider: EmbeddingProvider | None = None
        self.vector_db: BaseVectorDBProvider | None = None

        # Processing state
        self.documents: list[Document] = []
        self.chunks: list[Chunk] = []
        self.is_initialized = False
        self.is_processed = False

        # Set up logging
        if self.config.enable_logging:
            logging.basicConfig(level=getattr(logging, self.config.log_level))

        # If sources provided, resolve them
        self.sources = []
        if sources:
            self.sources = self._resolve_sources(sources)

    def _resolve_sources(
        self, sources: str | Path | list[str | Path]
    ) -> list[str | Path]:
        """Resolve and normalize sources."""
        if isinstance(sources, (str, Path)):
            sources = [sources]

        resolved = []
        for source in sources:
            source_path = Path(source) if isinstance(source, str) else source

            # If it's a directory, get all supported files
            if source_path.is_dir():
                supported_extensions = {
                    ".txt",
                    ".md",
                    ".pdf",
                    ".docx",
                    ".csv",
                    ".json",
                    ".yaml",
                    ".yml",
                    ".html",
                    ".xml",
                }
                for ext in supported_extensions:
                    resolved.extend(source_path.rglob(f"*{ext}"))
            else:
                resolved.append(source_path)

        return resolved

    async def initialize(self) -> None:
        """Initialize all RAG components."""
        if self.is_initialized:
            return

        logger.info("🚀 Initializing RAG pipeline...")

        try:
            # Initialize embedding provider
            logger.info(
                f"📊 Initializing embedding provider: {self.config.embedding.provider}"
            )
            self.embedding_provider = create_embedding_provider(
                self.config.embedding.provider,
                **self.config.embedding.model_dump(exclude={"provider"}),
            )

            # Initialize vector database
            logger.info(
                f"🗄️ Initializing vector database: {self.config.vectordb.provider}"
            )
            provider_classes = _get_provider_classes()
            if self.config.vectordb.provider in provider_classes:
                vector_db_class = provider_classes[self.config.vectordb.provider]
                self.vector_db = vector_db_class(
                    **self.config.vectordb.model_dump(exclude={"provider"})
                )
            else:
                raise ValueError(
                    f"Unknown vector database provider: {self.config.vectordb.provider}"
                )

            # Initialize loaders if sources provided
            if self.sources:
                logger.info(
                    f"📚 Initializing loaders for {len(self.sources)} sources..."
                )
                self.loaders = create_intelligent_loaders(
                    self.sources, **self.config.loader.model_dump()
                )

                # Initialize chunkers
                logger.info("✂️ Initializing chunkers...")
                self.chunkers = create_intelligent_splitters(
                    self.sources,
                    use_case=self.config.use_case,
                    quality_preference=self.config.quality_preference,
                    **self.config.chunking.model_dump(),
                )

            self.is_initialized = True
            logger.info("✅ RAG pipeline initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG pipeline: {e}")
            raise

    async def add_documents(self, sources: str | Path | list[str | Path]) -> None:
        """Add new documents to the pipeline."""
        await self.initialize()

        new_sources = self._resolve_sources(sources)
        self.sources.extend(new_sources)

        # Create loaders for new sources
        new_loaders = create_intelligent_loaders(
            new_sources, **self.config.loader.model_dump()
        )
        self.loaders.extend(new_loaders)

        # Reset processed state
        self.is_processed = False

    async def process_documents(self) -> None:
        """Process all documents: load, chunk, and embed."""
        if not self.is_initialized:
            await self.initialize()

        if self.is_processed:
            logger.info("📄 Documents already processed")
            return

        if not self.sources:
            raise ValueError("No sources to process. Add documents first.")

        logger.info(f"🔄 Processing {len(self.sources)} documents...")
        start_time = time.time()

        try:
            # Load documents
            logger.info("📖 Loading documents...")
            self.documents = []
            for loader in self.loaders:
                if self.config.parallel_processing:
                    docs = await loader.abatch(self.sources)
                else:
                    docs = loader.batch(self.sources)
                self.documents.extend(docs)

            logger.info(f"✅ Loaded {len(self.documents)} documents")

            # Chunk documents
            logger.info("✂️ Chunking documents...")
            self.chunks = []
            for chunker in self.chunkers:
                for doc in self.documents:
                    if self.config.parallel_processing:
                        chunks = await chunker.adocuments([doc])
                    else:
                        chunks = chunker.documents([doc])
                    self.chunks.extend(chunks)

            logger.info(f"✅ Created {len(self.chunks)} chunks")

            # Generate embeddings
            logger.info("🔢 Generating embeddings...")
            texts = [chunk.content for chunk in self.chunks]

            if self.config.parallel_processing:
                embeddings = await self.embedding_provider.aembed_documents(texts)
            else:
                embeddings = self.embedding_provider.embed_documents(texts)

            # Update chunks with embeddings
            for chunk, embedding in zip(self.chunks, embeddings, strict=False):
                chunk.embedding = embedding

            # Store in vector database
            logger.info("💾 Storing embeddings in vector database...")
            await self.vector_db.aadd_documents(self.chunks)

            self.is_processed = True
            processing_time = time.time() - start_time
            logger.info(
                f"✅ Document processing completed in {processing_time:.2f} seconds"
            )

        except Exception as e:
            logger.error(f"❌ Failed to process documents: {e}")
            raise

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[RAGSearchResult]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity threshold
            filters: Metadata filters

        Returns:
            List of search results
        """
        if not self.is_processed:
            await self.process_documents()

        # Use config defaults if not provided
        top_k = top_k or self.config.retrieval.top_k
        similarity_threshold = (
            similarity_threshold or self.config.retrieval.similarity_threshold
        )
        filters = filters or self.config.retrieval.metadata_filters

        logger.info(f"🔍 Searching for: '{query}'")

        # Generate query embedding
        query_embedding = await self.embedding_provider.aembed_query(query)

        # Search vector database
        results = await self.vector_db.asimilarity_search(
            query_embedding,
            k=top_k,
            similarity_threshold=similarity_threshold,
            filters=filters,
        )

        logger.info(f"📋 Found {len(results)} results")
        return results

    async def generate_response(
        self,
        query: str,
        context: list[RAGSearchResult] | None = None,
        llm_provider: Any | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate a response using retrieved context.

        Args:
            query: User query
            context: Retrieved context (if None, will search)
            llm_provider: LLM provider for generation
            **kwargs: Additional generation parameters

        Returns:
            Generated response with metadata
        """
        if context is None:
            context = await self.search(query)

        if not context:
            return {
                "response": "I couldn't find relevant information to answer your question.",
                "sources": [],
                "confidence": 0.0,
            }

        # Format context
        context_text = "\n\n".join(
            [f"Document {i+1}:\n{result.content}" for i, result in enumerate(context)]
        )

        # Create prompt
        prompt = f"""Based on the following context, please answer the user's question.

Context:
{context_text}

Question: {query}

Please provide a comprehensive answer based on the provided context. If the context doesn't contain enough information to answer the question, please say so."""

        # Generate response (this would integrate with your LLM provider)
        # For now, return a formatted response with context
        return {
            "response": f"Based on the retrieved documents, here's what I found:\n\n{context_text[:500]}...",
            "sources": [
                {
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.score,
                }
                for result in context
            ],
            "confidence": sum(result.score for result in context) / len(context),
            "query": query,
            "context_used": len(context),
        }

    async def stream_search(
        self, query: str, **kwargs
    ) -> AsyncGenerator[RAGSearchResult, None]:
        """Stream search results as they become available."""
        results = await self.search(query, **kwargs)
        for result in results:
            yield result

    def get_statistics(self) -> dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "config": self.config.name,
            "sources_count": len(self.sources),
            "documents_count": len(self.documents),
            "chunks_count": len(self.chunks),
            "loaders_count": len(self.loaders),
            "chunkers_count": len(self.chunkers),
            "is_initialized": self.is_initialized,
            "is_processed": self.is_processed,
            "embedding_provider": self.config.embedding.provider,
            "vector_db_provider": self.config.vectordb.provider,
        }

    async def clear(self) -> None:
        """Clear all processed data."""
        if self.vector_db:
            await self.vector_db.aclear()

        self.documents = []
        self.chunks = []
        self.is_processed = False

        logger.info("🧹 Cleared all processed data")

    async def save_state(self, path: str | Path) -> None:
        """Save pipeline state to disk."""
        state = {
            "config": self.config.model_dump(),
            "sources": [str(s) for s in self.sources],
            "statistics": self.get_statistics(),
        }

        import json

        with open(path, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"💾 Saved pipeline state to {path}")

    @classmethod
    async def load_state(cls, path: str | Path) -> "RAGPipeline":
        """Load pipeline state from disk."""
        import json

        with open(path) as f:
            state = json.load(f)

        pipeline = cls(
            config=RAGConfig.from_dict(state["config"]), sources=state["sources"]
        )

        await pipeline.initialize()
        logger.info(f"📂 Loaded pipeline state from {path}")

        return pipeline


# Convenience functions for quick usage
async def create_simple_rag(
    sources: str | Path | list[str | Path], **kwargs
) -> RAGPipeline:
    """Create a simple RAG pipeline with default configuration."""
    pipeline = RAGPipeline(config=get_simple_rag_config(), sources=sources, **kwargs)
    await pipeline.process_documents()
    return pipeline


async def quick_search(
    query: str, sources: str | Path | list[str | Path], top_k: int = 5
) -> list[RAGSearchResult]:
    """Quick search without creating a full pipeline."""
    pipeline = await create_simple_rag(sources)
    return await pipeline.search(query, top_k=top_k)
