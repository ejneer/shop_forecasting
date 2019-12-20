from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Dict, Generator, Union

from shop_forecasting.prioritizers import PrioritizedItem, Prioritizer


@dataclass(eq=False)
class RouterOperation:
    """One step of a manufacturing router."""

    work_center: "WorkCenter"
    router: "Router"
    sequence_number: int
    hours: float = 0.0


@dataclass(eq=False)
class Router:
    """A collection of manufacturing steps."""

    operations: Dict[int, RouterOperation]
    current_sequence: int
    next_sequence: int

    item_number: int = 0
    order_number: int = 0
    _iter_sequence: Generator = field(init=False)
    _complete_sentinel: int = -1

    def __post_init__(self):
        # TODO: is this premature optimization?
        self._iter_sequence = (
            seq
            for seq in self.operations.keys()
            if seq > self.current_sequence
            and self.current_sequence != self._complete_sentinel
        )

    def advance(self):
        """Move the current operation forward if router is not complete."""
        self.current_sequence = self.next_sequence
        if self.current_operation:
            self.current_operation.work_center.enqueue(self.current_operation)

        try:
            self.next_sequence = next(self._iter_sequence)
            # move this router into the next workcenter's queue
        except StopIteration:
            self.next_sequence = self._complete_sentinel

    @property
    def current_operation(self) -> Union[RouterOperation, None]:
        try:
            return self.operations[self.current_sequence]
        except KeyError:
            return None


@dataclass(eq=False)
class WorkCenter:
    """A group of related machines or processes that accomplish similar tasks."""

    queue: "PriorityQueue[PrioritizedItem]"
    name: str
    prioritizer: Prioritizer
    factory: "Factory"

    num_slots: int = 1
    available_slots: int = field(init=False)

    def __post_init__(self):
        self.available_slots = self.num_slots

    def dequeue(self) -> RouterOperation:
        """Returns next operation that can be worked in workcenter's queue."""
        return self.queue.get().item

    def enqueue(self, new_operation: RouterOperation) -> None:
        """Prioritize an operation and add it to the workcenter's queue."""
        prioritized_item = PrioritizedItem(0, new_operation)
        self.prioritizer.prioritize(prioritized_item)
        self.queue.put(prioritized_item)

        # begin work immediately if a slot is available
        if self.available_slots > 0:
            self.work_next()

    def work_next(self) -> None:
        """Remove an operation from the workcenter's queue to begin work on it."""
        if not self.queue.empty():
            self.factory.add_work_in_progress(self.dequeue())
            self.available_slots -= 1

    def free_slot(self) -> None:
        self.available_slots += 1
        self.work_next()


@dataclass
class Factory:
    """A group of workcenters that manages a flow of operations.
    
    A factory is reponsible for coordinating events happening across all work
    centers.  Namely, it maintains the order in which operations complete from
    a global perspective (i.e. the flow of time).
    """

    event_queue: "PriorityQueue[PrioritizedItem]"
    elapsed_hours: float = 0

    def add_work_in_progress(self, operation: RouterOperation) -> None:
        """Queue up an in work operation from a workcenter.
        
        Events are prioritized according to their completion times, defined by
        the time the operation takes to complete and how long they have been in
        the queue.  Incrementing the priority of new items by the elapsed time
        is analogous to decrementing the remaining time of all other operations
        in the queue, without the O(n) penalty upon every insertion.
        """
        self.event_queue.put(
            # operation priority == time when work started + how long work will take
            PrioritizedItem(operation.hours + self.elapsed_hours, operation)
        )

    def complete_next(self) -> bool:
        """Move elapsed time to the next operation completion."""
        if not self.event_queue.empty():
            next_item = self.event_queue.get()
            completed_operation = next_item.item

            time_worked = next_item.priority - self.elapsed_hours
            self.elapsed_hours += time_worked

            completed_operation.router.advance()
            completed_operation.work_center.free_slot()
            return True
        return False
