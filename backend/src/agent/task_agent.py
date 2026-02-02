"""
Task Agent implementation using Cohere API.

Provides an AI agent that maps natural language to MCP tools for task management.
Uses Cohere command-a-03-2025 model for reliable function calling and tool use support.
"""
import json
from typing import Any

import cohere

from .prompts import SYSTEM_PROMPT
from ..mcp import tools as mcp_tools

# Tool definitions for Cohere function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user unique identifier"},
                    "title": {"type": "string", "description": "The task title"},
                    "description": {"type": "string", "description": "Optional task description"}
                },
                "required": ["user_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Get all tasks for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user unique identifier"}
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed. IMPORTANT: You must first call list_tasks to get the task UUID, then use that UUID here.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user unique identifier"},
                    "task_id": {"type": "string", "description": "The task UUID. NOT the task title!"}
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user unique identifier"},
                    "task_id": {"type": "string", "description": "The task unique identifier (UUID)"},
                    "title": {"type": "string", "description": "New task title"},
                    "description": {"type": "string", "description": "New task description"}
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user unique identifier"},
                    "task_id": {"type": "string", "description": "The task unique identifier (UUID)"}
                },
                "required": ["user_id", "task_id"]
            }
        }
    }
]


def execute_tool(name: str, arguments: dict) -> Any:
    """Execute a tool by name with given arguments."""
    if name == "add_task":
        return mcp_tools.add_task(
            arguments["user_id"],
            arguments["title"],
            arguments.get("description")
        )
    elif name == "list_tasks":
        return mcp_tools.list_tasks(arguments["user_id"])
    elif name == "complete_task":
        return mcp_tools.complete_task(arguments["user_id"], arguments["task_id"])
    elif name == "update_task":
        return mcp_tools.update_task(
            arguments["user_id"],
            arguments["task_id"],
            arguments.get("title"),
            arguments.get("description")
        )
    elif name == "delete_task":
        return mcp_tools.delete_task(arguments["user_id"], arguments["task_id"])
    else:
        return {"error": f"Unknown tool: {name}"}


class TaskAgent:
    """
    AI agent for task management via natural language.
    Uses Cohere API for reliable tool/function calling support.
    """

    def __init__(self, model: str | None = None):
        """
        Initialize the TaskAgent.

        Args:
            model: Model to use (default: command-a-03-2025)
        """
        from ..config import get_settings
        settings = get_settings()

        # Use Cohere for reliable tool use support
        self.client = cohere.AsyncClientV2(
            api_key=settings.cohere_api_key,
        )
        # Use command-a-03-2025 for fast, reliable tool calling
        self.model = model or settings.cohere_model

    async def run(
        self,
        message: str,
        user_id: str,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Process a user message and return the agent response.

        Args:
            message: User natural language message
            user_id: User identifier for tool calls
            context: Optional additional context

        Returns:
            dict with response and tool_calls
        """
        # Build messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n\nCurrent User ID: {user_id}"}
        ]

        # Add conversation history if available
        if context and context.get("conversation_history"):
            for msg in context["conversation_history"][-5:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add current user message
        messages.append({"role": "user", "content": message})

        tool_calls_made = []

        # Call the model
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            tools=TOOLS,
        )

        # Handle tool calls if any
        while response.message.tool_calls:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response.message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in response.message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                # Inject user_id if not provided
                if "user_id" not in arguments:
                    arguments["user_id"] = user_id

                # Execute the tool
                result = execute_tool(function_name, arguments)

                tool_calls_made.append({
                    "name": function_name,
                    "arguments": arguments,
                    "result": result
                })

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Get next response
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                tools=TOOLS,
            )

        # Get final text response
        response_text = ""
        if response.message.content:
            for block in response.message.content:
                if hasattr(block, "text"):
                    response_text += block.text

        return {
            "response": response_text,
            "tool_calls": tool_calls_made
        }


def create_task_agent(model: str | None = None) -> TaskAgent:
    """Factory function to create a TaskAgent instance."""
    return TaskAgent(model=model)
