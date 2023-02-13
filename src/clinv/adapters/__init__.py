"""Store the exposed adapters."""

from typing import Dict, TypeVar

from .abstract import AbstractSource
from .aws import AWSSource
from .fake import FakeSource
from .risk import RiskSource

AdapterSource = TypeVar("AdapterSource", bound=AbstractSource)

# ignore: AdapterSource is unbound. I still don't know how to fix this
AVAILABLE_SOURCES: Dict[str, AdapterSource] = {  # type: ignore
    "risk": RiskSource,
    "aws": AWSSource,
    "fake": FakeSource,
}


__all__ = [
    "AVAILABLE_SOURCES",
    "AbstractSource",
    "AWSSource",
    "FakeSource",
    "RiskSource",
]
