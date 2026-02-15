"""OCR extraction endpoints - API v2 with enhanced features."""

from typing import List
from fastapi import APIRouter, File, UploadFile, Depends
from app.models import User
from app.schemas import OCRBatchResponse
from app.core.dependencies import get_current_active_user


router = APIRouter(prefix="/ocr")


@router.post("/batch", response_model=OCRBatchResponse)
async def batch_extract(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Extract text from multiple documents asynchronously.
    
    This endpoint accepts multiple files and processes them in the background.
    A job ID is returned which can be used to check status and retrieve results.
    """
    # TODO: Implement Celery task for batch processing
    return OCRBatchResponse(
        job_id="not_implemented",
        status="pending",
        message="Batch processing not yet implemented. Use v1 API for now."
    )
