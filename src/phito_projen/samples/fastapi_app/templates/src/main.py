"""Entrypoint for Similarity Service API."""

from typing import Optional

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from ben_similarity.config import Config
from ben_similarity.types import ProductionHost
from ben_similarity.web.api import middleware
from ben_similarity.web.api.routers import similarity
from ben_similarity.web.models.app_services import AppServices
from ben_similarity.web.services.faiss_refresh.service import FaissRefreshService


async def root():  # pragma: no cover
    """Root of API that redirects to the docs page."""
    response = RedirectResponse(url="/docs")
    return response


async def status():  # pragma: no cover
    """Health check endpoint."""
    return {"status": "Similarity Service API is running"}


def create_app(
    config: Optional[Config] = None,
    yt_refresher: Optional[FaissRefreshService] = None,
    ig_refresher: Optional[FaissRefreshService] = None,
) -> FastAPI:
    """
    Create and configure a FastAPI application for Similarity Service.

    :param config: Similarity Service global configuration
    :param yt_refresher: FAISS refresher for ``yt`` (for testing)
    :param ig_refresher: FAISS refresher for ``ig`` (for testing)

    :return: FastAPI application with global state, routes, and lifecycle events
    """
    app = FastAPI()

    if not config:
        config = Config()

    # attach configuration and stateful services to the global app state
    app.state.config = config
    app.state.services = AppServices(
        yt_faiss_refresher=yt_refresher
        or FaissRefreshService.from_config(host=ProductionHost.youtube, config=config),
        ig_faiss_refresher=ig_refresher
        or FaissRefreshService.from_config(host=ProductionHost.instagram, config=config),
    )

    # prepare to initialize the stateful services on startup
    @app.on_event("startup")
    def init_services():
        app.state.services.ig_faiss_refresher.init()
        app.state.services.yt_faiss_refresher.init()

    # register routes on app
    app.include_router(similarity.router)
    app.get("/status")(status)
    app.get("/")(root)

    # register middleware on app: these are executed in reverse order that they are registered
    app.middleware("http")(middleware.global_error_handler)
    app.middleware("http")(middleware.log_response)
    app.middleware("http")(middleware.add_response_headers)
    app.middleware("http")(middleware.log_request)
    app.middleware("http")(middleware.add_custom_header_info)

    return app


if __name__ == "__main__":
    # import uvicorn

    # api: FastAPI = create_app()
    # uvicorn.run(api, host="0.0.0.0", port=8080)

    from pathlib import Path

    import boto3
    import joblib

    run_id = "1636149331201022"
    bucket = "stagecoachglobalresource-artifactstoreforstagecoa-57y9iq0btnog"
    channels_url = f"yt-graphs/faiss_index-production-ids/yt_graph_channels_{run_id}.p"
    s3 = boto3.client("s3")

    THIS_DIR = Path(__file__).parent
    out_dir = Path("yt-graphs/faiss_index-production-ids")
    out_dir.mkdir(exist_ok=True)

    # Download the map from faiss_index number to username
    s3.download_file(
        bucket,
        channels_url,
        Filename=str(out_dir / Path(channels_url).name),
    )

    # Load in the instagram graph
    with open(channels_url, "rb") as f:
        channels = joblib.load(f)
        print("success")
