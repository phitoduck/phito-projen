"""
Define middleware steps for all API endpoints.

In this context, middleware is a series of methods that are run either before or after
executing the route. The perform operations such as adding state variables, logging,
and global exception handling.
"""


import uuid
from datetime import datetime
from typing import Callable

from starlette.requests import Request
from starlette.responses import JSONResponse

# redefining health check endpoint here to prevent circular import from main
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ben_similarity.config import LOGGER, Config
from ben_similarity.web.models.json_api import JsonApiResponse
from ben_similarity.web.models.middleware import CustomHeaderInfo

HEALTH_CHECK_ROUTE = "/status"

get_header_info: Callable[[Request], CustomHeaderInfo] = lambda request: request.app.state.custom_header_info


async def add_custom_header_info(request: Request, call_next: Callable) -> JSONResponse:
    """
    Add custom header information to the incoming request object to ``request.app.state``.

    This middleware is meant to be called in advance of middlewares
    that rely on the :class:`CustomHeaderInfo` instance to be present
    on ``request.app.state``.
    """
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    request.app.state.custom_header_info = CustomHeaderInfo(
        request_id=request_id,
        start_time=start_time,
    )
    return await call_next(request)


async def add_response_headers(request: Request, call_next: Callable):
    """
    Add headers to the ``request.app.state`` object.

    These include the ``X-Process-Time`` and ``X-Response-ID`` headers.
    """
    header_info: CustomHeaderInfo = get_header_info(request)
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(header_info.process_time, 3))
    response.headers["X-Response-ID"] = header_info.request_id
    return response


async def log_request(request: Request, call_next: Callable) -> JSONResponse:
    """
    Log all incoming requests to the API.

    .. note:: This is called after header information is added but before any route is executed.
    """
    config: Config = request.app.state.config
    if config.log_request_body:
        request_body = await request.body()
        request_body = request_body.decode("utf-8")
    else:
        request_body = None

    header_info: CustomHeaderInfo = get_header_info(request)

    info = dict(
        request_id=header_info.request_id,
        start_time=header_info.iso_start_time,
        url=request.url,
        host=request.client.host,
        port=request.client.port,
        request_body=request_body,
    )

    if request.url.path != HEALTH_CHECK_ROUTE:
        LOGGER.bind(**info).info(f"Incoming request: id = {info['request_id']}")

    return await call_next(request)


async def log_response(request: Request, call_next: Callable) -> JSONResponse:
    """Log metadata about the API response object."""
    header_info: CustomHeaderInfo = get_header_info(request)
    request_id = header_info.request_id

    response = await call_next(request)

    header_info.end_time = datetime.now()
    info = dict(
        request_id=request_id,
        start_time=header_info.iso_start_time,
        end_time=header_info.iso_end_time,
        process_time=round(header_info.process_time, 3),
        status_code=response.status_code,
    )

    if request.url.path != HEALTH_CHECK_ROUTE:
        LOGGER.bind(**info).info(f"Completed request: id = {request_id}")

    return response


async def global_error_handler(request: Request, call_next: Callable) -> JSONResponse:
    """Execute the FastAPI route, and handle any uncaught exceptions that are raised in the route."""
    try:
        return await call_next(request)
    # pylint: disable=broad-except
    except Exception as e:
        LOGGER.error(e)
        # pylint: disable=fixme
        # TODO -- will this cause the API to return a non-200 status code?
        return JsonApiResponse.make_error_response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            header_info=get_header_info(request),
            request=request,
            error_title="INTERNAL_SERVER_ERROR",
            error_detail="A runtime error occured while handling the request. To troubleshoot, search for the request ID in the logs.",
        )
