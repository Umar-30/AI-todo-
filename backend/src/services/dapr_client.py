"""
Dapr HTTP Client Wrapper for Event Publishing.

T009: Create Dapr HTTP client wrapper
Provides reusable functions for publishing events via Dapr HTTP API.
No direct Kafka client libraries - all messaging through Dapr.
"""
import logging
import os
from typing import Any, Dict, Optional
from uuid import uuid4

import asyncio

import httpx

logger = logging.getLogger(__name__)

# T105: Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 0.5

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub-redpanda")
STATESTORE_NAME = os.getenv("DAPR_STATESTORE_NAME", "statestore-redis")

# Topics
TOPIC_TASK_EVENTS = "task-events"
TOPIC_TASK_UPDATES = "task-updates"
TOPIC_REMINDERS = "reminders"


class DaprClientError(Exception):
    """Exception raised when Dapr operations fail."""
    pass


async def publish_event(
    topic: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, str]] = None,
    correlation_id: Optional[str] = None,
) -> bool:
    """
    Publish an event to a Dapr Pub/Sub topic.

    Args:
        topic: The topic name (e.g., 'task-events', 'task-updates')
        data: The event payload (will be JSON serialized)
        metadata: Optional metadata headers for the message
        correlation_id: Optional correlation ID for distributed tracing

    Returns:
        True if publish succeeded, False otherwise

    Raises:
        DaprClientError: If Dapr sidecar is unavailable or publish fails
    """
    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"

    headers = {"Content-Type": "application/json"}

    # Add correlation ID if provided
    if correlation_id:
        headers["x-correlation-id"] = correlation_id

    # Add custom metadata
    if metadata:
        for key, value in metadata.items():
            headers[f"metadata.{key}"] = value

    # T105: Retry logic for Dapr publish failures
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()

                logger.info(f"Published event to {topic}: {data.get('type', 'unknown')}")
                return True

        except httpx.ConnectError as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Dapr publish retry {attempt + 1}/{MAX_RETRIES} for {topic}")
                await asyncio.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
            else:
                logger.error(f"Dapr sidecar not available after {MAX_RETRIES} retries: {e}")
                raise DaprClientError(f"Dapr sidecar not available at {DAPR_BASE_URL}") from e

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            raise DaprClientError(f"Failed to publish event: {e}") from e

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Publish retry {attempt + 1}/{MAX_RETRIES}: {e}")
                await asyncio.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
            else:
                logger.error(f"Unexpected error publishing event: {e}")
                raise DaprClientError(f"Unexpected error: {e}") from e

    raise DaprClientError(f"Failed after {MAX_RETRIES} retries: {last_error}")


def publish_event_sync(
    topic: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, str]] = None,
    correlation_id: Optional[str] = None,
) -> bool:
    """
    Synchronous version of publish_event for use in non-async contexts.

    Args:
        topic: The topic name
        data: The event payload
        metadata: Optional metadata headers
        correlation_id: Optional correlation ID

    Returns:
        True if publish succeeded, False otherwise
    """
    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"

    headers = {"Content-Type": "application/json"}

    if correlation_id:
        headers["x-correlation-id"] = correlation_id

    if metadata:
        for key, value in metadata.items():
            headers[f"metadata.{key}"] = value

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()

            logger.info(f"Published event to {topic}: {data.get('type', 'unknown')}")
            return True

    except httpx.ConnectError as e:
        logger.warning(f"Dapr sidecar not available (sync): {e}")
        # Don't raise in sync mode - allow graceful degradation
        return False

    except Exception as e:
        logger.warning(f"Failed to publish event (sync): {e}")
        return False


async def get_state(key: str) -> Optional[Dict[str, Any]]:
    """
    Get state from Dapr State Store.

    Args:
        key: The state key

    Returns:
        The state value or None if not found
    """
    url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{key}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 204:
                return None

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        logger.error(f"Failed to get state {key}: {e}")
        raise DaprClientError(f"Failed to get state: {e}") from e

    except Exception as e:
        logger.error(f"Unexpected error getting state: {e}")
        raise DaprClientError(f"Unexpected error: {e}") from e


async def save_state(key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool:
    """
    Save state to Dapr State Store.

    Args:
        key: The state key
        value: The state value
        ttl_seconds: Optional TTL for the state entry

    Returns:
        True if save succeeded
    """
    url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}"

    state_entry = {
        "key": key,
        "value": value,
    }

    if ttl_seconds:
        state_entry["metadata"] = {"ttlInSeconds": str(ttl_seconds)}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=[state_entry])
            response.raise_for_status()

            logger.debug(f"Saved state for key {key}")
            return True

    except Exception as e:
        logger.error(f"Failed to save state {key}: {e}")
        raise DaprClientError(f"Failed to save state: {e}") from e


async def delete_state(key: str) -> bool:
    """
    Delete state from Dapr State Store.

    Args:
        key: The state key to delete

    Returns:
        True if delete succeeded
    """
    url = f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}/{key}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(url)
            response.raise_for_status()

            logger.debug(f"Deleted state for key {key}")
            return True

    except Exception as e:
        logger.error(f"Failed to delete state {key}: {e}")
        raise DaprClientError(f"Failed to delete state: {e}") from e


async def invoke_service(
    app_id: str,
    method: str,
    data: Optional[Dict[str, Any]] = None,
    http_method: str = "POST",
) -> Dict[str, Any]:
    """
    Invoke another service via Dapr Service Invocation.

    Args:
        app_id: The Dapr app ID of the target service
        method: The method/endpoint to call
        data: Optional request body
        http_method: HTTP method (GET, POST, PUT, DELETE)

    Returns:
        The response data from the service
    """
    url = f"{DAPR_BASE_URL}/v1.0/invoke/{app_id}/method/{method}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if http_method.upper() == "GET":
                response = await client.get(url)
            elif http_method.upper() == "POST":
                response = await client.post(url, json=data)
            elif http_method.upper() == "PUT":
                response = await client.put(url, json=data)
            elif http_method.upper() == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {http_method}")

            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

    except Exception as e:
        logger.error(f"Failed to invoke {app_id}/{method}: {e}")
        raise DaprClientError(f"Failed to invoke service: {e}") from e


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for distributed tracing."""
    return str(uuid4())
