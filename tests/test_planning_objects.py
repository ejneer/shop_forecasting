from queue import PriorityQueue
from shop_forecasting.prioritizers import PrioritizedItem
import pytest
from unittest.mock import Mock
from shop_forecasting.planning_objects import (
    Factory,
    Router,
    RouterOperation,
    WorkCenter,
)


def operation_stub(seq_num, hours):
    """Convenience test function, returns an operation with a mock router and workcenter."""
    return RouterOperation(
        work_center=Mock(WorkCenter),
        router=Mock(Router),
        sequence_number=seq_num,
        hours=hours,
    )


raw_material = operation_stub(seq_num=10, hours=0)
machine = operation_stub(seq_num=20, hours=5)
pack_and_ship = operation_stub(seq_num=30, hours=5)
ops = {op.sequence_number: op for op in [raw_material, machine, pack_and_ship]}


@pytest.fixture
def router_at_beginning() -> Router:
    router = Router(operations=ops, current_sequence=10, next_sequence=20)
    return router


@pytest.fixture
def router_at_middle() -> Router:
    router = Router(operations=ops, current_sequence=20, next_sequence=30)
    return router


@pytest.fixture
def router_at_end() -> Router:
    router = Router(operations=ops, current_sequence=30, next_sequence=-1)
    return router


def test_router_move_next(router_at_beginning: Router):
    assert router_at_beginning.current_sequence == 10
    assert router_at_beginning.next_sequence == 20
    router_at_beginning.advance()
    assert router_at_beginning.current_sequence == 20
    assert router_at_beginning.next_sequence == 30


def test_router_move_next_to_last_operation(router_at_middle: Router):
    assert router_at_middle.current_sequence == 20
    assert router_at_middle.next_sequence == 30
    router_at_middle.advance()
    assert router_at_middle.current_sequence == 30
    assert router_at_middle.next_sequence == -1


def test_router_move_next_to_completed(router_at_end: Router):
    assert router_at_end.current_sequence == 30
    assert router_at_end.next_sequence == -1
    router_at_end.advance()
    assert router_at_end.current_sequence == -1
    assert router_at_end.next_sequence == -1


def test_workcenter_dequeue_returns_item():
    wc = WorkCenter(
        queue=PriorityQueue(),
        name="Test Workcenter",
        prioritizer=Mock(),
        factory=Mock(),
    )
    prior1 = PrioritizedItem(priority=1, item=())
    prior2 = PrioritizedItem(priority=2, item=())

    wc.queue.put(prior2)
    wc.queue.put(prior1)

    assert id(wc.dequeue()) == id(prior1.item)
    assert id(wc.dequeue()) == id(prior2.item)


def test_factory_work_in_progress_maintains_order():
    factory = Factory(PriorityQueue())
    operation1 = Mock(hours=1)
    operation2 = Mock(hours=2)
    operation3 = Mock(hours=0.5)
    operation4 = Mock(hours=0.25)

    factory.add_work_in_progress(operation1) # (1, operation1)
    factory.add_work_in_progress(operation2) # (2, operation2)
    
    factory.complete_next()
    # operation1 completed, using 1 hour.
    # operation2 is in work, with 1 hour remaining.
    assert factory.elapsed_hours == 1

    factory.add_work_in_progress(operation3) # (1.5, operation3)
    factory.add_work_in_progress(operation4) # (1.25, operation3)
    factory.complete_next()
    # operation4 completed, using 0.25 hours.
    # operation2 is in work with 0.75 hours remaining
    # operation3 is in work, with 0.25 hours remaining
    assert factory.elapsed_hours == 1.25

    factory.complete_next()
    # operation3 completed, using 0.25 hours.
    # operation2 is in work, with 0.5 hours remaining
    assert factory.elapsed_hours == 1.5

    factory.complete_next()
    # operation2 completed, using 0.5 hours.
    assert factory.elapsed_hours == 2