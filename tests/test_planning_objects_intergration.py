from unittest import TestCase

from shop_forecasting.planning_objects import (
    Factory,
    Router,
    RouterOperation,
    WorkCenter,
)
from shop_forecasting.prioritizers import FifoPrioritizer
from shop_forecasting.util import EventLogger

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
    router.current_operation.work_center.enqueue(router.current_operation)  # type: ignore

ts_key = "timestamp"
ev_key = "event"
obj_key = "planning_object"
expected_events = [
    # ops for all 3 routers initially queued at inventory circumventing
    # the factory, so the initial queueing event is not recorded.
    # since inventory has 3 slots, it may work them concurrently
    {
        ts_key: 0,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_a.operations[10],
    },
    {
        ts_key: 0,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_b.operations[10],
    },
    {
        ts_key: 0,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_c.operations[10],
    },
    # all inventory ops here take 0.5 hrs, and since they are worked concurrently
    # they also finish concurrently
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_a.operations[10],
    },
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_b.operations[10],
    },
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_c.operations[10],
    },
    # router_a's machining operation is queued and started
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_a.operations[20],
    },
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_a.operations[20],
    },
    # router_b's turning operation is queued and started
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_b.operations[20],
    },
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_b.operations[20],
    },
    # router_c's shipping operation is queued and started
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_c.operations[20],
    },
    {
        ts_key: 0.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_c.operations[20],
    },
    # router_c's shipping operation is only 0.5 hrs, so it will be the next event
    # that occurs.
    {
        ts_key: 1,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_c.operations[20],
    },
    # router_c only had 2 operations, so it is now complete
    {ts_key: 1, ev_key: EventLogger.ROUTER_COMPLETED, obj_key: router_c,},
    # router_b's turning op is next to complete, with 2.5 hours remaining at this point
    {
        ts_key: 3.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_b.operations[20],
    },
    # router_b's turning op gets queued up at the next wc, machining.
    {
        ts_key: 3.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_b.operations[30],
    },
    # At this point, router_a's machining op is still being worked, so
    # router_b's machining op is not yet started.
    # router_a's machining op is next to complete.
    {
        ts_key: 5.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_a.operations[20],
    },
    # router_a's outside processing op is queued and started
    {
        ts_key: 5.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_a.operations[30],
    },
    {
        ts_key: 5.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_a.operations[30],
    },
    # router_b's machining op may now start
    {
        ts_key: 5.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_b.operations[30],
    },
    # router_b's machining op completes
    {
        ts_key: 6.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_b.operations[30],
    },
    # router_b outside processing queued and started
    {
        ts_key: 6.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_b.operations[40],
    },
    {
        ts_key: 6.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_b.operations[40],
    },
    # router_b outside processing completes
    {
        ts_key: 18.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_b.operations[40],
    },
    # router_b shipping operation queued and started
    {
        ts_key: 18.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_b.operations[50],
    },
    {
        ts_key: 18.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_b.operations[50],
    },
    # router_b shipping operation completes, completing router
    {
        ts_key: 19.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_b.operations[50],
    },
    {ts_key: 19.5, ev_key: EventLogger.ROUTER_COMPLETED, obj_key: router_b,},
    # router_a outside processing completes
    {
        ts_key: 29.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_a.operations[30],
    },
    # router_a shipping operation queued and started
    {
        ts_key: 29.5,
        ev_key: EventLogger.OPERATION_QUEUED,
        obj_key: router_a.operations[40],
    },
    {
        ts_key: 29.5,
        ev_key: EventLogger.OPERATION_STARTED,
        obj_key: router_a.operations[40],
    },
    # router_a shipping operation completes, completing router
    {
        ts_key: 30.5,
        ev_key: EventLogger.OPERATION_COMPLETED,
        obj_key: router_a.operations[40],
    },
    {ts_key: 30.5, ev_key: EventLogger.ROUTER_COMPLETED, obj_key: router_a,},
]


def test_factory_integration():
    while factory.complete_next():
        pass
    # confusingly named, checks that each list contains same items
    TestCase().assertCountEqual(factory.logger.events, expected_events)
