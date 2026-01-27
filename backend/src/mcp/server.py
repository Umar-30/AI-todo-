"""
MCP server for Todo AI Chatbot.

Exposes task operations as MCP tools for AI assistants.
Uses the Official MCP SDK for protocol compliance.
"""
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import tools
from .tools import TaskNotFoundError, ValidationError
from ..database import get_engine, check_connection

logger = logging.getLogger(__name__)

# Create MCP server instance
mcp_server = Server("todo-ai-chatbot")


def _format_error(error_type: str, message: str) -> list[TextContent]:
    """Format error response as TextContent."""
    return [TextContent(type="text", text=json.dumps({"error": error_type, "message": message}))]


def _format_result(data: Any) -> list[TextContent]:
    """Format successful result as TextContent."""
    return [TextContent(type="text", text=json.dumps(data))]


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task for a user. Returns the created task with its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Owner's user identifier (required)",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional)",
                    },
                },
                "required": ["user_id", "title"],
            },
        ),
        Tool(
            name="list_tasks",
            description="Get all tasks for a user. Returns a list of tasks, empty list if none exist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Owner's user identifier (required)",
                    },
                },
                "required": ["user_id"],
            },
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed. Updates the task's completed status to true.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Owner's user identifier (required)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier (UUID format, required)",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
        Tool(
            name="update_task",
            description="Update task details. Only provided fields are updated.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Owner's user identifier (required)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier (UUID format, required)",
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional)",
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional)",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
        Tool(
            name="delete_task",
            description="Permanently delete a task. This action cannot be undone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Owner's user identifier (required)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier (UUID format, required)",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from AI assistants."""
    try:
        if name == "add_task":
            result = tools.add_task(
                user_id=arguments["user_id"],
                title=arguments["title"],
                description=arguments.get("description"),
            )
            return _format_result(result)

        elif name == "list_tasks":
            result = tools.list_tasks(user_id=arguments["user_id"])
            return _format_result(result)

        elif name == "complete_task":
            result = tools.complete_task(
                user_id=arguments["user_id"],
                task_id=arguments["task_id"],
            )
            return _format_result(result)

        elif name == "update_task":
            result = tools.update_task(
                user_id=arguments["user_id"],
                task_id=arguments["task_id"],
                title=arguments.get("title"),
                description=arguments.get("description"),
            )
            return _format_result(result)

        elif name == "delete_task":
            result = tools.delete_task(
                user_id=arguments["user_id"],
                task_id=arguments["task_id"],
            )
            return _format_result(result)

        else:
            return _format_error("unknown_tool", f"Unknown tool: {name}")

    except ValidationError as e:
        return _format_error("validation_error", str(e))
    except TaskNotFoundError as e:
        return _format_error("task_not_found", str(e))
    except Exception as e:
        logger.exception(f"Error in tool {name}")
        return _format_error("internal_error", str(e))


def create_server() -> Server:
    """
    Create and configure the MCP server.

    Verifies database connection before returning the server instance.
    """
    # Ensure database engine is initialized
    get_engine()

    # Verify database connection
    if not check_connection():
        logger.warning("Database connection check failed - server starting anyway")

    logger.info("MCP server created successfully")
    return mcp_server


async def run_server() -> None:
    """
    Run the MCP server using stdio transport.

    This is the main entry point for running the server.
    """
    server = create_server()
    logger.info("Starting MCP server on stdio...")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
