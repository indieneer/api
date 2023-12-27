import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

from bson import ObjectId
from pymongo import ReturnDocument

from ..base import BaseDocument, Serializable
from app.services import Database
from .event import Event, EventCreate
from .metadata import BaseMetadata, JobMetadata
from .status_type import StatusType
from .validator import validate_job_type, validate_status, validate_event_type


class BackgroundJob(BaseDocument):
    type: str
    created_by: str
    metadata: BaseMetadata
    status: str
    events: List[Event]
    message: Optional[str]
    started_at: Optional[datetime.datetime]

    def __init__(
            self,
            type: str,
            created_by: str,
            metadata: Dict[str, Any],
            status: Optional[str] = None,
            events: Optional[List[Event]] = None,
            message: Optional[str] = None,
            started_at: Optional[datetime.datetime] = None,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.type = type
        self.created_by = created_by
        self.metadata = JobMetadata.create(self.type, **metadata)
        self.status = status if status is not None else StatusType.PENDING.value
        self.events = events if events is not None else []
        self.message = message
        self.started_at = started_at
            


@dataclass
class BackgroundJobCreate(Serializable):
    type: str
    metadata: Dict[str, Any]
    created_by: str


@dataclass
class BackgroundJobPatch(Serializable):
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BackgroundJobsModel:
    db: Database
    collection: str = "background_jobs"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_all(self):
        background_jobs = []

        for background_job in self.db.connection[self.collection].find():
            background_jobs.append(BackgroundJob(**background_job))

        return background_jobs

    def get(self, background_job_id: str):
        background_job = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(background_job_id)}
        )

        if background_job is not None:
            return BackgroundJob(**background_job)

    def create(self, input_data: BackgroundJobCreate):
        validate_job_type(input_data.type)

        background_job = BackgroundJob(**input_data.to_bson())

        self.db.connection[self.collection].insert_one(background_job.to_bson())

        return background_job

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
            validate_status(payload["status"])

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

    def add_event(self, background_job_id: str, event: EventCreate):
        validate_event_type(event.type)

        updated = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(background_job_id)},
            {"$push": {"events": Event(**event.to_json()).to_json()}},
            return_document=ReturnDocument.AFTER
        )

        if updated is not None:
            return BackgroundJob(**updated)
