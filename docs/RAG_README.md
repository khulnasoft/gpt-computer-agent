# Aideck RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system for intelligent document processing, embedding, and retrieval.

## 🚀 Features

### 📚 File Loaders
Support for multiple document formats:
- **Text files** (.txt, .md)
- **PDF documents** (.pdf)
- **Word documents** (.docx)
- **Spreadsheets** (.csv)
- **Structured data** (.json, .yaml, .xml)
- **Web content** (.html)

### ✂️ Chunking Strategies
Multiple text splitting strategies:
- **Recursive** - Intelligent recursive splitting
- **Character** - Fixed-size character chunks
- **Semantic** - Semantic similarity-based splitting
- **Markdown** - Header and structure-aware splitting
- **HTML** - Tag-aware splitting
- **JSON** - Object and array-aware splitting
- **Python** - Function and class-aware splitting

### 🧠 Embedding Providers
Support for multiple embedding providers:
- **OpenAI** - GPT embeddings (text-embedding-3-small, text-embedding-3-large)
- **Azure OpenAI** - Azure-hosted OpenAI embeddings
- **HuggingFace** - Open source transformer models
- **FastEmbed** - Fast local embeddings
- **Ollama** - Local Ollama embeddings
- **Gemini** - Google Gemini embeddings

### 🗄️ Vector Databases
Integration with multiple vector databases:
- **Chroma** - Open-source vector database
- **FAISS** - Facebook AI Similarity Search
- **Pinecone** - Managed vector database service
- **Qdrant** - Vector similarity search engine
- **Milvus** - Open-source vector database
- **Weaviate** - Knowledge graph-based vector database
- **PGVector** - PostgreSQL vector extension

### 🔍 Advanced Retrieval
- **Similarity search** with configurable thresholds
- **Hybrid search** (vector + keyword)
- **Result reranking** for better relevance
- **Diverse result selection**
- **Metadata filtering**
- **Date range filtering**

## 📦 Installation

```bash
# Install with RAG dependencies
pip install aideck[rag]

# Or install specific dependencies
pip install aideck
pip install chromadb fastembed openai
```

## 🎯 Quick Start

### Basic Usage

```python
import asyncio
from aideck.rag import RAGPipeline, get_simple_rag_config

async def main():
    # Create RAG pipeline with simple configuration
    config = get_simple_rag_config()
    pipeline = RAGPipeline(
        config=config,
        sources=["./documents/"]  # Directory with documents
    )

    # Process documents
    await pipeline.process_documents()

    # Search for relevant information
    results = await pipeline.search("What is artificial intelligence?")

    # Generate response with context
    response = await pipeline.generate_response("Explain AI in simple terms")
    print(response["response"])

asyncio.run(main())
```

### Quick Search

```python
from aideck.rag import quick_search

async def search_documents():
    results = await quick_search(
        "machine learning concepts",
        sources=["./ml_docs/", "./ai_papers.pdf"],
        top_k=5
    )

    for result in results:
        print(f"Score: {result.score:.3f}")
        print(f"Content: {result.content[:200]}...")

asyncio.run(search_documents())
```

## ⚙️ Configuration

### Simple Configuration

```python
from aideck.rag import get_simple_rag_config

config = get_simple_rag_config()
# Uses:
# - Recursive chunking (512 chars)
# - OpenAI embeddings
# - Chroma vector database
# - Basic similarity search
```

### Advanced Configuration

```python
from aideck.rag import get_advanced_rag_config

config = get_advanced_rag_config()
# Uses:
# - Semantic chunking (1024 chars)
# - OpenAI embeddings (large model)
# - Chroma with HNSW indexing
# - Reranking and hybrid search
```

### Custom Configuration

```python
from aideck.rag import RAGConfig

config = RAGConfig(
    name="my_rag_system",
    chunking={
        "chunk_size": 800,
        "chunk_overlap": 200,
        "strategy": "semantic"
    },
    embedding={
        "provider": "huggingface",
        "model_name": "all-MiniLM-L6-v2",
        "device": "cpu"
    },
    vectordb={
        "provider": "chroma",
        "persist_directory": "./my_vectordb"
    },
    retrieval={
        "top_k": 10,
        "similarity_threshold": 0.8,
        "enable_reranking": True
    }
)
```

### Configuration from File

```python
from aideck.rag import RAGConfig

# Load from JSON
config = RAGConfig.from_file("rag_config.json")

# Save configuration
config.save_to_file("my_config.yaml")
```

## 🔧 Environment Variables

Set up environment variables for cloud providers:

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export AZURE_OPENAI_ENDPOINT="your-azure-endpoint"

# Pinecone
export PINECONE_API_KEY="your-pinecone-api-key"

# Qdrant
export QDRANT_URL="your-qdrant-url"
```

## 📊 Examples

### Document Processing

```python
from aideck.rag import RAGPipeline

async def process_documents():
    pipeline = RAGPipeline(
        sources=[
            "./research_papers/",
            "./documentation.pdf",
            "./web_content.html"
        ]
    )

    await pipeline.process_documents()

    # Get statistics
    stats = pipeline.get_statistics()
    print(f"Processed {stats['documents_count']} documents")
    print(f"Created {stats['chunks_count']} chunks")
```

### Advanced Search

```python
async def advanced_search():
    pipeline = await create_simple_rag(["./docs/"])

    # Search with filters
    results = await pipeline.search(
        "machine learning algorithms",
        top_k=5,
        similarity_threshold=0.8,
        filters={"document_type": "research_paper"}
    )

    # Stream results
    async for result in pipeline.stream_search("deep learning"):
        print(f"Result: {result.content[:100]}...")
```

### Response Generation

```python
async def generate_response():
    pipeline = await create_simple_rag(["./knowledge_base/"])

    response = await pipeline.generate_response(
        "What are the latest developments in AI?",
        llm_provider="openai"  # Your preferred LLM
    )

    print(f"Response: {response['response']}")
    print(f"Sources: {len(response['sources'])}")
    print(f"Confidence: {response['confidence']}")
```

## 🏗️ Architecture

The RAG system consists of several key components:

### 1. Document Loaders
- **BaseLoader**: Abstract base class for all loaders
- **Intelligent loading**: Auto-detect file types and appropriate loaders
- **Batch processing**: Efficient processing of multiple documents
- **Metadata extraction**: Automatic metadata extraction from documents

### 2. Text Chunkers
- **BaseChunker**: Abstract base class for all chunking strategies
- **Content-aware**: Specialized chunkers for different content types
- **Overlap handling**: Configurable overlap between chunks
- **Boundary awareness**: Respect sentence and paragraph boundaries

### 3. Embedding Providers
- **BaseProvider**: Abstract interface for embedding providers
- **Batch processing**: Efficient batch embedding generation
- **Caching**: Local caching of embeddings
- **Fallback handling**: Graceful fallback between providers

### 4. Vector Databases
- **BaseVectorDB**: Abstract interface for vector databases
- **Index management**: Automatic index creation and management
- **Similarity search**: Efficient similarity search with filters
- **Persistence**: Local and cloud persistence options

### 5. RAG Pipeline
- **Orchestration**: Coordinates all components
- **Async processing**: Full async/await support
- **Error handling**: Comprehensive error handling and recovery
- **Monitoring**: Built-in statistics and monitoring

## 🧪 Testing

Run the test suite:

```bash
# Run all RAG tests
pytest tests/test_rag_*.py -v

# Run specific tests
pytest tests/test_rag_config.py -v
pytest tests/test_rag_pipeline.py -v

# Run with coverage
pytest tests/test_rag_*.py --cov=src/aideck/rag --cov-report=html
```

## 📈 Performance

### Optimization Tips

1. **Chunk Size**: Use 512-1024 characters for most use cases
2. **Batch Processing**: Enable parallel processing for large document sets
3. **Caching**: Enable embedding caching for repeated queries
4. **Vector DB**: Choose appropriate index type (HNSW for balance, IVF for speed)
5. **Provider Selection**: Use FastEmbed for local processing, OpenAI for quality

### Benchmarks

Typical performance characteristics:
- **Document loading**: 10-100 docs/second (depends on format)
- **Chunking**: 1000+ chunks/second
- **Embedding**: 100-1000 embeddings/second (depends on provider)
- **Search**: 10-100ms query time (depends on vector DB and index size)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [Full documentation](https://docs.aideck.ai/rag)
- **Issues**: [GitHub Issues](https://github.com/khulnasoft/aideck/issues)
- **Discussions**: [GitHub Discussions](https://github.com/khulnasoft/aideck/discussions)

## 🔗 Related Projects

- **Aideck**: Main AI agent framework
- **Aideck GUI**: Graphical interface for Aideck
- **Aideck MCP**: Model Context Protocol integration
