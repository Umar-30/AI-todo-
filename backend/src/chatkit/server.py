"""
ChatKit Server implementation for Todo AI Chatbot.

Wraps the TaskAgent to provide ChatKit-compatible responses.
"""
import json
import logging
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..agent import create_task_agent
from .store import ChatKitStore

logger = logging.getLogger(__name__)


class ChatKitRequest(BaseModel):
    """ChatKit request format."""
    type: str  # e.g., "message", "thread.create", "thread.messages"
    thread_id: str | None = None
    message: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class TodoChatKitServer:
    """
    ChatKit server implementation that delegates to TaskAgent.

    Handles ChatKit protocol requests and streams responses using SSE.
    """

    def __init__(self, user_id: str = "demo-user"):
        """
        Initialize the ChatKit server.

        Args:
            user_id: Default user ID for operations
        """
        self.user_id = user_id
        self.store = ChatKitStore(user_id=user_id)
        self.agent = create_task_agent()

    async def handle_request(self, request: ChatKitRequest) -> AsyncGenerator[str, None]:
        """
        Handle a ChatKit request and yield SSE events.

        Args:
            request: ChatKit request object

        Yields:
            SSE event strings
        """
        request_type = request.type
        thread_id = request.thread_id
        message = request.message
        metadata = request.metadata or {}

        # Extract user_id from metadata if provided
        user_id = metadata.get("user_id", self.user_id)

        try:
            if request_type == "thread.create":
                # Create a new thread
                thread = self.store.create_thread(user_id=user_id)
                yield self._format_event("thread.created", {"thread": thread})

            elif request_type == "thread.messages":
                # Get messages for a thread
                if not thread_id:
                    yield self._format_event("error", {"message": "thread_id required"})
                    return

                messages = self.store.get_messages(thread_id)
                yield self._format_event("thread.messages", {
                    "thread_id": thread_id,
                    "messages": messages,
                })

            elif request_type == "message":
                # Process a message through the agent
                if not message or not message.get("content"):
                    yield self._format_event("error", {"message": "message content required"})
                    return

                content = message["content"]

                # Create thread if not provided
                if not thread_id:
                    thread = self.store.create_thread(user_id=user_id)
                    thread_id = thread["id"]
                    yield self._format_event("thread.created", {"thread": thread})

                # Store user message
                user_msg = self.store.add_message(thread_id, "user", content)
                yield self._format_event("message.created", {
                    "message": user_msg,
                    "thread_id": thread_id,
                })

                # Get context from conversation history
                history = self.store.get_messages(thread_id)
                context = {
                    "conversation_history": history[:-1],  # Exclude the just-added user message
                }

                # Run the agent
                try:
                    result = await self.agent.run(
                        message=content,
                        user_id=user_id,
                        context=context,
                    )

                    response_text = result.get("response", "")
                    tool_calls = result.get("tool_calls", [])

                    # Emit tool events if any
                    for tc in tool_calls:
                        yield self._format_event("tool.started", {
                            "name": tc.get("name"),
                            "arguments": tc.get("arguments"),
                        })
                        yield self._format_event("tool.completed", {
                            "name": tc.get("name"),
                            "result": tc.get("result"),
                        })

                    # Store assistant message
                    assistant_msg = self.store.add_message(
                        thread_id, "assistant", response_text
                    )

                    # Emit response
                    yield self._format_event("message.created", {
                        "message": assistant_msg,
                        "thread_id": thread_id,
                    })
                    yield self._format_event("message.completed", {
                        "thread_id": thread_id,
                    })

                except Exception as e:
                    logger.error(f"Agent error: {e}")
                    yield self._format_event("error", {
                        "message": f"Agent error: {str(e)}",
                    })

            else:
                yield self._format_event("error", {
                    "message": f"Unknown request type: {request_type}",
                })

        except Exception as e:
            logger.error(f"ChatKit server error: {e}")
            yield self._format_event("error", {"message": str(e)})

    def _format_event(self, event: str, data: dict[str, Any]) -> str:
        """
        Format an SSE event.

        Args:
            event: Event type
            data: Event data

        Returns:
            SSE-formatted string
        """
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def create_chatkit_endpoint() -> APIRouter:
    """
    Create the ChatKit API router.

    Returns:
        FastAPI APIRouter with /chatkit endpoint
    """
    router = APIRouter(tags=["ChatKit"])

    @router.post("/chatkit")
    async def chatkit_endpoint(request: Request):
        """
        ChatKit message endpoint.

        Receives messages from ChatKit frontend and returns streamed responses.
        """
        try:
            body = await request.json()
            chatkit_request = ChatKitRequest(**body)
        except Exception as e:
            logger.error(f"Invalid request: {e}")
            return StreamingResponse(
                iter([f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"]),
                media_type="text/event-stream",
            )

        # Extract user_id from headers or use default
        user_id = request.headers.get("X-User-Id", "demo-user")

        server = TodoChatKitServer(user_id=user_id)

        return StreamingResponse(
            server.handle_request(chatkit_request),
            media_type="text/event-stream",
        )

    return router
