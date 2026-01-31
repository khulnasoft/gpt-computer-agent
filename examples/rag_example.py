"""
RAG System Example

This example demonstrates how to use the Aideck RAG system for document processing,
embedding, and retrieval.
"""

import asyncio
import tempfile
from pathlib import Path

from aideck.rag import (
    RAGConfig,
    RAGPipeline,
    get_advanced_rag_config,
    get_fast_rag_config,
    get_simple_rag_config,
    quick_search,
)


async def basic_rag_example():
    """Basic RAG example with simple configuration."""
    print("🚀 Basic RAG Example")
    print("=" * 50)

    # Create temporary documents
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create sample documents
        docs = [
            {
                "file": temp_path / "ai_basics.txt",
                "content": """
                Artificial Intelligence (AI) is a branch of computer science that aims to create
                intelligent machines that can perform tasks that typically require human intelligence.
                These tasks include learning, reasoning, problem-solving, perception, and language understanding.

                Machine Learning is a subset of AI that focuses on the development of algorithms
                that can learn and improve from experience without being explicitly programmed.
                """,
            },
            {
                "file": temp_path / "deep_learning.txt",
                "content": """
                Deep Learning is a subset of machine learning that uses neural networks with
                multiple layers to model and understand complex patterns in data. These neural networks
                are inspired by the structure and function of the human brain.

                Convolutional Neural Networks (CNNs) are particularly effective for image recognition
                tasks, while Recurrent Neural Networks (RNNs) are well-suited for sequential data
                like text and time series.
                """,
            },
            {
                "file": temp_path / "nlp.txt",
                "content": """
                Natural Language Processing (NLP) is a field of AI that focuses on the interaction
                between computers and human language. It involves tasks like text classification,
                sentiment analysis, machine translation, and question answering.

                Modern NLP systems often use transformer architectures like BERT and GPT, which have
                revolutionized the field by achieving state-of-the-art performance on many language tasks.
                """,
            },
        ]

        # Write documents to files
        for doc in docs:
            doc["file"].write_text(doc["content"].strip())

        # Create RAG pipeline with simple configuration
        config = get_simple_rag_config()
        config.chunking.chunk_size = 500  # Smaller chunks for demo
        config.retrieval.top_k = 3

        pipeline = RAGPipeline(config=config, sources=[doc["file"] for doc in docs])

        try:
            # Process documents
            print("📚 Processing documents...")
            await pipeline.process_documents()

            # Get statistics
            stats = pipeline.get_statistics()
            print(
                f"📊 Processed {stats['documents_count']} documents into {stats['chunks_count']} chunks"
            )

            # Perform searches
            queries = [
                "What is artificial intelligence?",
                "How do neural networks work?",
                "What is natural language processing?",
                "Tell me about deep learning architectures",
            ]

            print("\n🔍 Search Results:")
            print("-" * 30)

            for query in queries:
                print(f"\n❓ Query: {query}")
                results = await pipeline.search(query, top_k=2)

                for i, result in enumerate(results, 1):
                    print(f"  {i}. Score: {result.score:.3f}")
                    print(f"     Content: {result.content[:100]}...")
                    print(f"     Source: {result.metadata.get('source', 'Unknown')}")

            # Generate response
            print("\n💬 Generated Response:")
            print("-" * 30)

            response = await pipeline.generate_response(
                "What are the main differences between AI, machine learning, and deep learning?"
            )

            print(f"Response: {response['response']}")
            print(f"Confidence: {response['confidence']:.3f}")
            print(f"Sources used: {response['context_used']}")

        except Exception as e:
            print(f"❌ Error: {e}")
            print(
                "Note: This example requires embedding and vector database dependencies."
            )


async def advanced_rag_example():
    """Advanced RAG example with custom configuration."""
    print("\n🎯 Advanced RAG Example")
    print("=" * 50)

    # Create custom configuration
    config = get_advanced_rag_config()
    config.name = "advanced_demo"

    # Customize chunking for better semantic understanding
    config.chunking.strategy = "semantic"
    config.chunking.chunk_size = 800
    config.chunking.chunk_overlap = 200
    config.chunking.semantic_threshold = 0.7

    # Enable advanced retrieval features
    config.retrieval.enable_reranking = True
    config.retrieval.enable_hybrid_search = True
    config.retrieval.enable_diversity = True
    config.retrieval.top_k = 5

    # Use fastembed for local embeddings (no API keys needed)
    config.embedding.provider = "fastembed"
    config.embedding.model_name = "all-MiniLM-L6-v2"

    # Use Chroma for local vector storage
    config.vectordb.provider = "chroma"
    config.vectordb.persist_directory = "./data/advanced_rag_demo"

    print(f"📋 Configuration: {config.name}")
    print(f"🔧 Chunking strategy: {config.chunking.strategy}")
    print(f"🧠 Embedding provider: {config.embedding.provider}")
    print(f"🗄️ Vector DB: {config.vectordb.provider}")
    print(f"🔍 Reranking: {config.retrieval.enable_reranking}")
    print(f"🌐 Hybrid search: {config.retrieval.enable_hybrid_search}")

    # Note: Actual processing would require the dependencies to be installed
    print("\n💡 This configuration provides:")
    print("   • Semantic chunking for better context preservation")
    print("   • Local embeddings with FastEmbed")
    print("   • Advanced retrieval with reranking")
    print("   • Hybrid vector + keyword search")
    print("   • Diverse result selection")


async def quick_search_example():
    """Quick search example using convenience functions."""
    print("\n⚡ Quick Search Example")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a single document
        doc_file = temp_path / "python_guide.txt"
        doc_file.write_text(
            """
        Python is a high-level, interpreted programming language known for its simplicity
        and readability. It was created by Guido van Rossum and first released in 1991.

        Python supports multiple programming paradigms including procedural, object-oriented,
        and functional programming. It has a large standard library and extensive third-party
        packages for data science, web development, machine learning, and more.

        Popular Python frameworks include Django and Flask for web development,
        NumPy and Pandas for data analysis, and TensorFlow and PyTorch for machine learning.
        """
        )

        try:
            # Use quick search for simple retrieval
            results = await quick_search("What is Python?", sources=[doc_file], top_k=3)

            print(f"🔍 Found {len(results)} results:")

            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result.score:.3f}")
                print(f"     Content: {result.content[:150]}...")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("Note: Quick search requires embedding dependencies.")


async def configuration_examples():
    """Demonstrate different configuration options."""
    print("\n⚙️ Configuration Examples")
    print("=" * 50)

    # Simple configuration
    simple_config = get_simple_rag_config()
    print("📝 Simple Configuration:")
    print(f"   Chunk size: {simple_config.chunking.chunk_size}")
    print(f"   Strategy: {simple_config.chunking.strategy}")
    print(f"   Embedding: {simple_config.embedding.provider}")
    print(f"   Vector DB: {simple_config.vectordb.provider}")

    # Fast configuration
    fast_config = get_fast_rag_config()
    print("\n⚡ Fast Configuration:")
    print(f"   Chunk size: {fast_config.chunking.chunk_size}")
    print(f"   Strategy: {fast_config.chunking.strategy}")
    print(f"   Embedding: {fast_config.embedding.provider}")
    print(f"   Vector DB: {fast_config.vectordb.provider}")

    # Custom configuration
    custom_config = RAGConfig(
        name="custom_rag",
        chunking={"chunk_size": 600, "chunk_overlap": 100, "strategy": "recursive"},
        embedding={
            "provider": "openai",
            "model_name": "text-embedding-3-small",
            "batch_size": 16,
        },
        retrieval={"top_k": 7, "similarity_threshold": 0.75, "enable_reranking": True},
    )

    print("\n🎛️ Custom Configuration:")
    print(f"   Name: {custom_config.name}")
    print(f"   Chunk size: {custom_config.chunking.chunk_size}")
    print(f"   Embedding model: {custom_config.embedding.model_name}")
    print(f"   Top-K results: {custom_config.retrieval.top_k}")

    # Save configuration to file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "my_rag_config.json"
        custom_config.save_to_file(config_file)
        print(f"\n💾 Configuration saved to: {config_file}")

        # Load configuration from file
        loaded_config = RAGConfig.from_file(config_file)
        print(f"📂 Loaded configuration: {loaded_config.name}")


async def main():
    """Run all examples."""
    print("🎯 Aideck RAG System Examples")
    print("=" * 60)

    try:
        await basic_rag_example()
        await advanced_rag_example()
        await quick_search_example()
        await configuration_examples()

        print("\n✅ All examples completed!")
        print("\n💡 To use the RAG system with real embeddings:")
        print("   1. Install required dependencies: pip install aideck[rag]")
        print("   2. Set up API keys (OpenAI, etc.) in environment variables")
        print("   3. Choose your preferred embedding and vector database providers")
        print("   4. Run the examples with real document sources")

    except Exception as e:
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())
