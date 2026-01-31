from .azure_openai_provider import AzureOpenAIEmbedding
from .base import EmbeddingConfig, EmbeddingMetrics, EmbeddingMode, EmbeddingProvider
from .bedrock_provider import BedrockEmbedding
from .factory import (
    auto_detect_best_embedding,
    create_azure_openai_embedding,
    create_bedrock_embedding,
    create_best_available_embedding,
    create_embedding_provider,
    create_fastembed_provider,
    create_gemini_embedding,
    create_gemini_vertex_embedding,
    create_huggingface_embedding,
    create_ollama_embedding,
    create_openai_embedding,
    get_embedding_recommendations,
    get_provider_info,
    list_available_providers,
)
from .fastembed_provider import FastEmbedProvider
from .gemini_provider import (
    GeminiEmbedding,
    GeminiEmbeddingConfig,
    create_gemini_cloud_embedding,
    create_gemini_document_embedding,
    create_gemini_query_embedding,
    create_gemini_semantic_embedding,
    create_gemini_vertex_embedding,
)
from .huggingface_provider import HuggingFaceEmbedding
from .ollama_provider import OllamaEmbedding
from .openai_provider import OpenAIEmbedding, OpenAIEmbeddingConfig

__all__ = [
    "EmbeddingProvider",
    "EmbeddingConfig",
    "EmbeddingMode",
    "EmbeddingMetrics",
    "OpenAIEmbedding",
    "OpenAIEmbeddingConfig",
    "AzureOpenAIEmbedding",
    "BedrockEmbedding",
    "HuggingFaceEmbedding",
    "FastEmbedProvider",
    "OllamaEmbedding",
    "GeminiEmbedding",
    "GeminiEmbeddingConfig",
    "create_embedding_provider",
    "list_available_providers",
    "get_provider_info",
    "create_best_available_embedding",
    "auto_detect_best_embedding",
    "get_embedding_recommendations",
    "create_openai_embedding",
    "create_azure_openai_embedding",
    "create_bedrock_embedding",
    "create_huggingface_embedding",
    "create_fastembed_provider",
    "create_ollama_embedding",
    "create_gemini_embedding",
    "create_gemini_vertex_embedding",
    "create_gemini_document_embedding",
    "create_gemini_query_embedding",
    "create_gemini_semantic_embedding",
    "create_gemini_cloud_embedding",
]

PROVIDER_REGISTRY = {
    "openai": OpenAIEmbedding,
    "azure_openai": AzureOpenAIEmbedding,
    "azure": AzureOpenAIEmbedding,
    "bedrock": BedrockEmbedding,
    "aws": BedrockEmbedding,
    "huggingface": HuggingFaceEmbedding,
    "hf": HuggingFaceEmbedding,
    "fastembed": FastEmbedProvider,
    "qdrant": FastEmbedProvider,
    "ollama": OllamaEmbedding,
    "gemini": GeminiEmbedding,
    "google": GeminiEmbedding,
}
