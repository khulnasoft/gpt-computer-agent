"""
RAG Module Init File

This module provides a complete RAG (Retrieval-Augmented Generation) system for Aideck,
including configuration, pipeline, and utilities.
"""

from .config import (
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

# Try to import pipeline components, but don't fail if dependencies are missing
try:
    from .pipeline import RAGPipeline, create_simple_rag, quick_search

    _PIPELINE_AVAILABLE = True
except ImportError:
    _PIPELINE_AVAILABLE = False

    # Create placeholder classes
    class RAGPipeline:
        def __init__(self, *args, **kwargs):
            raise ImportError(f"Pipeline not available: {e}")

    def create_simple_rag(*args, **kwargs):
        raise ImportError("Pipeline not available")

    def quick_search(*args, **kwargs):
        raise ImportError("Pipeline not available")


__all__ = [
    # Configuration classes
    "RAGConfig",
    "RAGLoaderConfig",
    "RAGChunkingConfig",
    "RAGEmbeddingConfig",
    "RAGVectorDBConfig",
    "RAGRetrievalConfig",
    # Pre-configured configs
    "get_simple_rag_config",
    "get_advanced_rag_config",
    "get_fast_rag_config",
    # Pipeline classes (may not be available)
    "RAGPipeline",
    "create_simple_rag",
    "quick_search",
]
