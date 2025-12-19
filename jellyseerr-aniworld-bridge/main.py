import uvicorn
import sys
from jellyseerr_aniworld_bridge.config import get_settings
from jellyseerr_aniworld_bridge.webapp.main import app

if __name__ == "__main__":
    settings = get_settings()
    reload = "--reload" in sys.argv
    uvicorn.run(
        "jellyseerr_aniworld_bridge.webapp.main:app",
        host="0.0.0.0",
        port=settings.web_port,
        reload=reload,
    )
