import datetime
from enum import Enum
from typing import Optional, Dict, List
from bson import ObjectId
from dataclasses import dataclass

from pymongo import ReturnDocument

from app.services import Database
from . import BaseDocument, Serializable


class JobType(Enum):
    ES_SEEDER = "es_seeder"


class BaseMetadata(Serializable):
    pass


@dataclass
class EsSeederMetadata(BaseMetadata):
    match_query: str


class MetadataFactory:
    """
    Factory class to create metadata objects based on the job type.
    """

    @staticmethod
    def create_metadata(job_type: str, **kwargs) -> BaseMetadata:
        """
        Creates a metadata object based on the job type.

        :param job_type: The job type.
        :param kwargs: The metadata.
        :return: The metadata object.
        """
        if job_type == JobType.ES_SEEDER.value:
            return EsSeederMetadata(**kwargs)
        else:
            raise ValueError(f"Unsupported job type: {job_type}")


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
    events: Optional[List[Event]]
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
            updated_at: Optional[datetime.datetime] = datetime.datetime.utcnow(),
            _id: Optional[ObjectId] = None
    ) -> None:
        super().__init__(_id)

        self.type = type
        self.events = events if events is not None else []
        self.metadata = MetadataFactory.create_metadata(self.type, **metadata)
        self.status = status
        self.message = message
        self.created_by = created_by
        self.started_at = started_at
        self.created_at = created_at
        self.updated_at = updated_at


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
        try:
            JobType(job_type)
        except ValueError:
            raise ValueError("unsupported job type")

    def validate_status(self, status):
        try:
            StatusType(status)
        except ValueError:
            raise ValueError("unsupported status")

    def validate_event_type(self, event_type):
        try:
            EventType(event_type)
        except ValueError:
            raise ValueError("unsupported event type")

    def get_all(self):
        background_jobs = []

        for background_job in self.db.connection[self.collection].find():
            background_job["_id"] = str(background_job["_id"])
            background_jobs.append(background_job)

        return background_jobs

    def get(self, background_job_id: str):
        background_job = self.db.connection[self.collection].find_one(
            {"_id": background_job_id}
        )

        if background_job is not None:
            return BackgroundJob(**background_job)

    def create(self, input_data: BackgroundJobCreate):
        self.validate_job_type(input_data.type)

        background_job = BackgroundJob(**input_data.to_json()).as_json()
        self.db.connection[self.collection].insert_one(background_job)

        return BackgroundJob(**background_job)

    def patch(self, background_job_id: str, input_data: BackgroundJobPatch):
        if len(input_data.to_json().values()) == 0:
            raise ValueError("no updates provided")

        background_job = self.db.connection[self.collection].find_one({"_id": background_job_id})
        if background_job is None:
            return None

        payload = {key: value for key, value in input_data.to_json().items() if value is not None}
        if payload.get("metadata") is not None:
            for key, value in background_job["metadata"].items():
                if not input_data.to_json()["metadata"].get(key):
                    payload["metadata"][key] = value
            payload["metadata"] = MetadataFactory.create_metadata(background_job["type"],
                                                                  **payload["metadata"]).to_json()

        if payload.get("status") is not None:
            self.validate_status(payload["status"])

        return BackgroundJob(
            **self.db.connection[self.collection].find_one_and_update({"_id": background_job_id},
                                                                      {"$set": payload},
                                                                      return_document=ReturnDocument.AFTER))

    def delete(self, background_job_id: str):
        background_job = self.db.connection[self.collection].find_one_and_delete(
            {"_id": background_job_id}
        )

        if background_job is not None:
            return BackgroundJob(**background_job)

    def create_and_append_event(self, background_job_id: str, event: EventCreate):
        background_job = self.db.connection[self.collection].find_one(
            {"_id": background_job_id}
        )
        if background_job is None:
            return None

        payload = {"events": background_job["events"]}
        payload["events"].append(Event(**event.to_json()).to_json())

        return BackgroundJob(
            **self.db.connection[self.collection].find_one_and_update({"_id": background_job_id},
                                                                      {"$set": payload},
                                                                      return_document=ReturnDocument.AFTER))
