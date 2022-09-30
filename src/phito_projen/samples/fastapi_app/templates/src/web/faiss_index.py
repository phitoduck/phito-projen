"""Logic relating to using a FAISS index for inference."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Type, Union

import numpy as np
from faiss import IndexIVF

from ben_similarity.default_constants import DEFAULT__MAX_SIMILARITY_RESULTS
from ben_similarity.web.models.similarity_route.errors import ProductionNotFoundInFaissIndexError
from ben_similarity.web.models.similarity_route.similarity_response import SimilarProductionResultItem


@dataclass(frozen=True)
class FaissIndex:
    """Wrapper around the ``faiss`` library to easily run inferences with a FAISS index (searches)."""

    faiss_index: Union[IndexIVF]
    production_ids: List[str]
    embedding_dimension: int
    production_ids_to_indices: Dict[str, int]

    @classmethod
    def from_data(cls: Type[FaissIndex], faiss_index: IndexIVF, production_ids: List[str]) -> FaissIndex:
        """Create a FaissIndex wrapper from a ``faiss_index`` object and its ``production_ids``."""
        return cls(
            faiss_index=faiss_index,
            production_ids=production_ids,
            embedding_dimension=get_faiss_embedding_dimension(faiss_index),
            production_ids_to_indices={_id: idx for idx, _id in enumerate(production_ids)},
        )

    def search_for_similar_productions(
        self, target_production_id: str, max_results: int = DEFAULT__MAX_SIMILARITY_RESULTS
    ) -> List[SimilarProductionResultItem]:
        """
        Query the FAISS faiss_index for productions similar to ``target_production_id``.

        :raises FaissIndexError: if the number of max_results is greater than the number
            of production IDs in the Faiss index.

        :param target_production_id: Similarity results will be similar to this production ID.
        :param max_results: Upper bound on the number of similarity results that should be returned.
            Note, this number must not be greater than the total number of production IDs in the index.

        :return: A list of of production IDs similar to the ``target_production_id``.
        """
        if target_production_id not in self.production_ids:
            raise ProductionNotFoundInFaissIndexError(
                message=f"The production ID '{target_production_id}' is not in the FAISS index",
                missing_production_id=target_production_id,
            )

        if max_results >= len(self.production_ids):
            max_results = len(self.production_ids) - 1

        query_vector: np.ndarray = self.faiss_index.reconstruct(
            self.production_ids_to_indices[target_production_id]
        ).reshape(1, self.embedding_dimension)

        # add one to max results because the target_production_id is *always* returned
        # because a production is perfectly similar to itself
        _max_results = max_results + 1

        # find up to _max_results productions closest to the target production
        distances: np.ndarray  # 1 x N array; where N <= max_results + 1
        production_id_indices: np.ndarray  # 1 x N array; where N <= max_results + 1
        distances, production_id_indices = self.faiss_index.search(query_vector, _max_results)

        # remove the target production from results
        closest_production_indices_without_target = production_id_indices[0][1:]
        closest_production_distances_without_target: np.array = distances[0][1:]

        # collect the distances and production ids together in a list of results
        similar_production_results: List[SimilarProductionResultItem] = [
            SimilarProductionResultItem(
                production_id=self.production_ids[p_id_index],
                distance=distance,
            )
            for p_id_index, distance in zip(
                closest_production_indices_without_target, closest_production_distances_without_target
            )
        ]

        return similar_production_results


def get_faiss_embedding_dimension(faiss_index: IndexIVF) -> int:
    """Return the number of entries in the embedding vectors of the ``faiss_index``."""
    faiss_index.make_direct_map()
    sample_embedding: np.ndarray = faiss_index.reconstruct(0)
    return len(sample_embedding)
