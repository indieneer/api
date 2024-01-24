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
    mock_collection = mock_db.connection.__getitem__.return_value

    def get_new_mock_background_job(self):
        return {
            "_id": ObjectId(),
            "type": "es_seeder",
            "status": "pending",
            "metadata": {
                "match_query": "test"
            },
            "created_by": "test"
        }

    def test_get_background_jobs(self):
        def finds_and_returns_background_job():
            # given
            mock_background_job = self.get_new_mock_background_job()
            self.mock_collection.find_one.return_value = mock_background_job

            # when
            result = self.model.get(str(mock_background_job["_id"]))

            # then
            self.assertEqual(result._id, mock_background_job["_id"])
            self.mock_collection.find_one.assert_called_once_with({"_id": ObjectId(mock_background_job["_id"])})

        def does_not_find_background_job_and_returns_none():
            # given
            self.mock_collection.find_one.return_value = None
            mock_id = str(ObjectId())

            # when
            result = self.model.get(mock_id)

            # then
            self.assertIsNone(result)
            self.mock_collection.find_one.assert_called_once_with({"_id": ObjectId(mock_id)})

        tests = [
            finds_and_returns_background_job,
            does_not_find_background_job_and_returns_none
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            self.mock_db.reset_mock()
            self.mock_collection.reset_mock()

    def test_get_all_background_jobs(self):
        def finds_and_returns_all_background_jobs():
            # given
            mock_background_job = self.get_new_mock_background_job()

            self.mock_collection.find.return_value = [mock_background_job]

            # when
            result = self.model.get_all()

            # then
            self.assertEqual(result[0]._id, mock_background_job["_id"])
            self.mock_collection.find.assert_called_once()

        def does_not_find_background_jobs_and_returns_empty_list():
            # given
            self.mock_collection.find.return_value = []

            # when
            result = self.model.get_all()

            # then
            self.assertEqual(result, [])
            self.mock_collection.find.assert_called_once()

        tests = [
            finds_and_returns_all_background_jobs,
            does_not_find_background_jobs_and_returns_empty_list
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            self.mock_db.reset_mock()
            self.mock_collection.reset_mock()

    def test_create_background_job(self):
        def creates_and_returns_background_job():
            # given
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
            self.mock_collection.insert_one.assert_called_once()

        def fails_to_create_background_job_with_invalid_type_and_returns_an_error():
            # given
            mock_background_job_create = BackgroundJobCreate(
                type="invalid_type",
                metadata={
                    "match_query": "it_is_a_match"
                },
                created_by="test"
            )

            # when
            with self.assertRaises(ValueError):
                self.model.create(mock_background_job_create)

            # then
            self.mock_collection.insert_one.assert_not_called()

        tests = [
            creates_and_returns_background_job,
            fails_to_create_background_job_with_invalid_type_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            self.mock_db.reset_mock()
            self.mock_collection.reset_mock()

    def test_patch_background_job(self):
        def finds_then_patches_and_returns_background_job():
            # given
            mock_background_job = self.get_new_mock_background_job()
            self.mock_collection.find_one.return_value = mock_background_job

            mock_background_job_patch = BackgroundJobPatch(
                status="success"
            )

            mock_background_job["status"] = mock_background_job_patch.to_json()["status"]
            self.mock_collection.find_one_and_update.return_value = mock_background_job

            # when
            result = self.model.patch(str(mock_background_job["_id"]), mock_background_job_patch)

            # then
            self.assertEqual(result.to_json()["status"], mock_background_job_patch.to_json()["status"])
            self.mock_collection.find_one.assert_called_with({"_id": ObjectId(mock_background_job["_id"])})
            self.mock_collection.find_one_and_update.assert_called_once_with(
                {"_id": ObjectId(mock_background_job["_id"])},
                {"$set": {"status": "success"}},
                return_document=ReturnDocument.AFTER)

        def does_not_find_background_job_and_returns_none():
            # given
            self.mock_collection.find_one.return_value = None

            mock_id = str(ObjectId())
            mock_background_job_patch = BackgroundJobPatch(
                status="success"
            )

            # when
            result = self.model.patch(mock_id, mock_background_job_patch)

            # then
            self.assertIsNone(result)
            self.mock_collection.find_one.assert_called_with({"_id": ObjectId(mock_id)})
            self.mock_collection.find_one_and_update.assert_not_called()

        def fails_to_patch_background_job_with_invalid_status_and_returns_an_error():
            # given
            mock_background_job = self.get_new_mock_background_job()
            self.mock_collection.find_one.return_value = mock_background_job

            mock_background_job_patch = BackgroundJobPatch(
                status="invalid_status"
            )

            # when
            with self.assertRaises(ValueError):
                self.model.patch(str(mock_background_job["_id"]), mock_background_job_patch)

            # then
            self.mock_collection.find_one.assert_called_with({"_id": ObjectId(mock_background_job["_id"])})
            self.mock_collection.find_one_and_update.assert_not_called()

        tests = [
            finds_then_patches_and_returns_background_job,
            does_not_find_background_job_and_returns_none,
            fails_to_patch_background_job_with_invalid_status_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            self.mock_db.reset_mock()
            self.mock_collection.reset_mock()

    def test_put_background_job(self):
        def inserts_and_returns_background_job():
            # given
            mock_background_job = BackgroundJob(**self.get_new_mock_background_job())
            self.mock_collection.insert_one.inserted_id.return_value = mock_background_job._id

            # when
            result = self.model.put(mock_background_job)

            # then
            self.assertEqual(result.to_json(), mock_background_job.to_json())
            self.mock_collection.insert_one.assert_called_once_with(mock_background_job.to_json())

        def fails_to_insert_background_job_with_invalid_type_and_returns_an_error():
            # given
            mock_background_job = self.get_new_mock_background_job()
            mock_background_job["type"] = "invalid_type"

            # when
            with self.assertRaises(ValueError):
                self.model.put(BackgroundJob(**mock_background_job))

            # then
            self.mock_collection.insert_one.assert_not_called()

        def fails_to_insert_background_job_with_invalid_status_and_returns_an_error():
            # given
            mock_background_job = self.get_new_mock_background_job()
            mock_background_job["status"] = "invalid_status"

            # when
            with self.assertRaises(ValueError):
                self.model.put(BackgroundJob(**mock_background_job))

            # then
            self.mock_collection.insert_one.assert_not_called()

        def fails_to_insert_background_job_with_invalid_event_type_and_returns_an_error():
            # given
            mock_background_job = self.get_new_mock_background_job()
            mock_background_job["events"] = [Event(type="invalid_type", message="test")]

            # when
            with self.assertRaises(ValueError):
                self.model.put(BackgroundJob(**mock_background_job))

            # then
            self.mock_collection.insert_one.assert_not_called()

        tests = [
            inserts_and_returns_background_job,
            fails_to_insert_background_job_with_invalid_type_and_returns_an_error,
            fails_to_insert_background_job_with_invalid_status_and_returns_an_error,
            fails_to_insert_background_job_with_invalid_event_type_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            self.mock_db.reset_mock()
            self.mock_collection.reset_mock()

    def test_delete_background_job(self):
        def deletes_and_returns_deleted_count():
            # given
            mock_background_job = self.get_new_mock_background_job()
            self.mock_collection.delete_one.return_value = DeleteResult({"n": 1}, True)

            # when
            result = self.model.delete(str(mock_background_job["_id"]))

            # then
            self.assertEqual(result, 1)
            self.mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(mock_background_job["_id"])})

        def does_not_delete_and_returns_zero():
            # given
            self.mock_collection.delete_one.return_value = DeleteResult({"n": 0}, True)

            mock_id = str(ObjectId())

            # when
            result = self.model.delete(mock_id)

            # then
            self.assertEqual(result, 0)
            self.mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(mock_id)})

        tests = [
            deletes_and_returns_deleted_count,
            does_not_delete_and_returns_zero
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            self.mock_db.reset_mock()
            self.mock_collection.reset_mock()

    def test_add_event(self):
        def adds_event_and_returns_updated_background_job():
            # given
            mock_background_job = deepcopy(self.get_new_mock_background_job())
            mock_background_job["events"] = [Event(type="info", message="test info")]

            self.mock_collection.find_one_and_update.return_value = mock_background_job

            mock_event = EventCreate(
                type="info",
                message="test info"
            )

            # when
            result = self.model.add_event(str(mock_background_job["_id"]), mock_event)

            # then
            self.assertEqual(result.to_json()["events"][0]["type"], mock_event.type)
            self.mock_collection.find_one_and_update.assert_called_once()

        def fails_to_add_event_with_invalid_event_type_and_returns_an_error():
            # given
            mock_background_job = self.get_new_mock_background_job()
            self.mock_collection.find_one_and_update.return_value = mock_background_job

            mock_event = EventCreate(
                type="invalid_type",
                message="test info"
            )

            # when
            with self.assertRaises(ValueError):
                self.model.add_event(str(mock_background_job["_id"]), mock_event)

            # then
            self.mock_collection.find_one_and_update.assert_not_called()

        tests = [
            adds_event_and_returns_updated_background_job,
            fails_to_add_event_with_invalid_event_type_and_returns_an_error
        ]

        for test in tests:
            with self.subTest(test.__name__):
                test()
            self.mock_db.reset_mock()
            self.mock_collection.reset_mock()
