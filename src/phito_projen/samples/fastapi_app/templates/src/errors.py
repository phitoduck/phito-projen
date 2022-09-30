"""Domain specific exceptions that are raised at runtime in the Similarity Service."""


class SimilarityServiceError(Exception):
    """Base exception for all Similarity Service errors."""

    ...


class FaissIndexError(SimilarityServiceError):
    """Raised when something goes wrong when dealing with a FAISS index."""

    ...
