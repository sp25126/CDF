from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.schemas import GlobalResponse, UrlSourceRequest, TextSourceRequest
from app.services.source_service import source_service

router = APIRouter()

@router.post("/upload", response_model=GlobalResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Ingest a uploaded PDF or text file, parse it, chunk it, and index it.
    """
    filename = file.filename
    if not filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
    try:
        content = await file.read()
        if filename.endswith('.pdf'):
            metadata = source_service.add_pdf_source(filename, content)
        else:
            text_str = content.decode('utf-8', errors='ignore')
            metadata = source_service.add_text_source(filename, text_str)
            
        return {
            "status": "success",
            "data": metadata
        }
    except Exception as e:
        return {
            "status": "error",
            "error": {"message": f"Failed to ingest file: {str(e)}"}
        }

@router.post("/add-url", response_model=GlobalResponse)
async def add_url(request: UrlSourceRequest):
    """
    Ingest text parsed from a URL.
    """
    try:
        metadata = await source_service.add_url_source(request.url)
        return {
            "status": "success",
            "data": metadata
        }
    except Exception as e:
        return {
            "status": "error",
            "error": {"message": f"Failed to ingest URL: {str(e)}"}
        }

@router.post("/add-text", response_model=GlobalResponse)
async def add_text(request: TextSourceRequest):
    """
    Ingest pasted plain text.
    """
    try:
        metadata = source_service.add_text_source(request.title, request.text)
        return {
            "status": "success",
            "data": metadata
        }
    except Exception as e:
        return {
            "status": "error",
            "error": {"message": f"Failed to ingest text: {str(e)}"}
        }

@router.get("", response_model=GlobalResponse)
async def list_sources():
    """
    List all ingested source metadata.
    """
    sources = source_service.list_sources()
    return {
        "status": "success",
        "data": sources
    }

@router.delete("/{source_id}", response_model=GlobalResponse)
async def delete_source(source_id: str):
    """
    Delete an ingested source and its corresponding chunks.
    """
    deleted = source_service.delete_source(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
    return {
        "status": "success",
        "data": {"deleted": True, "source_id": source_id}
    }
