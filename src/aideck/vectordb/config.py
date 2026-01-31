from enum import Enum
from typing import Any, Literal, Union

import pydantic

PydanticConfig = pydantic.ConfigDict(frozen=True, extra="forbid")


class ProviderName(str, Enum):
    """Enumeration for supported vector database providers."""

    CHROMA = "chroma"
    QDRANT = "qdrant"
    WEAVIATE = "weaviate"
    PINECONE = "pinecone"
    MILVUS = "milvus"
    FAISS = "faiss"
    PG = "pgvector"


class Mode(str, Enum):
    """Enumeration for the operational mode of the provider."""

    CLOUD = "cloud"
    LOCAL = "local"
    EMBEDDED = "embedded"
    IN_MEMORY = "in_memory"


class DistanceMetric(str, Enum):
    """Enumeration for similarity calculation algorithms."""

    COSINE = "Cosine"
    EUCLIDEAN = "Euclidean"
    DOT_PRODUCT = "DotProduct"


class IndexType(str, Enum):
    """Enumeration for the core Approximate Nearest Neighbor (ANN) index algorithm."""

    HNSW = "HNSW"
    IVF_FLAT = "IVF_FLAT"
    FLAT = "FLAT"


class WriteConsistency(str, Enum):
    """Enumeration for write consistency in distributed databases."""

    STRONG = "strong"
    EVENTUAL = "eventual"


class ConsistencyLevel(str, Enum):
    STRONG = "Strong"
    BOUNDED = "Bounded"
    SESSION = "Session"
    EVENTUALLY = "Eventually"


class CoreConfig(pydantic.BaseModel):
    """
    Handles connection, identity, and the fundamental vector schema.
    Corresponds to Table 1: Core Configuration & Schema.
    """

    model_config = PydanticConfig
    db_path: str | None = None
    provider_name: ProviderName
    mode: Mode
    collection_name: str = "default_collection"
    cloud: str | None = None
    region: str | None = None
    host: str | None = None
    port: int | None = None
    api_key: pydantic.SecretStr | None = None
    use_tls: bool = True

    vector_size: int
    vector_size_sparse: int | None = None
    distance_metric: DistanceMetric = DistanceMetric.COSINE

    recreate_if_exists: bool = False

    @pydantic.validator("host", "api_key")
    def cloud_requirements(cls, v, values):
        """Validator to ensure cloud mode has the necessary credentials."""
        if values.get("mode") == Mode.CLOUD and v is None:
            raise ValueError("host and api_key are required for 'cloud' mode")
        return v


class HNSWTuningConfig(pydantic.BaseModel):
    """Fine-tunes the Hierarchical Navigable Small World (HNSW) index."""

    model_config = PydanticConfig
    index_type: Literal[IndexType.HNSW]
    m: int = 16
    ef_construction: int = 200


class IVFTuningConfig(pydantic.BaseModel):
    """Fine-tunes Inverted File (IVF) based indexes."""

    model_config = PydanticConfig
    index_type: Literal[IndexType.IVF_FLAT]
    nlist: int = 100


class FlatTuningConfig(pydantic.BaseModel):
    """Configuration for a FLAT (brute-force) index. No tuning needed."""

    model_config = PydanticConfig
    index_type: Literal[IndexType.FLAT]


IndexTuningConfig = Union[HNSWTuningConfig, IVFTuningConfig, FlatTuningConfig]


class QuantizationConfig(pydantic.BaseModel):
    """Compresses vectors to reduce memory usage."""

    model_config = PydanticConfig
    quantization_type: Literal["Scalar", "Product"]
    bits: int = 8


class PayloadIndexConfig(pydantic.BaseModel):
    """
    Defines a schema for a single payload index, allowing for optimized
    filtering on metadata fields.
    """

    model_config = PydanticConfig
    field_name: str
    field_schema_type: Literal["text", "keyword", "integer", "float", "geo", "boolean"]
    params: dict[str, Any] | None = None
    enable_full_text_index: bool | None = None


class IndexingConfig(pydantic.BaseModel):
    """
    Manages performance-critical aspects of index algorithm and memory usage.
    Corresponds to Table 2: Indexing, Storage & Performance Tuning.
    """

    model_config = PydanticConfig

    index_config: IndexTuningConfig = pydantic.Field(
        HNSWTuningConfig(index_type=IndexType.HNSW), discriminator="index_type"
    )
    quantization: QuantizationConfig | None = None

    payload_indexes: list[PayloadIndexConfig] | None = None
    create_dense_index: bool = True
    create_sparse_index: bool = False


class SearchConfig(pydantic.BaseModel):
    """
    Defines the default parameters for all retrieval operations.
    Corresponds to Table 3: Search & Retrieval Operations.
    These can be overridden at query time.
    """

    model_config = PydanticConfig

    default_top_k: int | None = None

    default_ef_search: int | None = None

    default_nprobe: int | None = None

    default_hybrid_alpha: float | None = None

    default_fusion_method: Literal["rrf", "weighted"] | None = None

    default_similarity_threshold: float | None = None

    dense_search_enabled: bool | None = None
    full_text_search_enabled: bool | None = None
    hybrid_search_enabled: bool | None = None

    filter: dict[str, Any] | None = None

    @pydantic.validator("default_hybrid_alpha")
    def alpha_in_range(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("alpha must be between 0.0 and 1.0")
        return v

    @pydantic.validator("default_similarity_threshold")
    def similarity_threshold_in_range(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        return v


class DataManagementConfig(pydantic.BaseModel):
    """
    Governs the behavior of data ingestion and lifecycle.
    Corresponds to Table 4: Data Management & Ingestion.
    """

    model_config = PydanticConfig

    batch_size: int = 128
    parallel_uploads: int = 4
    write_consistency: WriteConsistency = WriteConsistency.EVENTUAL


class AdvancedConfig(pydantic.BaseModel):
    """
    Contains optional, enterprise-grade operational features.
    Corresponds to Table 5: Advanced & Operational Features.
    """

    model_config = PydanticConfig

    namespace: str | None = None
    num_shards: int | None = None
    replication_factor: int | None = None


class Config(pydantic.BaseModel):
    """
    The master configuration object for a VectorDBProvider.

    This class is the single source of truth for a provider's setup. It is
    composed of modular sub-configs, each handling a specific functional area.
    Upon instantiation, it performs a deep validation of all parameters and their
    interdependencies, ensuring a valid and complete configuration.

    The object is immutable after creation to guarantee configuration stability.
    """

    model_config = PydanticConfig

    core: CoreConfig
    indexing: IndexingConfig = IndexingConfig()
    search: SearchConfig = SearchConfig()
    data_management: DataManagementConfig = DataManagementConfig()
    advanced: AdvancedConfig = AdvancedConfig()

    @pydantic.root_validator(skip_on_failure=True)
    def cross_config_validation(cls, values):
        """
        Performs high-level validation between different sub-configs.
        This ensures that the entire configuration is cohesive.
        """
        core_cfg: CoreConfig = values.get("core")
        indexing_cfg: IndexingConfig = values.get("indexing")

        if (
            core_cfg.distance_metric == DistanceMetric.EUCLIDEAN
            and core_cfg.provider_name in [ProviderName.CHROMA]
        ):
            pass

        search_cfg: SearchConfig = values.get("search")
        if search_cfg.default_nprobe and not isinstance(
            indexing_cfg.index_config, IVFTuningConfig
        ):
            raise ValueError(
                "`default_nprobe` can only be set for IVF_FLAT index types."
            )

        if search_cfg.default_ef_search and not isinstance(
            indexing_cfg.index_config, HNSWTuningConfig
        ):
            raise ValueError(
                "`default_ef_search` can only be set for HNSW index types."
            )

        if not indexing_cfg.create_dense_index and not indexing_cfg.create_sparse_index:
            raise ValueError(
                "Configuration Error: At least one of 'create_dense_index' or "
                "'create_sparse_index' must be True in IndexingConfig. A collection "
                "cannot be created without a vector index."
            )

        if indexing_cfg.payload_indexes:
            for payload_config in indexing_cfg.payload_indexes:
                if payload_config.enable_full_text_index:
                    if payload_config.field_schema_type not in ["text", "keyword"]:
                        raise ValueError(
                            f"Configuration Error: The 'enable_full_text_index' flag on field "
                            f"'{payload_config.field_name}' is invalid. This index can only be "
                            f"applied to fields of type 'text' or 'keyword'."
                        )
        return values
