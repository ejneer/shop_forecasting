from unittest.mock import Mock
from datetime import datetime

from shop_forecasting.prioritizers import (
    EarliestDueDatePrioritizier,
    FifoPrioritizer,
    PrioritizedItem,
    ShortestProcessingTimePrioritizer,
)


def test_fifo_prioritizer_order():
    item1 = PrioritizedItem(-1, Mock())
    item2 = PrioritizedItem(-1, Mock())

    prioritizer = FifoPrioritizer()
    prioritizer.prioritize(item1)
    prioritizer.prioritize(item2)

    assert item1.priority == 0
    assert item2.priority == 1


def test_shortest_processing_time_prioritizer():
    item1 = PrioritizedItem(-1, Mock(hours=1))
    item2 = PrioritizedItem(-1, Mock(hours=2))

    prioritizer = ShortestProcessingTimePrioritizer()
    prioritizer.prioritize(item1)
    prioritizer.prioritize(item2)

    assert item1.priority < item2.priority


def test_earliest_due_date_prioritizer():
    item1 = PrioritizedItem(
        -1, Mock(due_date=datetime.strptime("2018-08-18", "%Y-%m-%d"))
    )
    item2 = PrioritizedItem(
        -1, Mock(due_date=datetime.strptime("2020-01-17", "%Y-%m-%d"))
    )

    prioritizer = EarliestDueDatePrioritizier()
    prioritizer.prioritize(item1)
    prioritizer.prioritize(item2)

    assert item1.priority < item2.priority
