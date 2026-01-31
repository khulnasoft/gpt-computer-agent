"""
Data models for AI Safety Engine
"""

from typing import Any

from pydantic import BaseModel


class PolicyInput(BaseModel):
    """Input data for policy processing"""

    input_texts: list[str] | None = None
    input_images: list[str] | None = None
    input_videos: list[str] | None = None
    input_audio: list[str] | None = None
    input_files: list[str] | None = None
    extra_data: dict[str, Any] | None = None


class RuleOutput(BaseModel):
    """Result from rule processing"""

    confidence: float
    content_type: str
    details: str
    triggered_keywords: list[str] | None = None


class PolicyOutput(BaseModel):
    """Result from policy execution"""

    output_texts: list[str] | None = None
    output_images: list[str] | None = None
    output_videos: list[str] | None = None
    output_audio: list[str] | None = None
    output_files: list[str] | None = None
    action_output: dict[str, Any] | None = None
    transformation_map: dict[int, dict[str, str]] | None = None


# Backward compatibility aliases
RuleInput = PolicyInput
ActionResult = PolicyOutput


ActionOutput = PolicyOutput
