import logging
from pathlib import Path
from typing import List, Dict, Optional
from argparse import Namespace

from aniworld.search import search_media
from aniworld.menu import menu
from aniworld.models import Anime, Episode
from aniworld.action.download import download as download_action
from aniworld.config import ANIWORLD_TO

from .config import get_settings

class AniWorldClientWrapper:
    def __init__(self, download_path: str):
        self.download_path = Path(download_path)
        # The new library doesn't need the arguments object to be configured globally.
        # Instead, we pass the necessary options to the functions that need them.

    def find_show(self, query: str) -> List[Dict]:
        """
        Finds shows on AniWorld based on a search query.
        """
        try:
            results = search_media(keyword=query, only_return=True)
            return [r for r in results if r.get("type") == "anime"]
        except Exception as e:
            logging.error(f"Error finding show on AniWorld: {e}")
            return []

    def download_episode(self, show: Dict, season_number: int, episode_number: int, progress_callback=None) -> Optional[Path]:
        """
        Downloads a specific episode of a show and returns the file path.
        """
        try:
            anime_slug = show.get("link")
            if not anime_slug:
                logging.error("Show dictionary is missing the 'link' key.")
                return None

            if anime_slug.startswith("/"):
                anime_slug = anime_slug[1:]

            # The menu function now requires an arguments object.
            # We can create a simple Namespace object with the necessary attributes.
            args = Namespace(
                language="de",
                provider="Vidoza",
                action="Download",
                aniskip=False,
                keep_watching=False
            )
            parsed_anime = menu(arguments=args, slug=anime_slug)

            if not parsed_anime:
                logging.error(f"Could not parse anime details from slug: {anime_slug}")
                return None

            target_episode: Optional[Episode] = None
            for episode in parsed_anime:
                if episode.season == season_number and episode.episode == episode_number:
                    target_episode = episode
                    break

            if not target_episode:
                logging.warning(f"Episode S{season_number:02}E{episode_number:02} not found for {parsed_anime.title}")
                return None

            # Create a new Anime object containing only the episode to download.
            anime_to_download = Anime(
                title=parsed_anime.title,
                slug=parsed_anime.slug,
                episode_list=[target_episode]
            )

            # The download action creates the file path, so we need to construct it
            # to return it.
            from aniworld.common import sanitize_filename
            sanitized_title = sanitize_filename(anime_to_download.title)
            filename = f"{sanitized_title} - S{season_number:02}E{episode_number:03} - ({args.language}).mp4"
            expected_filepath = self.download_path / sanitized_title / filename

            # The download function from the library needs the output_dir to be set in the arguments.
            from aniworld.parser import arguments
            arguments.output_dir = str(self.download_path)

            logging.info(f"Starting download of {filename}")
            download_action(anime_to_download, web_progress_callback=progress_callback)
            logging.info(f"Finished download of {filename}")

            return expected_filepath

        except Exception as e:
            logging.error(f"An error occurred during download: {e}")
            return None


def get_aniworld_client() -> AniWorldClientWrapper:
    settings = get_settings()
    return AniWorldClientWrapper(download_path=settings.download_path)
