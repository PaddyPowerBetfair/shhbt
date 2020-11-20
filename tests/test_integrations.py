import os

from unittest import TestCase
from unittest.mock import Mock, patch

from shhbt.gitclient import CommitStatus
from shhbt.server import create_flask_app
from tests.data import api_json_res


class TestIntegrations(TestCase):
    test_dir_data = f"{os.path.dirname(__file__)}/data"

    test_env = {
        "GITLAB_TOKEN": "Testing Token",
        "GITLAB_URI": "testing_instance.gitlab.com",
        "CONFIG_LOCATION": f"{test_dir_data}/config_with_sig.yaml",
    }

    test_client = None

    def setUp(self) -> None:
        _app = create_flask_app()
        self.test_client = _app.test_client()

    @patch("shhbt.gitclient.gitlab._GitLab._update_commit_status")
    @patch("requests.Session.request")
    @patch.dict("os.environ", test_env)
    def test_unsafe_gitlab_returns_200(self, req_mock, status_mock):
        diff_mock = Mock()
        diff_mock.json.return_value = api_json_res.DIFF_UNSAFE_FILE_CONTENT

        req_mock.side_effect = [Mock(), diff_mock]  # No config repo, specific diff

        assert self.test_client.post("/", headers={"X-Gitlab-Event": "test-event"}, json=api_json_res.EVENT_FOR_UNSAFE)

        assert status_mock.call_count == 2
        assert status_mock.call_args_list == [
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.PENDING),),
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.FAILED),),
        ]

    @patch("shhbt.gitclient.gitlab._GitLab._update_commit_status")
    @patch("requests.Session.request")
    @patch.dict("os.environ", test_env)
    def test_skips_and_succeeds_when_deleted_file(self, req_mock, status_mock):
        diff_mock = Mock()
        diff_mock.json.return_value = api_json_res.DIFF_DELETED_FILE

        req_mock.side_effect = [Mock(), diff_mock]  # No config repo, specific diff

        assert (
            self.test_client.post(
                "/", headers={"X-Gitlab-Event": "test-event"}, json=api_json_res.EVENT_FOR_UNSAFE
            ).status_code
            == 200
        )

        assert status_mock.call_count == 2
        assert status_mock.call_args_list == [
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.PENDING),),
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.SUCCESS),),
        ]

    @patch.dict("os.environ", test_env)
    def test_returns_400_if_not_merge_request(self):
        assert (
            self.test_client.post(
                "/", headers={"X-Gitlab-Event": "test-event"}, json={"event_type": "comment"}
            ).status_code
            == 400
        )

    @patch.dict("os.environ", test_env)
    def test_only_post_is_allowed_for_known_endpoints(self):
        assert self.test_client.get("/", headers={"X-Gitlab-Event": "some-event"}).status_code == 405
        assert self.test_client.put("/", headers={"X-Gitlab-Event": "some-event"}).status_code == 405
        assert self.test_client.delete("/", headers={"X-Gitlab-Event": "some-event"}).status_code == 405

    @patch.dict("os.environ", test_env)
    def test_all_other_calls_returns_404(self):
        assert self.test_client.post("/test-endpoint").status_code == 404
        assert self.test_client.get("/test-endpoint").status_code == 404
        assert self.test_client.put("/test-endpoint").status_code == 404
        assert self.test_client.delete("/test-endpoint").status_code == 404
