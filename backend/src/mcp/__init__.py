"""
MCP (Model Context Protocol) server module for Todo AI Chatbot.

Exposes stateless task operations as MCP tools for AI assistants.

Usage:
    # Run as module
    python -m src.mcp

    # Or import and run programmatically
    import asyncio
    from src.mcp import run_server
    asyncio.run(run_server())
"""
import asyncio

from .server import create_server, run_server
from .tools import (
    add_task,
    list_tasks,
    complete_task,
    update_task,
    delete_task,
)

__all__ = [
    "create_server",
    "run_server",
    "add_task",
    "list_tasks",
    "complete_task",
    "update_task",
    "delete_task",
]


def main() -> None:
    """Entry point for running the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
