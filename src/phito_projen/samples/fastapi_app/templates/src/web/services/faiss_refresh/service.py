"""Define the :class:`FaissRefreshService`."""

from __future__ import annotations

from typing import Optional, Type

from godrics_hollow import GodricsHollow

from ben_similarity.config import LOGGER, Config
from ben_similarity.types import ProductionHost
from ben_similarity.web.faiss_index import FaissIndex
from ben_similarity.web.services.faiss_refresh.load_faiss import (
    fetch_current_model_id,
    load_faiss_index_from_model_registry,
    load_faiss_production_ids_from_model_registry,
)
from ben_similarity.web.services.service import Service


class FaissRefreshService(Service):
    """See ``__init__()``."""

    def __init__(
        self,
        host: ProductionHost,
        model_id_gh_secret: str,
        faiss_bucket: str,
        gh: Optional[GodricsHollow] = None,
    ):
        """
        Service for downloading the version of the FAISS faiss_index that should be in production.

        :param model_id_gh_secret: ID of the Godrics Hollow secret used to the FAISS faiss_index model ID.
        :param faiss_bucket: the S3 bucket identifier containing the model weights
        :param gh: an optional GodricsHollow instance for overriding default behavior when testing
        """
        self.host = host
        self.faiss_bucket: str = faiss_bucket
        self.model_id_gh_secret: str = model_id_gh_secret

        # to be fetched
        self.faiss_index: Optional[FaissIndex] = None
        self.model_id: Optional[str] = None

        # for unit testing
        self.gh: Optional[GodricsHollow] = gh

    @staticmethod
    def get_gh_secret_id(host: ProductionHost, config: Config) -> str:
        """Return the correct GodricsHollow secret from the ``config`` based on the ``host``."""
        model_id_gh_secret: Optional[str] = None
        if host == ProductionHost.youtube:
            model_id_gh_secret = config.youtube_gh_secret_id
        elif host == ProductionHost.instagram:
            model_id_gh_secret = config.instagram_gh_secret_id
        return model_id_gh_secret

    # pylint: disable=arguments-differ
    @classmethod
    def from_config(
        cls: Type[FaissRefreshService], host: ProductionHost, config: Config
    ) -> FaissRefreshService:
        """
        Create a :class:`FaissRefreshService` from a global Config object (factory).

        :param host: the platform which the FAISS faiss_index is meant for (``yt``, ``ig``, etc.)
        :param config: configuration for the entire Similarity Service
        """
        model_id_gh_secret: str = FaissRefreshService.get_gh_secret_id(host=host, config=config)
        return cls(model_id_gh_secret=model_id_gh_secret, faiss_bucket=config.model_bucket, host=host)

    def init(self):
        """Download models to be used in inference."""
        self.refresh_model_id_and_model()

    def refresh_model_id_and_model(self):
        """Load the latest model ID and model from the registry."""
        self.model_id = fetch_current_model_id(gh_secret_id=self.model_id_gh_secret, gh=self.gh)

        # prepare a new FaissIndex wrapper to run inferences using the FAISS weights
        logged_data = {
            "model-id": self.model_id,
            "host": self.host.value,
            "bucket": self.faiss_bucket,
        }
        LOGGER.bind(**logged_data).info("Fetching FAISS index and associated production IDs.")
        self.faiss_index = FaissIndex.from_data(
            faiss_index=load_faiss_index_from_model_registry(
                bucket=self.faiss_bucket, model_id=self.model_id, host=self.host
            ),
            production_ids=load_faiss_production_ids_from_model_registry(
                bucket=self.faiss_bucket, model_id=self.model_id, host=self.host
            ),
        )

    def needs_refresh(self) -> bool:
        """Return ``True`` if a newer version of the model is available."""
        newest_model_id = fetch_current_model_id(gh_secret_id=self.model_id_gh_secret, gh=self.gh)
        return newest_model_id != self.model_id
