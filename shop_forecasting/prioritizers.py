from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any


@dataclass(order=True)
class PrioritizedItem:
    """Generic wrapper for any data, providing a field to indicate priority."""

    priority: float
    item: Any = field(compare=False)


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


class ShortestProcessingTimePrioritizer(Prioritizer):
    """Prioritize items by shortest processing time, shorter being higher priority."""

    def prioritize(self, prioritized_item: PrioritizedItem) -> None:
        prioritized_item.priority = prioritized_item.item.hours


class EarliestDueDatePrioritizier(Prioritizer):
    """Prioritizes items based upon a given due date, earlier being higher priority.
    
    This relies on the prioritized item having a due_date property of a type
    that supports equality comparisons.
    """

    def prioritize(self, prioritized_item: PrioritizedItem) -> None:
        prioritized_item.priority = prioritized_item.item.due_date
