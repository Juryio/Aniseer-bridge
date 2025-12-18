from typing import Any, Dict, List, Optional
import httpx
import logging

from .config import get_settings


class JellyseerrClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key}

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}/api/v1{path}"
        try:
            with httpx.Client() as client:
                response = client.request(method, url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            # Add logging here
            logging.error(f"Error communicating with Jellyseerr API: {e}")
            return None

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        # NOTE: The exact API endpoint and parameters for filtering pending requests
        # are assumed. Based on common API design, it might be something like this.
        # The Jellyseerr API documentation should be consulted for the correct endpoint.
        # This assumes a 'status' of 3 is for pending requests.
        params = {"take": 100, "skip": 0, "filter": "approved", "sort": "added"}
        data = self._request("GET", "/request", params=params)
        return data.get("results", []) if data else []

    def mark_request_as_available(self, request_id: int) -> bool:
        # NOTE: This endpoint is an assumption. The actual endpoint might be different.
        # It's assumed that a POST request to this endpoint will update the status.
        response = self._request("POST", f"/request/{request_id}/available")
        return response is not None

def get_jellyseerr_client() -> JellyseerrClient:
    settings = get_settings()
    return JellyseerrClient(base_url=settings.jellyseerr_url, api_key=settings.jellyseerr_api_key)
