"""An abstract ``Service`` class to manage stateful interactions with external services."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ben_similarity.config import Config


class Service(ABC):
    """
    Initialize a ``Service`` class, meant manage interactions with external services.

    Examples of external services include databases, authentication services,
    other REST APIs, file storage like S3.

    Each service has a :func:`Service.init()` method that is run once
    on application startup.
    """

    @abstractmethod
    def init(self, **kwargs):
        """
        Perform any setup required to interact with the external service.

        For a database, this could mean opening a connection and running a
        test query to ensure connectivity.
        """
        raise NotImplementedError("Not implemented!")

    @classmethod
    def from_config(cls, config: Config, **kwargs) -> Service:
        """
        Initialize the service using the global application configuration.

        The child class should be intelligent enough to access only the
        minimum required attributes from the global configuration.

        :param config: global application configuration for Similarity Service
        """
        raise NotImplementedError("Not implemented!")
