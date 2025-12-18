import time
import threading
from typing import List, Dict, Optional
import logging

from sqlalchemy.orm import Session

from .jellyseerr_client import JellyseerrClient
from .aniworld_client import AniWorldClientWrapper
from .mapper import RequestMapper
from .models import DownloadJob, JobStatus, get_db_session
from .config import get_settings


class BridgeService:
    def __init__(
        self,
        jellyseerr_client: JellyseerrClient,
        aniworld_client: AniWorldClientWrapper,
        mapper: RequestMapper,
        db_session: Session,
    ):
        self.jellyseerr_client = jellyseerr_client
        self.aniworld_client = aniworld_client
        self.mapper = mapper
        self.db_session = db_session
        self._stop_event = threading.Event()
        self._cancellation_events: Dict[int, threading.Event] = {}

    def start_polling(self):
        """Starts the background polling thread."""
        thread = threading.Thread(target=self._poll_requests)
        thread.daemon = True
        thread.start()

    def stop_polling(self):
        """Stops the background polling thread."""
        self._stop_event.set()

    def _poll_requests(self):
        """Periodically polls Jellyseerr for new requests."""
        settings = get_settings()
        while not self._stop_event.is_set():
            logging.info("Polling Jellyseerr for new requests...")
            self.process_pending_requests()
            time.sleep(settings.poll_interval)

    def process_pending_requests(self):
        """Processes pending requests from Jellyseerr."""
        pending_requests = self.jellyseerr_client.get_pending_requests()
        for request in pending_requests:
            self.create_download_jobs_for_request(request)

    def create_download_jobs_for_request(self, request: Dict):
        """Creates download jobs for a given Jellyseerr request."""
        media = request.get("media", {})
        if media.get("mediaType") != "tv":
            logging.info(f"Skipping non-TV request: {media.get('name')}")
            return

        show = self.mapper.map_request_to_show(request)
        if not show:
            return

        seasons = request.get("seasons", [])
        for season in seasons:
            season_number = season.get("seasonNumber")
            episodes = season.get("episodes", [])
            for episode in episodes:
                self.create_download_job(
                    request_id=request.get("id"),
                    show_name=media.get("name"),
                    aniworld_url=show.get("link"),
                    season_number=season_number,
                    episode_number=episode.get("episodeNumber"),
                )

    def create_download_job(
        self, request_id: int, show_name: str, aniworld_url: str, season_number: int, episode_number: int
    ):
        """Creates a single download job and adds it to the database."""
        existing_job = (
            self.db_session.query(DownloadJob)
            .filter_by(
                request_id=request_id,
                season=season_number,
                episode=episode_number,
            )
            .first()
        )

        if existing_job:
            logging.info(f"Job for {show_name} S{season_number:02}E{episode_number:02} already exists.")
            return

        job = DownloadJob(
            request_id=request_id,
            show_name=show_name,
            aniworld_url=aniworld_url,
            season=season_number,
            episode=episode_number,
            status=JobStatus.QUEUED,
        )
        self.db_session.add(job)
        self.db_session.commit()
        logging.info(f"Created job for {show_name} S{season_number:02}E{episode_number:02}.")

    def _update_job_progress(self, job_id: int, progress: float):
        """Updates the progress of a download job."""
        if job_id in self._cancellation_events and self._cancellation_events[job_id].is_set():
            raise Exception("Download cancelled")

        job = self.db_session.query(DownloadJob).filter_by(id=job_id).first()
        if job:
            job.progress = progress
            self.db_session.commit()

    def _download_job_thread(self, job: DownloadJob):
        try:
            show = {"link": job.aniworld_url, "name": job.show_name}
            filepath = self.aniworld_client.download_episode(
                show=show,
                season_number=job.season,
                episode_number=job.episode,
                progress_callback=lambda p: self._update_job_progress(job.id, p),
            )

            if filepath and filepath.exists():
                job.filepath = str(filepath)
                job.status = JobStatus.COMPLETED
                self.jellyseerr_client.mark_request_as_available(job.request_id)
            else:
                job.status = JobStatus.FAILED

            self.db_session.commit()

        except Exception as e:
            if "Download cancelled" in str(e):
                job.status = JobStatus.CANCELLED
            else:
                job.status = JobStatus.FAILED
            self.db_session.commit()
            logging.error(f"Error processing job {job.id}: {e}")
        finally:
            if job.id in self._cancellation_events:
                del self._cancellation_events[job.id]

    def process_download_queue(self):
        """Processes the download queue, one job at a time."""
        job = (
            self.db_session.query(DownloadJob)
            .filter_by(status=JobStatus.QUEUED)
            .order_by(DownloadJob.created_at)
            .first()
        )

        if not job:
            return

        job.status = JobStatus.RUNNING
        self.db_session.commit()

        self._cancellation_events[job.id] = threading.Event()
        thread = threading.Thread(target=self._download_job_thread, args=(job,))
        thread.daemon = True
        thread.start()

    def cancel_job(self, job_id: int):
        """Cancels a running job."""
        if job_id in self._cancellation_events:
            self._cancellation_events[job_id].set()

def get_bridge_service() -> BridgeService:
    from .jellyseerr_client import get_jellyseerr_client
    from .aniworld_client import get_aniworld_client
    from .mapper import RequestMapper

    settings = get_settings()
    db_session = get_db_session(settings.database_url)
    jellyseerr_client = get_jellyseerr_client()
    aniworld_client = get_aniworld_client()
    mapper = RequestMapper(aniworld_client)

    return BridgeService(jellyseerr_client, aniworld_client, mapper, db_session)
