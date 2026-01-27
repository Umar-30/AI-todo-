"""
AI Intent Agent module for Todo AI Chatbot.

Provides an AI agent that interprets natural language user messages
and maps them to appropriate MCP tools for task management.
"""
from .task_agent import create_task_agent, TaskAgent
from .prompts import SYSTEM_PROMPT

__all__ = [
    "create_task_agent",
    "TaskAgent",
    "SYSTEM_PROMPT",
]
