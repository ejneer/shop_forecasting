from queue import PriorityQueue
from unittest.mock import Mock
from shop_forecasting.prioritizers import FifoPrioritizer
from shop_forecasting.planning_objects import (
    Factory,
    Router,
    RouterOperation,
    WorkCenter,
)

factory = Factory()

# define some work centers routers may go through
inventory = WorkCenter(
    name="inventory", prioritizer=FifoPrioritizer(), factory=factory, num_slots=3
)
machining = WorkCenter(
    name="machining", prioritizer=FifoPrioritizer(), factory=factory,
)
turning = WorkCenter(name="turning", prioritizer=FifoPrioritizer(), factory=factory,)
outside_processing = WorkCenter(
    name="outside_processing",
    prioritizer=FifoPrioritizer(),
    factory=factory,
    # Assume there is no limit to how many orders we can send for outside processing
    num_slots=int(1e6),
)
shipping = WorkCenter(name="shipping", prioritizer=FifoPrioritizer(), factory=factory,)

work_centers = [inventory, machining, turning, outside_processing, shipping]

router_a = Router(
    operations={}, current_sequence=10, order_number=1000, factory=factory
)
router_b = Router(
    operations={}, current_sequence=10, order_number=2000, factory=factory
)
router_c = Router(
    operations={}, current_sequence=10, order_number=3000, factory=factory
)
routers = [router_a, router_b, router_c]

router_a.operations = {
    10: RouterOperation(
        work_center=inventory, router=router_a, sequence_number=10, hours=0.5
    ),
    20: RouterOperation(
        work_center=machining, router=router_a, sequence_number=20, hours=5
    ),
    30: RouterOperation(
        work_center=outside_processing, router=router_a, sequence_number=30, hours=24,
    ),
    40: RouterOperation(
        work_center=shipping, router=router_a, sequence_number=40, hours=1
    ),
}

router_b.operations = {
    10: RouterOperation(
        work_center=inventory, router=router_b, sequence_number=10, hours=0.5
    ),
    20: RouterOperation(
        work_center=turning, router=router_b, sequence_number=20, hours=3
    ),
    30: RouterOperation(
        work_center=machining, router=router_b, sequence_number=30, hours=1
    ),
    40: RouterOperation(
        work_center=outside_processing, router=router_b, sequence_number=40, hours=12,
    ),
    50: RouterOperation(
        work_center=shipping, router=router_b, sequence_number=50, hours=1
    ),
}

router_c.operations = {
    10: RouterOperation(
        work_center=inventory, router=router_c, sequence_number=10, hours=0.5
    ),
    20: RouterOperation(
        work_center=shipping, router=router_c, sequence_number=20, hours=0.5
    ),
}

for router in routers:
    router.current_operation.work_center.enqueue(router.current_operation)


def test_factory():
    while factory.complete_next():
        # TODO: validate log of events
        pass
