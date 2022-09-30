"""Centralized configuration manager for the Similarity Service."""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from godrics_hollow import GodricsHollow

# pylint: disable=no-name-in-module
from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable
from river_pig.river_pig import RiverPig

from ben_similarity.default_constants import (
    DEFAULT__INSTAGRAM_MODEL__GH_SECRET_ID,
    DEFAULT__YOUTUBE_MODEL__GH_SECRET_ID,
    MODEL_BUCKET_GH_SECRET,
)
from ben_similarity.utilities import get_project_base

# config from environment variables will be prefixed with this
# the remainder will be the attribute names on the Config class
# e.g. SS__ENVIRONMENT
ENVIRONMENT_VARIABLE_PREFIX = "SS__"

# default config file to use if no override is provided in env vars
DEFAULT_CONFIG_PATH = Path(get_project_base(), "config.yml")

# allow override of the similarity service config file using env vars
CONFIG_PATH_OVERRIDE_ENV_VAR = ENVIRONMENT_VARIABLE_PREFIX + "CONFIG_FILE"

# create global logging object to use in all modules
LOGGER = RiverPig.from_secrets(
    name="similarity-service",
    ignore=["commit_id"],
).logger


class Environments(str, Enum):
    """Provide a choice of allowable deployment environments."""

    local = "local"
    dev = "development"
    prod = "production"
    localint = "local_integration"


# pylint: disable=unused-argument
def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    App settings from the yaml config file.

    This function matches the signature of a ``pydantic.SourceProviderCallable``
    and can therefore be used to provide config values to a ``pydantic.BaseSettings``
    object.

    :param settings: other settings present in the BaseSettings object
        from previously executed config providers. This is a required
        argument for a function to match the SourceProviderCallable
        signature.
    """
    config_path = Path(os.environ.get(CONFIG_PATH_OVERRIDE_ENV_VAR, DEFAULT_CONFIG_PATH))
    with Path(config_path).open(mode="r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        return config


class Config(BaseSettings):
    """
    Pydantic's approach to managing application configuration.

    See the pydantic.BaseSettings docs here:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """

    # environment the Similarity Service is being run in
    environment: Environments

    # whether to log the request body when logging
    log_request_body: bool = False

    # secrets detailing which model weights to use for inferencing
    youtube_gh_secret_id: str = DEFAULT__YOUTUBE_MODEL__GH_SECRET_ID
    instagram_gh_secret_id: str = DEFAULT__INSTAGRAM_MODEL__GH_SECRET_ID

    __model_bucket: Optional[str] = None

    @property
    def model_bucket(self) -> str:
        """Lazy fetch global name of the S3 bucket for model weights (in the appropriate environment)."""
        # fetch the model bucket location if not present
        if not self.__dict__.get("__model_bucket"):
            gh = GodricsHollow()
            self.__dict__["__model_bucket"] = gh.get_secret(MODEL_BUCKET_GH_SECRET)["bucket"]
        return self.__dict__["__model_bucket"]

    class Config:
        """Pydantic's approach to customize our subclass of BaseSettings."""

        # read env vars matching SS__<some attr name>, e.g. SS__LOG_REQUEST_BODY -> Config.log_request_body
        env_prefix = ENVIRONMENT_VARIABLE_PREFIX

        # allow any casing for environment variables, e.g. SS__log_request_body or SS__Log_Request_BODY
        case_sensitive = False

        # use the ``.value`` property from Enum attributes rather than the raw enum
        use_enum_values = True

        # lock Config attributes so that they are constants after being set
        frozen = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """
            Register Pydantic config providers.

            Config providers will be prioritized in the order they are returned here.

            ``customize_sources`` is a :class:`BaseSettings` Lifecycle method
            that allows you to add custom sources of config besides environment variables
            and ``Config.__init__`` parameters. In our case, we also get config values
            from a YAML file.

            The Pydantic docs provide a tutorial and explanation of how to set this up:
            https://pydantic-docs.helpmanual.io/usage/settings/#adding-sources

            :param init_settings: __init__ kwargs passed to this Pydantic model on instantiation
            :param env_settings: key value pairs discovered from environment variables
                (only env vars beginning with the ``env_prefix`` are used)
            :param file_secret_settings:
            """
            return (
                # priority #1 -- kwargs to Config() constructor
                init_settings,
                # priority #2 -- environment variable versions of config values
                env_settings,
                # priority #3 -- values from yaml config file
                yaml_config_settings_source,
                # priority #4
                file_secret_settings,
            )
