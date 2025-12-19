# Jellyseerr AniWorld Bridge

A service that connects Jellyseerr to AniWorld Downloader, automating the process of fulfilling anime requests.

## Features

-   Automatically fetches pending requests from Jellyseerr.
-   Maps Jellyseerr requests to AniWorld shows.
-   Downloads episodes/seasons/movies using the `aniworld-downloader` library.
-   Marks requests as "available" in Jellyseerr upon successful download.
-   Provides a web interface to monitor and manage download jobs.

## How it works

The service periodically polls the Jellyseerr API for approved requests. For each request, it attempts to find a matching show on AniWorld. If a match is found, it creates download jobs for the requested episodes. The downloaded files are stored in a configurable directory, and the request is marked as available in Jellyseerr.

The web interface provides a dashboard to view the status of all download jobs, including progress, speed, and any errors. It also allows for canceling and retrying jobs.

## Environment Variables

The following environment variables are used for configuration:

| Variable            | Description                                   | Default     |
| ------------------- | --------------------------------------------- | ----------- |
| `JELLYSEERR_URL`    | The base URL of your Jellyseerr instance.     | (required)  |
| `JELLYSEERR_API_KEY`| Your Jellyseerr API key.                      | (required)  |
| `DOWNLOAD_PATH`     | The directory where anime should be downloaded. | `/data/anime` |
| `POLL_INTERVAL`     | The interval in seconds to poll Jellyseerr.   | `60`        |
| `WEB_PORT`          | The port for the web interface.               | `8081`      |

## Usage

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/jellyseerr-aniworld-bridge.git
    cd jellyseerr-aniworld-bridge
    ```

2.  **Configure environment variables:**

    Create a `.env` file in the root of the project and add the required environment variables:

    ```
    JELLYSEERR_URL=http://your-jellyseerr-host:5055
    JELLYSEERR_API_KEY=your-api-key
    ```

**Note on Docker Networking:** When running this service in Docker, `localhost` in the `JELLYSEERR_URL` will not connect to a service running on your host machine. Use `http://host.docker.internal:5055` instead. This special DNS name resolves to your host machine's IP from within the Docker container.

3.  **Run with Docker Compose:**

    ```bash
    docker-compose up --build
    ```

The web interface will be available at `http://localhost:8081`.
