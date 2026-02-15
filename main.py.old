
import tempfile
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from parsers import process_document, UnsupportedFileType, ParsingError
from fastapi.concurrency import run_in_threadpool

app = FastAPI()

@app.post("/v1/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    """
    Extracts text from an uploaded document.
    """
    # Create a temporary file with the same suffix as the original file
    temp_file_path = None
    try:
        # Use a 'with' block SOLELY for writing the file.
        # It will be closed automatically upon exiting the block,
        # which flushes the data to disk.
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name # Get the path for later use

        # NOW the file is closed and fully written. Process it.
        content, mime_type = process_document(temp_file_path)

        return {
            "filename": file.filename,
            "mime_type": mime_type,
            "content": content,
        }
    except UnsupportedFileType:
        raise HTTPException(status_code=415, detail="Unsupported file type")
    except ParsingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Ensure the temporary file is deleted if its path was assigned
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
