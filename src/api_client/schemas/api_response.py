from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class ApiClientResponse(Generic[T]):
    """Raw API response container for upper layers."""

    status_code: int
    data: T
