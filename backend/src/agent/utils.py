"""
Utility functions for the Task Agent.

Provides helper functions for response formatting and task display.
"""
from typing import Any


def format_task_list(tasks: list[dict]) -> str:
    """
    Format a list of tasks for display to the user.

    Args:
        tasks: List of task dictionaries from list_tasks tool

    Returns:
        Formatted string representation of tasks
    """
    if not tasks:
        return "You don't have any tasks yet."

    lines = ["Here are your tasks:\n"]
    for i, task in enumerate(tasks, 1):
        status = "✓" if task.get("completed", False) else "○"
        title = task.get("title", "Untitled")
        description = task.get("description")

        line = f"{i}. [{status}] {title}"
        if description:
            line += f"\n   {description}"
        lines.append(line)

    completed = sum(1 for t in tasks if t.get("completed", False))
    total = len(tasks)
    lines.append(f"\n{completed}/{total} tasks completed")

    return "\n".join(lines)


def format_task_created(task: dict) -> str:
    """
    Format a confirmation message for task creation.

    Args:
        task: Task dictionary from add_task tool

    Returns:
        Confirmation message string
    """
    title = task.get("title", "your task")
    return f"I've added '{title}' to your tasks."


def format_task_completed(task: dict) -> str:
    """
    Format a confirmation message for task completion.

    Args:
        task: Task dictionary from complete_task tool

    Returns:
        Confirmation message string
    """
    title = task.get("title", "the task")
    return f"I've marked '{title}' as complete. Great job!"


def format_task_updated(task: dict, old_title: str | None = None) -> str:
    """
    Format a confirmation message for task update.

    Args:
        task: Task dictionary from update_task tool
        old_title: Original task title (optional)

    Returns:
        Confirmation message string
    """
    new_title = task.get("title", "the task")
    if old_title and old_title != new_title:
        return f"I've updated '{old_title}' to '{new_title}'."
    return f"I've updated '{new_title}'."


def format_task_deleted(task_id: str, title: str | None = None) -> str:
    """
    Format a confirmation message for task deletion.

    Args:
        task_id: ID of deleted task
        title: Task title if known

    Returns:
        Confirmation message string
    """
    if title:
        return f"I've removed '{title}' from your tasks."
    return "I've removed the task from your list."


def format_error(error_type: str, message: str) -> str:
    """
    Format a user-friendly error message.

    Args:
        error_type: Type of error (e.g., "task_not_found", "validation_error")
        message: Error message from tool

    Returns:
        User-friendly error message
    """
    if error_type == "task_not_found":
        return f"I couldn't find that task. {message}"
    elif error_type == "validation_error":
        return f"There was a problem with your request: {message}"
    else:
        return f"Something went wrong: {message}"


def extract_json_result(result: Any) -> dict | list | None:
    """
    Extract JSON result from tool response.

    Args:
        result: Raw tool response

    Returns:
        Parsed JSON data or None if parsing fails
    """
    import json

    if isinstance(result, (dict, list)):
        return result

    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return None

    return None
