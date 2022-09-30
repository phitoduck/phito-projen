"""Constants, logic, and Exception subclasses related specifically to error handling in the /similarity route."""

from dataclasses import dataclass

from starlette.status import HTTP_404_NOT_FOUND

from ben_similarity.errors import FaissIndexError
from ben_similarity.web.models.similarity_route.similarity_response import SimilarityProductionIdError


@dataclass(frozen=True)
class ProductionNotFoundInFaissIndexError(FaissIndexError):
    """Raised when a requested production ID is not present in the FAISS index."""

    message: str
    missing_production_id: str

    def to_similarity_production_id_error(self) -> SimilarityProductionIdError:
        """Create a Similarity-Production-Error from a Production-Not-Found-In-Faiss-Index error for a response."""
        return SimilarityProductionIdError(
            target_production_id=self.missing_production_id,
            status_code=HTTP_404_NOT_FOUND,
            detail=f"A production with ID '{self.missing_production_id}' has not been indexed for this host.",
        )
