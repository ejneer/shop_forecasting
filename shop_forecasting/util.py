class EventLogger:
    ROUTER_COMPLETED = "router_completed"
    OPERATION_STARTED = "operation_started"
    OPERATION_COMPLETED = "operation_completed"
    OPERATION_QUEUED = "operated_queued"

    def __init__(self):
        self.events = []

    def log_event(self, timestamp, event, planning_object):
        self.events.append(
            {"timestamp": timestamp, "event": event, "planning_object": planning_object}
        )
