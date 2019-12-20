from unittest.mock import Mock
from shop_forecasting.prioritizers import FifoPrioritizer, PrioritizedItem
from shop_forecasting.planning_objects import RouterOperation


def test_fifo_prioritizer_order():
    item1 = PrioritizedItem(-1, Mock(spec=RouterOperation))
    item2 = PrioritizedItem(-1, Mock(spec=RouterOperation))
    
    prioritizer = FifoPrioritizer()
    prioritizer.prioritize(item1)
    prioritizer.prioritize(item2)

    assert item1.priority == 0
    assert item2.priority == 1