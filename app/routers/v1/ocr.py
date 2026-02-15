"""OCR extraction endpoints - API v1."""

import tempfile
import os
import time
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UsageLog
from app.services.parsers import process_document, UnsupportedFileType, ParsingError
from app.schemas import OCRResponse
from app.core.dependencies import get_current_active_user
from app.config import settings


router = APIRouter(prefix="/ocr")


@router.post("/extract", response_model=OCRResponse)
async def extract_text(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract text from an uploaded document.
    
    Supports: PDF, DOCX, XLSX, PPTX, images (PNG, JPG, TIFF), 
    ODT, RTF, HTML, EPUB, Markdown, CSV
    """
    # Check file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Create temporary file
    temp_file_path = None
    start_time = time.time()
    
    try:
        # Write to temp file
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Process document
        content, mime_type = process_document(temp_file_path)
        processing_time = time.time() - start_time
        
        # Log usage
        usage_log = UsageLog(
            user_id=current_user.id,
            endpoint="/api/v1/ocr/extract",
            file_type=mime_type,
            file_size=file_size,
            processing_time=processing_time,
            status_code=200,
        )
        db.add(usage_log)
        await db.commit()
        
        return OCRResponse(
            filename=file.filename,
            mime_type=mime_type,
            content=content,
            file_size=file_size,
            processing_time=processing_time
        )
        
    except UnsupportedFileType as e:
        # Log failed request
        usage_log = UsageLog(
            user_id=current_user.id,
            endpoint="/api/v1/ocr/extract",
            file_size=file_size,
            status_code=415,
            error_message=str(e)
        )
        db.add(usage_log)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type"
        )
        
    except ParsingError as e:
        # Log failed request
        usage_log = UsageLog(
            user_id=current_user.id,
            endpoint="/api/v1/ocr/extract",
            file_size=file_size,
            status_code=422,
            error_message=str(e)
        )
        db.add(usage_log)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    except Exception as e:
        # Log failed request
        usage_log = UsageLog(
            user_id=current_user.id,
            endpoint="/api/v1/ocr/extract",
            file_size=file_size,
            status_code=500,
            error_message=str(e)
        )
        db.add(usage_log)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
        
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
