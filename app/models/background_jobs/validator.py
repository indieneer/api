from .metadata import JOB_TYPES
from .status_type import StatusType
from .event import EventType


def validate_job_type(job_type):
    if job_type not in JOB_TYPES:
        raise ValueError("Unsupported job type")


def validate_status(status):
    try:
        StatusType(status)
    except ValueError:
        raise ValueError("Unsupported status")


def validate_event_type(event_type):
    try:
        EventType(event_type)
    except ValueError:
        raise ValueError("Unsupported event type")
