from typing import Optional
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..models import DownloadJob, JobStatus, get_db_session
from ..config import get_settings
from ..service import BridgeService, get_bridge_service
from pathlib import Path

app = FastAPI()
# Use a relative path for the templates directory
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=templates_path)


@app.on_event("startup")
async def startup_event():
    bridge_service = get_bridge_service()
    bridge_service.start_polling()
    # This is a simplistic way to run the download processor.
    # A more robust solution would use a separate worker process.
    import threading
    def process_downloads():
        import time
        while True:
            bridge_service.process_download_queue()
            time.sleep(5)

    download_thread = threading.Thread(target=process_downloads)
    download_thread.daemon = True
    download_thread.start()


@app.get("/", response_class=HTMLResponse)
async def read_jobs(request: Request, db: Session = Depends(lambda: get_db_session(get_settings().database_url))):
    jobs = db.query(DownloadJob).all()
    return templates.TemplateResponse("index.html", {"request": request, "jobs": jobs})

@app.get("/api/jobs")
def get_jobs(status: Optional[str] = None, db: Session = Depends(lambda: get_db_session(get_settings().database_url))):
    query = db.query(DownloadJob)
    if status:
        query = query.filter(DownloadJob.status == JobStatus[status.upper()])
    return query.all()

@app.get("/api/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(lambda: get_db_session(get_settings().database_url))):
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
