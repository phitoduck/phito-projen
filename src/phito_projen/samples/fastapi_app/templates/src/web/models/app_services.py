"""Model the stateful services that are present on ``app.state``."""

from dataclasses import dataclass

from ben_similarity.web.services.faiss_refresh.service import FaissRefreshService


@dataclass
class AppServices:
    """
    All :class:`Service` s scoped to the lifecycle of a Similarity Service FastAPI app.

    During requests, all interactions with external webservices are managed by :class:`Service`.
    """

    yt_faiss_refresher: FaissRefreshService
    ig_faiss_refresher: FaissRefreshService
