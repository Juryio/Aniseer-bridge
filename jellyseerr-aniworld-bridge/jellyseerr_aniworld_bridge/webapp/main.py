from typing import Optional
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..models import DownloadJob, JobStatus, get_db_session, initialize_db
from ..config import get_settings
from ..service import BridgeService, get_bridge_service
from pathlib import Path
import asyncio

app = FastAPI()
# Use a relative path for the templates directory
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=templates_path)


async def process_downloads_periodically(bridge_service: BridgeService):
    """Periodically processes the download queue."""
    while True:
        bridge_service.process_download_queue()
        await asyncio.sleep(5)


@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    initialize_db(settings.database_url)
    bridge_service = get_bridge_service()
    bridge_service.start_polling()
    asyncio.create_task(process_downloads_periodically(bridge_service))


@app.get("/", response_class=HTMLResponse)
async def read_jobs(request: Request, db: Session = Depends(get_db_session)):
    jobs = db.query(DownloadJob).all()
    return templates.TemplateResponse("index.html", {"request": request, "jobs": jobs})

@app.get("/api/jobs")
def get_jobs(status: Optional[str] = None, db: Session = Depends(get_db_session)):
    query = db.query(DownloadJob)
    if status:
        query = query.filter(DownloadJob.status == JobStatus[status.upper()])
    return query.all()

@app.get("/api/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db_session)):
    return db.query(DownloadJob).filter(DownloadJob.id == job_id).first()

@app.post("/api/jobs/{job_id}/cancel")
def cancel_job_endpoint(job_id: int, bridge_service: BridgeService = Depends(get_bridge_service)):
    bridge_service.cancel_job(job_id)
    return {"message": "Job cancellation request received."}

@app.post("/api/refresh")
def force_refresh(bridge_service: BridgeService = Depends(get_bridge_service)):
    """
    Manually triggers a poll for new Jellyseerr requests.
    """
    bridge_service.process_pending_requests()
    return RedirectResponse(url="/", status_code=303)
