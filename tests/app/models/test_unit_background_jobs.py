from copy import deepcopy
from unittest.mock import MagicMock

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.results import DeleteResult

from app.models.background_jobs import BackgroundJobsModel, BackgroundJobCreate, BackgroundJobPatch, BackgroundJob, \
    EventCreate, Event
from tests import UnitTest


class BackgroundJobsModelTestCase(UnitTest):
    mock_db = MagicMock()
    model = BackgroundJobsModel(mock_db)

    mock_background_job = {
        "_id": ObjectId("5f7f9b9b9b9b9b9b9b9b9b9b"),
        "type": "es_seeder",
        "status": "pending",
        "metadata": {
            "match_query": "test"
        },
        "created_by": "test"
    }

    def test_get_all_background_jobs(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_background_job = {
            "_id": ObjectId("5f7f9b9b9b9b9b9b9b9b9b9b"),
            "type": "es_seeder",
            "status": "pending",
            "metadata": {
                "match_query": "test"
            },
            "created_by": "test"
        }

        mock_collection.find.return_value = [mock_background_job]

        # when
        result = self.model.get_all()

        # then
        self.assertEqual(result[0]._id, mock_background_job["_id"])
        mock_collection.find.assert_called_once_with()

        mock_collection.reset_mock()

    def test_get_background_job(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_collection.find_one.return_value = self.mock_background_job

        # when
        result = self.model.get(str(self.mock_background_job["_id"]))

        # then
        self.assertEqual(result._id, self.mock_background_job["_id"])
        mock_collection.find_one.assert_called_once_with({"_id": ObjectId(self.mock_background_job["_id"])})

        mock_collection.reset_mock()

    def test_get_background_job_with_invalid_id(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_collection.find_one.return_value = None
        mock_id = "5f7f9b9b9b9b9b9b9b9b9b9b"

        # when
        result = self.model.get(mock_id)

        # then
        self.assertIsNone(result)
        mock_collection.find_one.assert_called_once_with({"_id": ObjectId(mock_id)})

        mock_collection.reset_mock()

    def test_create_background_job(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_background_job_create = BackgroundJobCreate(
            type="es_seeder",
            metadata={
                "match_query": "it_is_a_match"
            },
            created_by="test"
        )

        # when
        result = self.model.create(mock_background_job_create)

        # then
        # actually a bit unsure about this one, but it seems to work
        self.assertEqual(result.to_json()["metadata"]["match_query"],
                         mock_background_job_create.to_json()["metadata"]["match_query"])
        mock_collection.insert_one.assert_called_once()

        mock_collection.reset_mock()

    def test_patch_background_job(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_collection.find_one.return_value = self.mock_background_job

        mock_background_job_patch = BackgroundJobPatch(
            status="success"
        )

        self.mock_background_job["status"] = mock_background_job_patch.to_json()["status"]
        mock_collection.find_one_and_update.return_value = self.mock_background_job

        # when
        result = self.model.patch(str(self.mock_background_job["_id"]), mock_background_job_patch)

        # then
        self.assertEqual(result.to_json()["status"], mock_background_job_patch.to_json()["status"])
        mock_collection.find_one.assert_called_with({"_id": ObjectId(self.mock_background_job["_id"])})
        mock_collection.find_one_and_update.assert_called_once_with(
            {"_id": ObjectId(self.mock_background_job["_id"])},
            {"$set": {"status": "success"}},
            return_document=ReturnDocument.AFTER)

        mock_collection.reset_mock()

    def test_patch_background_job_with_invalid_status(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_collection.find_one.return_value = self.mock_background_job

        mock_background_job_patch = BackgroundJobPatch(
            status="invalid_status"
        )

        # when
        with self.assertRaises(ValueError):
            self.model.patch(str(self.mock_background_job["_id"]), mock_background_job_patch)

        # then
        mock_collection.find_one.assert_called_with({"_id": ObjectId(self.mock_background_job["_id"])})
        mock_collection.find_one_and_update.assert_not_called()

        mock_collection.reset_mock()

    def test_put_background_job(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_background_job = BackgroundJob(**self.mock_background_job)
        mock_collection.insert_one.inserted_id.return_value = mock_background_job._id
        # when
        result = self.model.put(mock_background_job)

        # then
        self.assertEqual(result.to_json(), mock_background_job.to_json())
        mock_collection.insert_one.assert_called_once_with(mock_background_job.to_json())

        mock_collection.reset_mock()

    def test_delete_background_job(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_collection.delete_one.return_value = DeleteResult({"n": 1}, True)

        # when
        result = self.model.delete(str(self.mock_background_job["_id"]))

        # then
        self.assertEqual(result, 1)
        mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(self.mock_background_job["_id"])})

        mock_collection.reset_mock()

    def test_add_event(self):
        # given
        mock_collection = self.mock_db.connection.__getitem__.return_value
        mock_background_job = deepcopy(self.mock_background_job)
        mock_background_job["events"] = [Event(type="info", message="test info")]

        mock_collection.find_one_and_update.return_value = mock_background_job

        mock_event = EventCreate(
            type="info",
            message="test info"
        )

        # when
        result = self.model.add_event(str(self.mock_background_job["_id"]), mock_event)

        # then
        self.assertEqual(result.to_json()["events"][0]["type"], mock_event.type)
        mock_collection.find_one_and_update.assert_called_once()

        mock_collection.reset_mock()
