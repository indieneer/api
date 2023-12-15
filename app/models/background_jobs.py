import datetime
from enum import Enum
from typing import Optional, Dict, List, Type
from dataclasses import dataclass

from bson import ObjectId
from pymongo import ReturnDocument

from app.services import Database
from . import BaseDocument, Serializable


class BaseMetadata(Serializable):
    def __init__(self, **kwargs):
        pass


@dataclass
class EsSeederMetadata(BaseMetadata):
    match_query: str


JOB_METADATA: Dict[str, Type[BaseMetadata]] = {
    "es_seeder": EsSeederMetadata
}
JOB_TYPES = JOB_METADATA.keys()


class JobMetadata:
    """
    Factory class to create metadata objects based on the job type.
    """

    @staticmethod
    def create(job_type: str, **kwargs) -> BaseMetadata:
        """
        Creates a metadata object based on the job type.

        :param job_type: The job type.
        :param kwargs: The metadata.
        :return: The metadata object.
        """
        metadata = JOB_METADATA.get(job_type)

        if metadata is None:
            raise ValueError(f"Unsupported job type: {job_type}")

        return metadata(**kwargs)


class StatusType(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class EventType(Enum):
    ERROR = "error"
    INFO = "info"


class Event(Serializable):
    """
    Event class of Background Job.
    """

    type: str
    message: str
    date: datetime.datetime

    def __init__(
            self,
            type: str,
            message: str
    ):
        self.type = type
        self.message = message
        self.date = datetime.datetime.utcnow()


@dataclass
class EventCreate(Serializable):
    type: str
    message: str


class BackgroundJob(BaseDocument):
    type: str
    events: List[Event]
    metadata: BaseMetadata
    status: str
    message: Optional[str]
    created_by: str
    started_at: Optional[datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def __init__(
            self,
            type: str,
            metadata: Dict[str, any],
            created_by: str,
            events=None,
            status: str = StatusType.PENDING.value,
            message: Optional[str] = "",
            started_at: Optional[datetime.datetime] = None,
            created_at: Optional[datetime.datetime] = datetime.datetime.utcnow(),
            **kwargs
    ) -> None:
        super().__init__(kwargs.get("_id"))

        self.type = type
        self.events = events if events is not None else []
        self.metadata = JobMetadata.create(self.type, **metadata)
        self.status = status
        self.message = message
        self.created_by = created_by
        self.started_at = started_at
        self.created_at = created_at
        self.updated_at = datetime.datetime.utcnow()


@dataclass
class BackgroundJobCreate(Serializable):
    type: str
    metadata: Dict[str, any]
    created_by: str


@dataclass
class BackgroundJobPatch(Serializable):
    status: Optional[str] = None
    metadata: Optional[Dict[str, any]] = None


class BackgroundJobsModel:
    db: Database
    collection: str = "background_jobs"

    def __init__(self, db: Database) -> None:
        self.db = db

    def validate_job_type(self, job_type):
        if job_type not in JOB_TYPES:
            raise ValueError("Unsupported job type")

    def validate_status(self, status):
        try:
            StatusType(status)
        except ValueError:
            raise ValueError("Unsupported status")

    def validate_event_type(self, event_type):
        try:
            EventType(event_type)
        except ValueError:
            raise ValueError("Unsupported event type")

    def get_all(self):
        background_jobs = []

        for background_job in self.db.connection[self.collection].find():
            background_jobs.append(BackgroundJob(**background_job))

        return background_jobs

    def get(self, background_job_id: str):
        print(background_job_id, type(background_job_id), ObjectId(background_job_id))
        background_job = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(background_job_id)}
        )
        print(background_job)

        if background_job is not None:
            return BackgroundJob(**background_job)

    def create(self, input_data: BackgroundJobCreate):
        self.validate_job_type(input_data.type)

        # temporary... very temporary
        background_job = BackgroundJob(**input_data.to_json())
        temp_id = background_job._id
        background_job_2 = background_job.as_json()
        background_job_2["_id"] = temp_id

        self.db.connection[self.collection].insert_one(background_job_2)

        return BackgroundJob(**background_job_2)

    def patch(self, background_job_id: str, input_data: BackgroundJobPatch):
        background_job = self.db.connection[self.collection].find_one({"_id": ObjectId(background_job_id)})
        if background_job is None:
            return None

        payload = {key: value for key, value in input_data.to_json().items() if value is not None}
        if payload.get("metadata") is not None:
            for key, value in background_job["metadata"].items():
                if not input_data.to_json()["metadata"].get(key):
                    payload["metadata"][key] = value
            payload["metadata"] = JobMetadata.create(background_job["type"],
                                                     **payload["metadata"]).to_json()

        if payload.get("status") is not None:
            self.validate_status(payload["status"])

        updated = self.db.connection[self.collection].find_one_and_update({"_id": ObjectId(background_job_id)},
                                                                          {"$set": payload},
                                                                          return_document=ReturnDocument.AFTER)
        if updated is not None:
            return BackgroundJob(**updated)

    def delete(self, background_job_id: str):
        background_job = self.db.connection[self.collection].find_one_and_delete(
            {"_id": background_job_id}
        )

        if background_job is not None:
            return BackgroundJob(**background_job)

    def create_and_append_event(self, background_job_id: str, event: EventCreate):
        updated = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(background_job_id)},
            {"$push": {"events": Event(**event.to_json()).to_json()}},
            return_document=ReturnDocument.AFTER
        )

        if updated is not None:
            return BackgroundJob(**updated)
