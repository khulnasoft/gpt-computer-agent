from __future__ import annotations

from .base import BaseLoader
from .config import (
    CSVLoaderConfig,
    DOCXLoaderConfig,
    HTMLLoaderConfig,
    JSONLoaderConfig,
    LoaderConfig,
    LoaderConfigFactory,
    MarkdownLoaderConfig,
    PdfLoaderConfig,
    TextLoaderConfig,
    XMLLoaderConfig,
    YAMLLoaderConfig,
    advanced_config,
    simple_config,
)
from .csv import CSVLoader
from .docx import DOCXLoader
from .factory import (
    LoaderFactory,
    can_handle_file,
    check_extension_conflicts,
    create_factory,
    create_intelligent_loaders,
    create_loader,
    create_loader_for_content,
    create_loader_for_file,
    get_factory,
    get_loader_statistics,
    get_supported_extensions,
    get_supported_loaders,
    list_available_loaders,
    load_document,
    load_documents_batch,
    validate_source,
    with_factory,
)
from .html import HTMLLoader
from .json import JSONLoader
from .markdown import MarkdownLoader
from .pdf import PdfLoader
from .text import TextLoader
from .xml import XMLLoader
from .yaml import YAMLLoader

__all__ = [
    "BaseLoader",
    "LoaderConfig",
    "TextLoaderConfig",
    "CSVLoaderConfig",
    "PdfLoaderConfig",
    "DOCXLoaderConfig",
    "JSONLoaderConfig",
    "XMLLoaderConfig",
    "YAMLLoaderConfig",
    "MarkdownLoaderConfig",
    "HTMLLoaderConfig",
    "LoaderConfigFactory",
    "simple_config",
    "advanced_config",
    "TextLoader",
    "CSVLoader",
    "PdfLoader",
    "DOCXLoader",
    "JSONLoader",
    "XMLLoader",
    "YAMLLoader",
    "MarkdownLoader",
    "HTMLLoader",
    "LoaderFactory",
    "get_factory",
    "create_loader",
    "create_loader_for_file",
    "create_loader_for_content",
    "can_handle_file",
    "get_supported_extensions",
    "get_supported_loaders",
    "load_document",
    "load_documents_batch",
    "create_intelligent_loaders",
    "validate_source",
    "get_loader_statistics",
    "list_available_loaders",
    "check_extension_conflicts",
    "create_factory",
    "with_factory",
]
