from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.schemas import UrlSourceRequest, TextSourceRequest
from app.services.source_ingest import source_ingest_service
from pydantic import BaseModel
from app.services.retrieval import retrieve_relevant_chunks

router = APIRouter()

@router.post("/upload")
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
            metadata = source_ingest_service.add_pdf_source(filename, content)
        else:
            text_str = content.decode('utf-8', errors='ignore')
            metadata = source_ingest_service.add_text_source(filename, text_str)
            
        res = {
            "status": "success",
            "data": metadata,
            "source_id": metadata.get("id"),
            "id": metadata.get("id")
        }
        for k, v in metadata.items():
            if k not in res:
                res[k] = v
        return res
    except Exception as e:
        return {
            "status": "error",
            "error": {"message": f"Failed to ingest file: {str(e)}"}
        }

@router.post("/add-url")
async def add_url(request: UrlSourceRequest):
    """
    Ingest text parsed from a URL.
    """
    try:
        metadata = await source_ingest_service.add_url_source(request.url)
        res = {
            "status": "success",
            "data": metadata,
            "source_id": metadata.get("id"),
            "id": metadata.get("id")
        }
        for k, v in metadata.items():
            if k not in res:
                res[k] = v
        return res
    except Exception as e:
        return {
            "status": "error",
            "error": {"message": f"Failed to ingest URL: {str(e)}"}
        }

@router.post("/add-text")
async def add_text(request: TextSourceRequest):
    """
    Ingest pasted plain text.
    """
    try:
        metadata = source_ingest_service.add_text_source(request.title, request.text)
        res = {
            "status": "success",
            "data": metadata,
            "source_id": metadata.get("id"),
            "id": metadata.get("id")
        }
        for k, v in metadata.items():
            if k not in res:
                res[k] = v
        return res
    except Exception as e:
        return {
            "status": "error",
            "error": {"message": f"Failed to ingest text: {str(e)}"}
        }

@router.get("/list")
async def list_sources():
    """
    List all ingested source metadata.
    """
    sources = source_ingest_service.list_sources()
    return {
        "status": "success",
        "data": sources,
        "sources": sources
    }

class QueryRequest(BaseModel):
    source_id: str
    query: str

@router.post("/query")
async def query_source(request: QueryRequest):
    """
    Query chunks from a source.
    """
    chunks = retrieve_relevant_chunks(request.query, source_id=request.source_id, limit=3)
    chunk_list = [c.model_dump() for c in chunks]
    return {
        "status": "success",
        "data": chunk_list,
        "chunks": chunk_list
    }

@router.delete("/{source_id}")
async def delete_source(source_id: str):
    """
    Delete an ingested source and its corresponding chunks.
    """
    deleted = source_ingest_service.delete_source(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
    return {
        "status": "success",
        "data": {"deleted": True, "source_id": source_id},
        "deleted": True,
        "source_id": source_id
    }
