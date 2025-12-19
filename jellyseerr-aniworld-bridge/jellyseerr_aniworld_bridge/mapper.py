from typing import Dict, Optional, List
import logging

from .jellyseerr_client import JellyseerrClient
from .aniworld_client import AniWorldClientWrapper


class RequestMapper:
    def __init__(self, aniworld_client: AniWorldClientWrapper):
        self.aniworld_client = aniworld_client

    def _construct_search_query(self, request: Dict) -> Optional[str]:
        """Constructs a search query from a Jellyseerr request."""
        media_info = request.get("media", {})
        title = media_info.get("name")
        original_title = media_info.get("originalName")

        # Prioritize original (e.g., Japanese) title for anime
        query = original_title or title

        if not query or not query.strip():
            logging.warning(f"Could not construct a valid search query for request ID {request.get('id')}. Skipping.")
            return None

        return query.strip()

    def map_request_to_show(self, request: Dict) -> Optional[Dict]:
        """
        Maps a Jellyseerr request to a show on AniWorld.
        Returns the best matching show dictionary or None if no match is found.
        """
        search_query = self._construct_search_query(request)
        if not search_query:
            logging.error("Could not construct a search query from the request.")
            return None

        logging.info(f"Searching for '{search_query}' on AniWorld...")
        search_results = self.aniworld_client.find_show(search_query)

        if not search_results:
            logging.warning(f"No results found for '{search_query}'.")
            return None

        # For simplicity, we'll assume the first result is the correct one.
        # A more advanced implementation could use fuzzy matching or compare years.
        best_match = search_results[0]
        logging.info(f"Found a match for '{search_query}': {best_match.get('name')}")

        return best_match
