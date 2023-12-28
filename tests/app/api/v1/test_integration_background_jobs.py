from tests import IntegrationTest


class BackgroundJobsTestCase(IntegrationTest):
    def test_get_all_background_jobs(self):
        # given
        background_job = self.fixtures.background_job.clone()
        _, cleanup = self.factory.background_jobs.create(background_job)
        self.addCleanup(cleanup)

        test_cases = [
            {
                "name": "Returns all background jobs",
                "expect": lambda data: type(data) == list and len(data) != 0
            }
        ]

        # when
        for test_case in test_cases:
            with self.subTest(test_case["name"]):
                response = self.app.get(
                    '/v1/background_jobs')
                expect = test_case["expect"]

                # then
                json_data = response.get_json()
                self.assertIsInstance(json_data, dict)
                self.assertIsNone(json_data.get("error"))
                self.assertEquals(response.status_code, 200)

                data = json_data.get("data")

                self.assertTrue(expect(data))
