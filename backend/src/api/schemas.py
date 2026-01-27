"""
Pydantic schemas for the Chat API.

Defines request and response models for the chat endpoint.
"""
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request body for POST /api/{user_id}/chat endpoint.

    Attributes:
        message: User's message content (required, non-empty)
        conversation_id: Existing conversation to continue (optional)
    """
    message: str = Field(
        ...,
        min_length=1,
        description="User's message to the AI assistant",
    )
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID to continue (optional)",
    )


class ToolCallInfo(BaseModel):
    """
    Information about a single tool call made by the agent.

    Attributes:
        name: Tool name (e.g., "add_task", "list_tasks")
        arguments: Arguments passed to the tool
        result: Result returned by the tool
    """
    name: str = Field(
        ...,
        description="Name of the tool called",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool",
    )
    result: Any = Field(
        default=None,
        description="Result returned by the tool",
    )


class ChatResponse(BaseModel):
    """
    Response body from POST /api/{user_id}/chat endpoint.

    Attributes:
        conversation_id: Conversation identifier (new or existing)
        response: Agent's response message
        tool_calls: List of tools invoked during processing
    """
    conversation_id: UUID = Field(
        ...,
        description="Conversation identifier (new or existing)",
    )
    response: str = Field(
        ...,
        description="AI assistant's response message",
    )
    tool_calls: list[ToolCallInfo] = Field(
        default_factory=list,
        description="List of tools invoked during processing",
    )


class VoiceError(BaseModel):
    """
    Error information for voice processing failures.

    Attributes:
        code: Error code for client handling
        message: Human-readable error message
    """
    code: str = Field(
        ...,
        description="Error code (e.g., TRANSCRIPTION_FAILED, TTS_FAILED, AUDIO_INVALID)",
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
    )


class VoiceResponse(BaseModel):
    """
    Response body from POST /api/{user_id}/voice-agent endpoint.

    Attributes:
        conversation_id: Conversation identifier (new or existing)
        assistant_audio: Base64-encoded MP3 audio of agent response
        transcript: Transcribed text from user's speech (null if failed)
        response_text: Agent's text response
        tool_calls: List of MCP tools invoked during processing
        error: Error details if voice processing partially failed
    """
    conversation_id: UUID = Field(
        ...,
        description="Conversation identifier (new or existing)",
    )
    assistant_audio: str = Field(
        ...,
        description="Base64-encoded MP3 audio of agent response",
    )
    transcript: Optional[str] = Field(
        default=None,
        description="Transcribed text from user's speech (null if transcription failed)",
    )
    response_text: str = Field(
        ...,
        description="Agent's text response",
    )
    tool_calls: list[ToolCallInfo] = Field(
        default_factory=list,
        description="List of MCP tools invoked during processing",
    )
    error: Optional[VoiceError] = Field(
        default=None,
        description="Error details if voice processing partially failed",
    )
