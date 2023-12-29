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
        """
        Get all background jobs from the database.
        :return: The background jobs data.
        :rtype: List[BackgroundJob]
        """
        background_jobs = []

        for background_job in self.db.connection[self.collection].find():
            background_jobs.append(BackgroundJob(**background_job))

        return background_jobs

    def get(self, background_job_id: str):
        """
        Get a background job from the database.
        :param background_job_id: The ID of the background job to be retrieved.
        :type background_job_id: str
        :return: The background job data.
        :rtype: BackgroundJob
        """
        background_job = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(background_job_id)}
        )

        if background_job is not None:
            return BackgroundJob(**background_job)

    def create(self, input_data: BackgroundJobCreate):
        """
        Create a new background job in the database with a new ID.
        :param input_data: The background job data to be created.
        :type input_data: BackgroundJobCreate
        :return: The created background job data with a new ID.
        :rtype: BackgroundJob
        """
        validate_job_type(input_data.type)

        background_job = BackgroundJob(**input_data.to_bson())

        self.db.connection[self.collection].insert_one(background_job.to_bson())

        return background_job

    def patch(self, background_job_id: str, input_data: BackgroundJobPatch):
        """
        Update a background job in the database.
        :param background_job_id: The ID of the background job to be updated.
        :type background_job_id: str
        :param input_data: The background job data to be updated.
        :type input_data: BackgroundJobPatch
        :return: The updated background job data.
        :rtype: BackgroundJob
        """
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

    def put(self, input_data: BackgroundJob):
        """
        Create a new background job in the database with a new ID.
        :param input_data: The background job data to be created.
        :type input_data: BackgroundJob
        :return: The created background job data with a new ID.
        :rtype: BackgroundJob
        """
        background_job_data = input_data.to_json()
        validate_job_type(background_job_data["type"])
        validate_status(background_job_data["status"])
        for event in background_job_data["events"]:
            validate_event_type(event["type"])
        del background_job_data["_id"]

        inserted_id = self.db.connection[self.collection].insert_one(background_job_data).inserted_id
        background_job_data["_id"] = inserted_id

        return BackgroundJob(**background_job_data)

    def delete(self, background_job_id: str):
        """
        Delete a background job from the database.
        :param background_job_id: The ID of the background job to be deleted.
        :type background_job_id: str
        :return: The number of deleted background jobs.
        :rtype: int
        """
        background_job = self.db.connection[self.collection].delete_one(
            {"_id": ObjectId(background_job_id)}
        )

        return background_job.deleted_count

    def add_event(self, background_job_id: str, event: EventCreate):
        """
        Add a new event to the background job.
        :param background_job_id: The ID of the background job to be updated.
        :type background_job_id: str
        :param event: The event to be added.
        :type event: EventCreate
        :return: The updated background job data.
        :rtype: BackgroundJob
        """
        validate_event_type(event.type)

        updated = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(background_job_id)},
            {"$push": {"events": Event(**event.to_json()).to_json()}},
            return_document=ReturnDocument.AFTER
        )

        if updated is not None:
            return BackgroundJob(**updated)
