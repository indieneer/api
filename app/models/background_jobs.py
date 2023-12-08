import datetime
import json
from enum import Enum
from typing import Optional, Any, Dict
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
    @staticmethod
    def create_metadata(job_type: JobType, **kwargs) -> EsSeederMetadata:
        if job_type == JobType.ES_SEEDER.value:
            return EsSeederMetadata(**kwargs)
        else:
            raise ValueError(f"Unsupported job type: {job_type}")


class StatusType(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class BackgroundJob(BaseDocument):
    type: JobType
    metadata: BaseMetadata
    status: StatusType
    message: Optional[str]
    created_by: str
    started_at: Optional[datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def __init__(
            self,
            type: JobType,
            metadata: Dict[str, any],
            created_by: str,
            status: StatusType = StatusType.PENDING.value,
            message: Optional[str] = "",
            started_at: Optional[datetime.datetime] = None,
            created_at: Optional[datetime.datetime] = datetime.datetime.utcnow(),
            updated_at: Optional[datetime.datetime] = datetime.datetime.utcnow(),
            _id: Optional[ObjectId] = None,
            **kwargs
    ) -> None:
        super().__init__(_id)

        self.type = type
        self.metadata = MetadataFactory.create_metadata(self.type, **metadata)
        self.status = status
        self.message = message
        self.created_by = created_by
        self.started_at = started_at
        self.created_at = created_at
        self.updated_at = updated_at


@dataclass
class BackgroundJobCreate(Serializable):
    type: JobType
    metadata: Dict[str, any]
    created_by: str


@dataclass
class BackgroundJobPatch(Serializable):
    status: Optional[StatusType] = None
    message: Optional[str] = None


class BackgroundJobsModel:
    db: Database
    collection: str = "background_jobs"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, background_job_id: str):
        background_job = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(background_job_id)}
        )

        if background_job is not None:
            return BackgroundJob(**background_job)

    def create(self, input_data: BackgroundJobCreate):
        background_job = BackgroundJob(**input_data.to_json()).as_json()
        self.db.connection[self.collection].insert_one(background_job)

        return BackgroundJob(**background_job)

    def patch(self, background_job_id: str, input_data: BackgroundJobPatch):
        if len(input_data.to_json().values()) == 0:
            raise ValueError("No updates provided")

        payload = input_data.to_json()
        if input_data.to_json().get("metadata"):
            background_job = self.db.connection[self.collection].find_one({"_id": ObjectId(background_job_id)})
            for key, value in background_job["metadata"].items():
                if not input_data.to_json()["metadata"].get(key):
                    payload["metadata"][key] = value

        return BackgroundJob(**self.db.connection[self.collection].find_one_and_update({"_id": ObjectId(background_job_id)}, {"$set": payload}, return_document=ReturnDocument.AFTER))

    def delete(self, background_job_id: str):
        background_job = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(background_job_id)}
        )

        if background_job is not None:
            return BackgroundJob(**background_job)
