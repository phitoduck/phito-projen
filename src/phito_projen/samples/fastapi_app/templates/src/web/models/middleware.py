"""Models used in FastAPI middleware."""

# pylint: disable=no-name-in-module, unused-argument

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


def get_timestamp(dt: datetime) -> str:
    """Parse datetime to ISO formatted date string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")


class CustomHeaderInfo(BaseModel):
    """Custom headers kept on ``request.app.state``."""

    request_id: str
    start_time: datetime = datetime.now()
    end_time: Optional[datetime] = None

    @property
    def process_time(self) -> float:
        """Return the number of seconds between start and end time as a decimal number."""
        delta = (self.end_time - self.start_time).total_seconds()
        return delta

    @property
    def iso_start_time(self) -> str:
        """Return ISO formatted start time."""
        return get_timestamp(self.start_time)

    @property
    def iso_end_time(self) -> str:
        """Return ISO formatted end time."""
        return get_timestamp(self.end_time)
