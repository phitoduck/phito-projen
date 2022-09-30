"""Domain specific types for the Similarity Service."""

from enum import Enum
from typing import Literal

TProductionHost = Literal["yt", "ig"]


class ProductionHost(str, Enum):
    """Social media productions for which similars are searched for."""

    youtube = "yt"
    instagram = "ig"
