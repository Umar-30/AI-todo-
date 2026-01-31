"""
Task Agent implementation using OpenAI API directly.

Provides an AI agent that maps natural language to MCP tools for task management.
Uses OpenAI gpt-4o-mini for reliable function calling and tool use support.
"""
import json
from typing import Any

from openai import AsyncOpenAI

from .prompts import SYSTEM_PROMPT
from ..mcp import tools as mcp_tools

# Tool definitions for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user's unique identifier"},
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
                    "user_id": {"type": "string", "description": "The user's unique identifier"}
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
                    "user_id": {"type": "string", "description": "The user's unique identifier"},
                    "task_id": {"type": "string", "description": "The task's UUID (e.g., 'd18627f4-73ff-4450-943e-451c24962de0'). NOT the task title!"}
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user's unique identifier"},
                    "task_id": {"type": "string", "description": "The task's unique identifier (UUID)"},
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
                    "user_id": {"type": "string", "description": "The user's unique identifier"},
                    "task_id": {"type": "string", "description": "The task's unique identifier (UUID)"}
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
    Uses OpenAI API directly for reliable tool/function calling support.
    """

    def __init__(self, model: str | None = None):
        """
        Initialize the TaskAgent.

        Args:
            model: Model to use (default: gpt-4o-mini)
        """
        from ..config import get_settings
        settings = get_settings()

        # Use OpenAI directly for reliable tool use support
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        # Use gpt-4o-mini for fast, reliable tool calling
        self.model = model or "gpt-4o-mini"

    async def run(
        self,
        message: str,
        user_id: str,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Process a user message and return the agent's response.

        Args:
            message: User's natural language message
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
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Handle tool calls if any
        while assistant_message.tool_calls:
            # Add assistant message with tool calls
            messages.append(assistant_message)

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message

        # Get final text response
        response_text = assistant_message.content or ""

        return {
            "response": response_text,
            "tool_calls": tool_calls_made
        }


def create_task_agent(model: str | None = None) -> TaskAgent:
    """Factory function to create a TaskAgent instance."""
    return TaskAgent(model=model)
