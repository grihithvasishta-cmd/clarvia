from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from clairvia_ai.main import main

logging.basicConfig(level="INFO")
logger = logging.getLogger("api_server")

app = FastAPI(title="Clairvia AI Backend")

pipeline = main()

class ProcessRequest(BaseModel):
    source_type: str
    path_or_url: str
    options: Optional[dict] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
def process(req: ProcessRequest):
    try:
        source = req.source_type.lower()
        if source == "pdf":
            result = pipeline.process_pdf(req.path_or_url)
        elif source == "audio":
            result = pipeline.process_audio(req.path_or_url)
        elif source == "image":
            result = pipeline.process_image(req.path_or_url)
        elif source == "youtube":
            result = pipeline.process_youtube(req.path_or_url)
        else:
            raise HTTPException(status_code=400, detail="Unsupported source_type")
        return result
    except Exception as e:
        logger.exception("Processing error")
        raise HTTPException(status_code=500, detail=str(e))
