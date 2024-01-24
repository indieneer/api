from bson import ObjectId

from app.models.tags import TagCreate
from tests import IntegrationTest


class TagsTestCase(IntegrationTest):
    @property
    def token(self):
        return self.factory.logins.login(email="test_integration+admin@pork.com",
                                               password="9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:")["access_token"]

    def test_get_tags(self):
        # given
        _, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get("/v1/admin/tags",
                                headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json["data"]), 1 + 1)
        self.assertEqual(response_json["data"][1]["name"], "Test Tag 1")

    def test_get_tags_without_token_present(self):
        # when
        response = self.app.get("/v1/admin/tags")
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json["error"]
                         ["code"], "authorization_header_missing")

    def test_get_tags_with_not_admin_token(self):
        # given
        token = self.factory.logins.login(email="test_integration+regular@pork.com",
                                          password="9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:")["access_token"]

        # when
        response = self.app.get("/v1/admin/tags",
                                headers={"Authorization": f'Bearer {token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json["error"], "no permission")

    def test_get_tag_by_id(self):
        # given
        tag, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/tags/{tag._id}",
                                headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["name"], "Test Tag 1")

    def test_get_tag_by_id_not_found(self):
        id = str(ObjectId())

        # when
        response = self.app.get(f"/v1/admin/tags/{id}",
                                headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json["error"],
                         f"The tag with ID {id} was not found.")

    def test_get_tag_by_id_with_invalid_token(self):
        # given
        tag, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)

        # when
        response = self.app.get(f"/v1/admin/tags/{tag._id}",
                                headers={"Authorization": f'Bearer {self.token}a'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json["error"]["code"], "invalid_header")

    def test_create_tag(self):
        # given
        payload = {
            "name": "Test Tag Create"
        }

        # when
        response = self.app.post("/v1/admin/tags",
                                 headers={
                                     "Authorization": f'Bearer {self.token}'},
                                 json=payload)
        response_json = response.get_json()

        # then
        self.factory.tags.cleanup(ObjectId(response_json["data"]["_id"]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["data"]["name"], "Test Tag Create")

    def test_create_tag_with_invalid_token(self):
        # given
        payload = {
            "name": "Test Tag Create"
        }

        # when
        response = self.app.post("/v1/admin/tags",
                                 headers={
                                     "Authorization": f'Bearer {self.token}a'},
                                 json=payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json["error"]["code"], "invalid_header")

    def test_create_tag_with_no_required_fields_present(self):
        # given
        data = {
            "description": "Test Description"
        }

        # when
        response = self.app.post("/v1/admin/tags",
                                 headers={
                                     "Authorization": f'Bearer {self.token}'},
                                 json=data)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_json["error"], "Bad Request.")

    def test_update_tag(self):
        # given
        tag, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)

        payload = {
            "name": "Test Tag 2"
        }

        # when
        response = self.app.patch(f"/v1/admin/tags/{tag._id}",
                                  headers={
                                      "Authorization": f'Bearer {self.token}'},
                                  json=payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["data"]["name"], "Test Tag 2")

    def test_update_tag_with_invalid_token(self):
        # given
        tag, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)

        payload = {
            "name": "Test Tag 2"
        }

        # when
        response = self.app.patch(f"/v1/admin/tags/{tag._id}",
                                  headers={
                                      "Authorization": f'Bearer {self.token}a'},
                                  json=payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_json["error"]["code"], "invalid_header")

    def test_update_token_with_invalid_keys(self):
        # given
        tag, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)

        payload = {
            "name": "Test Tag 2",
            "description": "Test Description"
        }

        # when
        response = self.app.patch(f"/v1/admin/tags/{tag._id}",
                                  headers={
                                      "Authorization": f'Bearer {self.token}'},
                                  json=payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response_json["error"], "The keys ['description'] are not allowed.")

    def test_update_token_with_invalid_id(self):
        # given
        id = ObjectId()
        payload = {
            "name": "Test Tag 2"
        }

        # when
        response = self.app.patch(f"/v1/admin/tags/{id}",
                                  headers={
                                      "Authorization": f'Bearer {self.token}'},
                                  json=payload)
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json["error"], f"\"Tag\" not found.")

    def test_delete_tag(self):
        # given
        tag, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)

        # when
        response = self.app.delete(f"/v1/admin/tags/{tag._id}",
                                   headers={"Authorization": f'Bearer {self.token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_json["data"], f"Successfully deleted the tag with ID {tag._id}")

    def test_delete_tag_without_permission(self):
        # given
        tag, cleanup = self.factory.tags.create(TagCreate(name="Test Tag 1"))
        self.addCleanup(cleanup)
        token = self.factory.logins.login(email="test_integration+regular@pork.com",
                                          password="9!8@7#6$5%4^3&2*1(0)-_=+[]{}|;:")["access_token"]

        # when
        response = self.app.delete(f"/v1/admin/tags/{tag._id}",
                                   headers={"Authorization": f'Bearer {token}'})
        response_json = response.get_json()

        # then
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json["error"], "no permission")
