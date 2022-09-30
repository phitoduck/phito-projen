"""Models for JSON:API response body."""

from typing import Any, Dict, Optional, Type, Union

import fastapi

# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
from pydantic import BaseModel, Field
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ben_similarity.web.models.middleware import CustomHeaderInfo


class ErrorSource(BaseModel):
    """Potentially point to the source of the error and provide additional information."""

    pointer: str
    parameters: str

    @classmethod
    def from_request(
        cls: Type["ErrorSource"],
        request: fastapi.Request,
    ) -> "ErrorSource":
        """Create an ErrorSource using the FastAPI request object."""
        return ErrorSource(pointer=str(request.url.path), parameters=str(request.query_params))


class JsonApiError(BaseModel):
    """Error schema used in JSON:API compliant responses."""

    class Config:
        """pydantic approach to configuring the behavior of a model."""

        frozen = True

    request_id: str = Field(description="The id given to the specific request that generated the error.")
    status_code: int = Field(
        default=HTTP_500_INTERNAL_SERVER_ERROR, description="The HTTP status code associated with the error."
    )
    title: str = Field(description="A common page_help for the error type.")
    detail: Union[str] = Field(description="Specific information for error troubleshooting.")

    source: Optional[ErrorSource] = Field(
        default=None, description="Optional pointer to the source of the error."
    )
    meta: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional information to assist with discovering the error."
    )


class JsonApiResponse(BaseModel):
    """Response body set forth by the JSON:API standard."""

    data: Optional[Any] = Field(
        default=None, description="The data object holds the information that was requested by the caller."
    )
    meta: Any = Field(
        default=None, description="Metadata holds information about the data, its shape, for example."
    )
    error: Optional[JsonApiError] = Field(
        default=None,
        description="If an error occurs, troubleshooting information will be found in the error object.",
    )

    @classmethod
    def make_error_response(
        cls: Type["JsonApiResponse"],
        status_code: int,
        header_info: CustomHeaderInfo,
        request: fastapi.Request,
        error_title: str,
        error_detail: Any,
    ) -> "JsonApiResponse":
        """Create an error response that will suffice for most error cases."""
        return JsonApiResponse(
            data=None,
            meta=None,
            error=JsonApiError(
                request_id=header_info.request_id,
                status_code=status_code,
                source=ErrorSource.from_request(request=request),
                meta=None,
                title=error_title,
                detail=error_detail,
            ),
        )
