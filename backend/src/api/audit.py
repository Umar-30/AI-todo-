"""
Audit API endpoint for Todo AI Chatbot.

T095: Audit history endpoint - proxies to audit-service via Dapr service invocation.
"""
import logging
import os
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .tasks import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Audit"])

security = HTTPBearer()

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
AUDIT_APP_ID = "audit-service"


@router.get(
    "/audit/{task_id}",
    responses={
        200: {"description": "Audit history for the task"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
    summary="Get task audit history",
    description="Returns chronological audit trail for a specific task.",
)
async def get_task_audit(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> List[Dict[str, Any]]:
    """
    Get audit history for a task via Dapr service invocation to audit-service.
    """
    verify_token(credentials.credentials)

    url = f"{DAPR_BASE_URL}/v1.0/invoke/{AUDIT_APP_ID}/method/audit/{task_id}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        logger.warning("Audit service not available via Dapr, returning empty")
        return []

    except Exception as e:
        logger.error(f"Error fetching audit history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit history")
