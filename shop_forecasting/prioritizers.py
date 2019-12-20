from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any


@dataclass(order=True)
class PrioritizedItem:
    """Generic wrapper for any data, providing a field to indicate priority."""

    priority: float
    item: Any = field(compare=False)


@dataclass
class Prioritizer(ABC):
    """Interface definition that all prioritizers must implement."""

    @abstractmethod
    def prioritize(self, prioritized_item: PrioritizedItem) -> None:
        pass


@dataclass
class FifoPrioritizer(Prioritizer):
    """Prioritizes items in a first-in-first-out manner."""

    queue_count: int = 0

    def prioritize(self, prioritized_item: PrioritizedItem) -> None:
        prioritized_item.priority = self.queue_count
        self.queue_count += 1
