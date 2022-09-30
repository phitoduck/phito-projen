"""Models used to form the response of the /similarity route."""

from typing import Any, List, Optional, Type

import fastapi

# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
from pydantic import BaseModel, Field
from starlette.status import HTTP_200_OK

from ben_similarity.web.models.json_api import ErrorSource, JsonApiError
from ben_similarity.web.models.middleware import CustomHeaderInfo

# similarity request error titles
SOME_PRODUCTION_ERRORS = "FAILED_ON_SOME_PRODUCTIONS"
ALL_PRODUCTIONS_FAILED = "ALL_PRODUCTIONS_FAILED"
ALL_PRODUCTIONS_SUCCEEDED = "ALL_PRODUCTIONS_SUCCEEDED"


def get_similarity_error_title(num_successful_productions: int, num_failed_productions: int) -> str:
    """Return the correct error title given the number of successful and failed productions that occurred."""
    if num_successful_productions == 0 and num_failed_productions > 0:
        return ALL_PRODUCTIONS_FAILED
    if num_successful_productions > 0 and num_failed_productions == 0:
        return ALL_PRODUCTIONS_SUCCEEDED
    return SOME_PRODUCTION_ERRORS


class SimilarityProductionIdError(BaseModel):
    """Error type explaining why the SS failed to return similar productions for a specific production ID."""

    class Config:
        """pydantic approach to configuring BaseModel subclasses."""

        frozen = True

    target_production_id: str = Field(
        description="ID of production for which similar productions failed to be retrieved due to an error."
    )
    status_code: int = Field(
        description="An HTTP status code whose reason most closely aligns with the cause of failure."
    )
    detail: str = Field(description="High-level description of what caused the failure.")


class Error(JsonApiError):
    """Error schema used in JSON:API compliant responses."""

    detail: List[SimilarityProductionIdError] = Field(
        description="Specific information for error troubleshooting."
    )


class SimilarProductionResultItem(BaseModel):
    """A single similarity result containing information about one production similar to the target production."""

    production_id: str = Field(description="ID of productions similar to the target production.")
    distance: float = Field(
        description="Measure of how dissimilar this production is from the target production."
    )

    def __eq__(self, other: "SimilarProductionResultItem") -> bool:
        """Check equality of to ``SimilarProductionResultItem`` objects."""
        return self.production_id == other.production_id and self.distance == other.distance


class SimilarProductionsResult(BaseModel):
    """Portion of response that contains the similarity results for a single production ID."""

    target_production_id: str = Field(description="ID of production who results are similar to.")
    similar_productions: List[SimilarProductionResultItem] = Field(
        description="Productions similar to the target production."
    )


class SimilarityJsonApiResponse(BaseModel):
    """
    Respond to each api call with a consistently shaped model consisting of data, metadata, and errors.

    The JSON:API specification insists that the response from any api call be consistent at its top level.
    Inside this top-level object are request-specific results in the form of data, metadata, and errors.

    .. note:  There will be a data object or an error object, not both.
    """

    data: Optional[List[SimilarProductionsResult]] = Field(
        default=None, description="The data object holds the information that was requested by the caller."
    )
    meta: Any = Field(
        default=None, description="Metadata holds information about the data, its shape, for example."
    )
    error: Optional[Error] = Field(
        default=None,
        description="If an error occurs, troubleshooting information will be found in the error object.",
    )

    @classmethod
    def make_success_response(
        cls: Type["SimilarityJsonApiResponse"],
        errors_by_production_id: List[SimilarityProductionIdError],
        similars_by_production_id: List[SimilarProductionsResult],
        header_info: CustomHeaderInfo,
        request: fastapi.Request,
    ) -> "SimilarityJsonApiResponse":
        """Create a JSON:API success response for a similarity request."""
        return SimilarityJsonApiResponse(
            data=similars_by_production_id,
            meta=None,
            error=Error(
                detail=errors_by_production_id,
                status_code=HTTP_200_OK,
                source=ErrorSource.from_request(request=request),
                title=get_similarity_error_title(
                    num_successful_productions=len(similars_by_production_id),
                    num_failed_productions=len(errors_by_production_id),
                ),
                request_id=header_info.request_id,
                meta={},
            ),
        )
