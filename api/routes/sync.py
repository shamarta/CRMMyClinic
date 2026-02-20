from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.database.sync import sync_engine

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncResponse(BaseModel):
    success: bool
    message: str
    result: Dict[str, bool]


@router.post("/manual", response_model=SyncResponse)
async def manual_sync():
    try:
        result = await sync_engine.perform_sync()
        return {
            "success": True,
            "message": "Synchronization completed successfully",
            "result": result,
        }
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synchronization failed: {str(e)}",
        )


@router.get("/status")
async def sync_status():
    return {
        "enabled": sync_engine.sync_enabled,
        "running": sync_engine.running,
        "interval_seconds": sync_engine.sync_interval,
    }
