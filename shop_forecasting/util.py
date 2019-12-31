class EventLogger:
    ROUTER_COMPLETE = "router_complete"
    OPERATION_START = "operation_start"
    OPERATION_COMPLETE = "operation_complete"
    QUEUED_AT_WORKCENTER = "queued_at_workcenter"

    def __init__(self):
        self.messages = []

    def log_event(self, timestamp, event, planning_object):
        self.messages.append(
            {"timestamp": timestamp, "event": event, "planning_object": planning_object}
        )
