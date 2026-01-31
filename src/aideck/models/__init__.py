"""
Aideck Models Module

This module provides model providers and utilities for working with various LLM providers.
"""

from .base import BaseModelProvider
from .factory import ModelFactory
from .providers import (
    Anthropic,
    AzureOpenAI,
    BedrockAnthropic,
    Deepseek,
    Gemini,
    Ollama,
    OpenAI,
    OpenRouter,
)
from .utils import (
    check_provider_environment,
    get_all_supported_models,
    get_estimated_cost,
    list_available_models,
)

__all__ = [
    # Base classes
    "BaseModelProvider",
    # Provider classes
    "OpenAI",
    "AzureOpenAI",
    "Deepseek",
    "OpenRouter",
    "Ollama",
    "Anthropic",
    "BedrockAnthropic",
    "Gemini",
    # Utility functions
    "list_available_models",
    "get_all_supported_models",
    "check_provider_environment",
    "get_estimated_cost",
    # Factory
    "ModelFactory",
]
