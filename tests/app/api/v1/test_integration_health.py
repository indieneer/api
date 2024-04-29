from tests import IntegrationTest


class HealthTestCase(IntegrationTest):

    def test_get_health(self):
        # when
        response = self.app.get("/v1/health")

        # then
        expected = {
            "status": "ok",
            "data": {
                "db": 1.0,
                "env": "test",
                "version": "0.0.1"
            }
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected)
