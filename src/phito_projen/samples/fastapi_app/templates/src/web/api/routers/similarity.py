"""End points related to similarity."""
from dataclasses import dataclass
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, Query, Request
from starlette.status import HTTP_200_OK

from ben_similarity.default_constants import (
    MAX_ALLOWED_SIMILARITY_RESULTS_PER_PRODUCTION,
    MAX_PRODUCTIONS_IN_SIMILARITY_QUERY,
)
from ben_similarity.types import ProductionHost, TProductionHost
from ben_similarity.web.api.middleware import get_header_info
from ben_similarity.web.faiss_index import FaissIndex
from ben_similarity.web.models.app_services import AppServices
from ben_similarity.web.models.similarity_route.errors import ProductionNotFoundInFaissIndexError
from ben_similarity.web.models.similarity_route.similarity_response import (
    SimilarityJsonApiResponse,
    SimilarityProductionIdError,
    SimilarProductionResultItem,
    SimilarProductionsResult,
)
from ben_similarity.web.services.faiss_refresh.service import FaissRefreshService

router = APIRouter()


@dataclass
class SimilarityQueryParams:
    """Official, FastAPI-supported way of doing validation on key-value query parameters."""

    host: TProductionHost = Query(..., description="The host platform for the production IDs being submitted")
    production_ids: List[str] = Query(
        ...,
        description="Production IDs for which you wish to search for similar productions",
        max_length=MAX_PRODUCTIONS_IN_SIMILARITY_QUERY,
    )
    max_results_per_production: Optional[int] = Query(
        default=10,
        ge=1,
        le=MAX_ALLOWED_SIMILARITY_RESULTS_PER_PRODUCTION,
        description="Limit the number of similar productions for every returned production.",
    )


# pylint: disable=unused-argument
@router.get(
    "/api/v1/experimental/similarity/faiss",
    tags=["search"],
    response_model=SimilarityJsonApiResponse,
    status_code=HTTP_200_OK,
)
def faiss_search(request: Request, params: SimilarityQueryParams = Depends(SimilarityQueryParams)):
    """Find similar YouTube or Instagram productions."""
    services: AppServices = request.app.state.services
    faiss_refresher: FaissRefreshService = get_faiss_refresher(host=params.host, services=services)

    # download a new FAISS index if the index meant to be deployed has changed
    if faiss_refresher.needs_refresh():
        faiss_refresher.refresh_model_id_and_model()

    # for each production, get a collection of similar productions or an error
    similar_production_results: List[SimilarProductionsResult]
    similar_production_errors: List[SimilarityProductionIdError]
    similar_production_results, similar_production_errors = get_similarity_results_and_errors(
        production_ids=params.production_ids,
        faiss_index=faiss_refresher.faiss_index,
        max_results_per_production=params.max_results_per_production,
    )

    return SimilarityJsonApiResponse.make_success_response(
        similars_by_production_id=similar_production_results,
        errors_by_production_id=similar_production_errors,
        header_info=get_header_info(request),
        request=request,
    )


def get_faiss_refresher(host: TProductionHost, services: AppServices) -> FaissRefreshService:
    """
    Retrieve the correct FaissRefresherService object for the desired ``host``.

    :param host: a production host such as youtube or instagram
    :param services: all of the services available to the FastAPI app at request time
    """
    return services.yt_faiss_refresher if host == ProductionHost.youtube.value else services.ig_faiss_refresher


def get_similarity_results_and_errors(
    production_ids: List[str], faiss_index: FaissIndex, max_results_per_production: int
) -> Tuple[List[SimilarProductionsResult], List[SimilarityProductionIdError]]:
    """
    Run each production through a FAISS similarity search one at a time and return the results or an error for each.

    :param production_ids: productions for which to search for similar productions
    :param faiss_index: index of productions to use to search for results
    :param max_results_per_production: return no more than this many results per production
    """
    similarity_production_results: List[SimilarProductionsResult] = []
    similarity_production_errors: List[SimilarityProductionIdError] = []

    for production_id in production_ids:
        try:
            similarity_result_items: List[
                SimilarProductionResultItem
            ] = faiss_index.search_for_similar_productions(
                target_production_id=production_id, max_results=max_results_per_production
            )
            similarity_result = SimilarProductionsResult(
                target_production_id=production_id,
                similar_productions=similarity_result_items,
            )
            similarity_production_results.append(similarity_result)
        except ProductionNotFoundInFaissIndexError as e:
            similarity_production_errors.append(e.to_similarity_production_id_error())

    return similarity_production_results, similarity_production_errors
