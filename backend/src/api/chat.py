"""
Chat API endpoint for Todo AI Chatbot.

Implements POST /api/{user_id}/chat for stateless chat interactions.
"""
import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path

from .schemas import ChatRequest, ChatResponse, ToolCallInfo
from .services import (
    ConversationAccessDeniedError,
    ConversationNotFoundError,
    create_conversation,
    create_message,
    get_conversation_with_messages,
)
from ..agent import create_task_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Bad request (empty message)"},
        403: {"description": "Access denied (conversation belongs to different user)"},
        404: {"description": "Conversation not found"},
        500: {"description": "Internal server error"},
    },
    summary="Send a chat message",
    description="Send a message to the AI assistant and receive a response.",
)
async def chat(
    request: ChatRequest,
    user_id: str = Path(..., min_length=1, description="User's unique identifier"),
) -> ChatResponse:
    """
    Process a chat message and return the AI assistant's response.

    Creates a new conversation if conversation_id is not provided.
    Continues an existing conversation if conversation_id is provided.
    """
    logger.info(f"Chat request from user {user_id}")

    # Validate message is not empty (after trimming)
    message_content = request.message.strip()
    if not message_content:
        logger.warning(f"Empty message from user {user_id}")
        raise HTTPException(
            status_code=400,
            detail="Message content is required",
        )

    try:
        # Load existing conversation or create new one
        conversation_id: UUID
        message_history: list[dict[str, str]] = []

        if request.conversation_id:
            # Continue existing conversation
            logger.info(f"Loading conversation {request.conversation_id}")
            try:
                conversation, messages = get_conversation_with_messages(
                    request.conversation_id,
                    user_id,
                )
                conversation_id = conversation.id

                # Build message history for agent context
                for msg in messages:
                    message_history.append({
                        "role": msg.role,
                        "content": msg.content,
                    })
                logger.info(f"Loaded {len(messages)} messages from conversation")

            except ConversationNotFoundError:
                logger.warning(f"Conversation {request.conversation_id} not found")
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )
            except ConversationAccessDeniedError:
                logger.warning(
                    f"User {user_id} denied access to conversation {request.conversation_id}"
                )
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to conversation",
                )
        else:
            # Create new conversation
            logger.info(f"Creating new conversation for user {user_id}")
            conversation = create_conversation(user_id)
            conversation_id = conversation.id
            logger.info(f"Created conversation {conversation_id}")

        # Store user message before processing
        create_message(
            user_id=user_id,
            conversation_id=conversation_id,
            role="user",
            content=message_content,
        )
        logger.info("Stored user message")

        # Run the AI agent with message history context
        agent = create_task_agent()
        tool_calls: list[ToolCallInfo] = []

        try:
            # Build context with conversation history
            context = {
                "conversation_history": message_history,
            }

            # Execute agent - returns dict with response and tool_calls
            agent_result = await agent.run(
                message=message_content,
                user_id=user_id,
                context=context,
            )

            # Extract response and tool calls from agent result
            response_text = agent_result.get("response", "")
            raw_tool_calls = agent_result.get("tool_calls", [])

            # Convert tool calls to ToolCallInfo objects
            for tc in raw_tool_calls:
                tool_calls.append(ToolCallInfo(
                    name=tc.get("name", "unknown"),
                    arguments=tc.get("arguments", {}),
                    result=tc.get("result"),
                ))

            logger.info(f"Agent response received, {len(tool_calls)} tool calls")

        except Exception as e:
            logger.error(f"Agent processing error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process message",
            )

        # Store assistant response
        create_message(
            user_id=user_id,
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
        )
        logger.info("Stored assistant response")

        return ChatResponse(
            conversation_id=conversation_id,
            response=response_text,
            tool_calls=tool_calls,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process message",
        )
