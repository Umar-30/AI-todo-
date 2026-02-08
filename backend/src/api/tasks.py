"""
Tasks API endpoint for Todo AI Chatbot.

Implements GET /api/tasks (authenticated) for fetching user tasks.
Includes SSE endpoint for real-time task updates.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import os

from ..mcp.tools import list_tasks, search_tasks, complete_task, uncomplete_task, delete_task, ValidationError, TaskNotFoundError
from ..events import task_event_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Tasks"])

# Security scheme for bearer token
security = HTTPBearer()

def verify_token(token: str) -> dict:
    """Verify JWT token and return user data."""
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET", "todo-ai-chatbot-secret"), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class TaskResponse(BaseModel):
    """Task data model for API responses."""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[str]
    priority: Optional[str]
    category: Optional[str]
    tags: Optional[list[str]] = None
    reminder_time: Optional[str] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[str] = None
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    """Response model for task list endpoint."""
    tasks: list[TaskResponse]


@router.get(
    "/{user_id}/tasks",
    response_model=TaskListResponse,
    responses={
        200: {"description": "Successfully retrieved task list"},
        500: {"description": "Internal server error"},
    },
    summary="Get user's tasks by user_id",
    description="Returns a list of all tasks belonging to the specified user.",
)
async def get_tasks_by_user_id(user_id: str) -> TaskListResponse:
    """
    Fetch all tasks for a user by user_id.
    """
    logger.info(f"Fetching tasks for user {user_id}")

    try:
        tasks = list_tasks(user_id)
        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
        return TaskListResponse(tasks=tasks)

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    responses={
        200: {"description": "Successfully retrieved task list"},
        401: {"description": "Unauthorized - invalid or missing token"},
        500: {"description": "Internal server error"},
    },
    summary="Get authenticated user's tasks",
    description="Returns a list of all tasks belonging to the authenticated user.",
)
async def get_tasks(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TaskListResponse:
    """
    Fetch all tasks for the authenticated user.

    Uses the MCP list_tasks tool internally for database access.
    Requires authentication via Bearer token.
    """
    # Verify the token and extract user data
    user_data = verify_token(credentials.credentials)
    user_id = user_data.get("sub")

    logger.info(f"Fetching tasks for authenticated user {user_id}")

    try:
        tasks = list_tasks(user_id)
        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
        return TaskListResponse(tasks=tasks)

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")


@router.get(
    "/tasks/search",
    response_model=TaskListResponse,
    responses={
        200: {"description": "Search results"},
        401: {"description": "Unauthorized"},
    },
    summary="Search, filter, and sort tasks",
    description="T077-T082: Search tasks by text, filter by status/priority/tags, sort by fields.",
)
async def search_tasks_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    q: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
) -> TaskListResponse:
    """Search, filter, and sort tasks."""
    user_data = verify_token(credentials.credentials)
    user_id = user_data.get("sub")

    try:
        tag_list = tags.split(",") if tags else None
        tasks = search_tasks(
            user_id=user_id,
            query=q,
            status=status,
            priority=priority,
            tags=tag_list,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return TaskListResponse(tasks=tasks)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to search tasks")


class DeleteResponse(BaseModel):
    """Response model for delete operation."""
    deleted: bool
    task_id: str


@router.patch(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task marked as completed"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
    },
    summary="Mark task as completed",
)
async def mark_task_complete(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TaskResponse:
    """Mark a task as completed."""
    user_data = verify_token(credentials.credentials)
    user_id = user_data.get("sub")

    try:
        task = complete_task(user_id, task_id)
        return TaskResponse(**task)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/tasks/{task_id}/uncomplete",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task marked as pending"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
    },
    summary="Mark task as pending",
)
async def mark_task_uncomplete(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TaskResponse:
    """Mark a task as not completed (pending)."""
    user_data = verify_token(credentials.credentials)
    user_id = user_data.get("sub")

    try:
        task = uncomplete_task(user_id, task_id)
        return TaskResponse(**task)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/tasks/{task_id}",
    response_model=DeleteResponse,
    responses={
        200: {"description": "Task deleted"},
        401: {"description": "Unauthorized"},
        404: {"description": "Task not found"},
    },
    summary="Delete a task",
)
async def delete_task_endpoint(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> DeleteResponse:
    """Permanently delete a task."""
    user_data = verify_token(credentials.credentials)
    user_id = user_data.get("sub")

    try:
        result = delete_task(user_id, task_id)
        return DeleteResponse(**result)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/tasks/stream",
    responses={
        200: {"description": "SSE stream for real-time task updates"},
        401: {"description": "Unauthorized"},
    },
    summary="Subscribe to real-time task updates",
    description="Server-Sent Events endpoint for receiving real-time task updates.",
)
async def stream_task_updates(
    request: Request,
    token: Optional[str] = None,
):
    """
    SSE endpoint for real-time task updates.

    Clients receive events when tasks are created, updated, completed, or deleted.
    Events include: task.created, task.updated, task.completed, task.uncompleted, task.deleted

    Note: Token is passed via query param since EventSource doesn't support headers.
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = verify_token(token)
    user_id = user_data.get("sub")

    logger.info(f"Starting SSE stream for user {user_id}")

    async def event_generator():
        try:
            async for event in task_event_manager.subscribe(user_id):
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info(f"Client disconnected, closing SSE stream for user {user_id}")
                    break
                yield event
        except Exception as e:
            logger.error(f"SSE stream error for user {user_id}: {e}")
        finally:
            logger.info(f"SSE stream ended for user {user_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
