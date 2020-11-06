import os
from unittest import TestCase
from unittest.mock import patch

import pytest

from shhbt.gitclient.gitlab import handle_gitlab_event, _GitLab, CommitStatus
from shhbt.session import Session
from tests import SecretTestMixin
from tests.data import api_json_res


class TestGitLabIntegration(SecretTestMixin, TestCase):
    test_dir_data = f"{os.path.dirname(__file__)}/data"

    gitlab_config_patch = patch("shhbt.gitclient.gitlab._GitLab.config_in_repo")
    gitlab_config_mock = None

    gitlab_change_status_patch = patch("shhbt.gitclient.gitlab._GitLab._update_commit_status")
    gitlab_change_status_mock = None

    diff_patch = patch("shhbt.gitclient.gitlab._GitLab._fetch_diff")
    diff_mock = None

    test_env = {
        "GITLAB_TOKEN": "Testing Token",
        "GITLAB_URI": "Testing Instance",
        "CONFIG_LOCATION": f"{test_dir_data}/config_with_sig.yaml",
    }

    def setUp(self) -> None:
        self.gitlab_config_mock = self.gitlab_config_patch.start()
        self.gitlab_config_mock.return_value = False, None

        self.gitlab_change_status_mock = self.gitlab_change_status_patch.start()

        self.diff_mock = self.diff_patch.start()

    def tearDown(self) -> None:
        self.gitlab_config_patch.stop()
        self.diff_patch.stop()


    def test_raises_if_no_hostname_nor_token(self):
        with pytest.raises(ValueError):
            _GitLab(hostname="", token="")

    def test_raises_if_hostname_and_token_are_none(self):
        with pytest.raises(ValueError):
            _GitLab(hostname=None, token=None)

    @patch.dict("os.environ", test_env)
    def test_skips_merge_commits_and_detects_filename(self):
        # Mock prep
        self.diff_mock.return_value = api_json_res.DIFF_UNSAFE_FILENAME

        # GIVEN an EVENT which contemplates items that belong to the blacklist
        # WHEN the handle function is called
        handle_gitlab_event(event_body=api_json_res.EVENT_FOR_UNSAFE)

        # THEN the call to change status the happened two times
        assert self.gitlab_change_status_mock.call_count == 2

        # AND THEN the payloads were in this order (one to pending, one to failed)
        assert self.gitlab_change_status_mock.call_args_list == [
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.PENDING),),
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.FAILED),),
        ]
    
    @patch.dict("os.environ", test_env)
    def test_can_detect_secrets_in_extension(self):
        # Mock prep
        self.diff_mock.return_value = api_json_res.DIFF_UNSAFE_FILE_EXTENSION

        # GIVEN an EVENT which contemplates items that belong to the blacklist
        # WHEN the handle function is called
        handle_gitlab_event(event_body=api_json_res.EVENT_FOR_UNSAFE)

        # THEN the call to change status the happened two times
        assert self.gitlab_change_status_mock.call_count == 2

        # AND THEN the payloads were in this order (one to pending, one to failed)
        assert self.gitlab_change_status_mock.call_args_list == [
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.PENDING),),
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.FAILED),),
        ]

    @patch.dict("os.environ", test_env)
    def test_can_detect_secrets_in_content(self):
        # Mock prep
        self.diff_mock.return_value = api_json_res.DIFF_UNSAFE_FILE_CONTENT

        # GIVEN an EVENT which contemplates items that belong to the blacklist
        # WHEN the handle function is called
        handle_gitlab_event(event_body=api_json_res.EVENT_FOR_UNSAFE)

        # THEN the call to change status the happened two times
        assert self.gitlab_change_status_mock.call_count == 2

        # AND THEN the payloads were in this order (one to pending, one to failed)
        assert self.gitlab_change_status_mock.call_args_list == [
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.PENDING),),
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.FAILED),),
        ]
    
    @patch.dict("os.environ", test_env)
    def test_skips_events_that_are_not_pushed_to(self):
         # Mock prep
        self.diff_mock.return_value = api_json_res.DIFF_DELETED_FILE

        # GIVEN an EVENT which contemplates items that belong to the blacklist
        # WHEN the handle function is called
        handle_gitlab_event(event_body=api_json_res.EVENT_FOR_UNSAFE)

        # THEN the call to change status the happened two times
        assert self.gitlab_change_status_mock.call_count == 2

        # AND THEN the payloads were in this order (one to pending, one to success - no scans ran)
        assert self.gitlab_change_status_mock.call_args_list == [
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.PENDING),),
            ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.SUCCESS),),
        ]   
    def test_ignores_blacklisted_items(self):
        override_env = {
            "GITLAB_TOKEN": "Testing Token",
            "GITLAB_URI": "Testing Instance",
            "CONFIG_LOCATION": f"{self.test_dir_data}/config_with_blacklists.yaml",
        }

        with patch.dict("os.environ", override_env):
            # Mock prep
            self.diff_mock.return_value = api_json_res.DIFF_FILE_BLACKLIST

            # GIVEN an EVENT which contemplates items that belong to the blacklist
            # WHEN the handle function is called
            handle_gitlab_event(event_body=api_json_res.EVENT_FOR_UNSAFE)

            # THEN the call to change status the happened two times
            assert self.gitlab_change_status_mock.call_count == 2

            # AND THEN the payloads were in this order (one to pending, one to success)
            assert self.gitlab_change_status_mock.call_args_list == [
                ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.PENDING),),
                ((api_json_res.EVENT_FOR_UNSAFE.get("project").get("id"), "test_sha", CommitStatus.SUCCESS),),
            ]

    @patch.dict("os.environ", test_env)
    def test_parses_config_from_repo(self):
        # GIVEN GitLab returns the repo has a config file that does not contain signatures or blacklists
        self.gitlab_config_mock.return_value = True, "test: 'Field'"

        # WHEN the class is instantiated
        cli = _GitLab(hostname="test", token="test")

        # AND WHEN we request to fetch the config and assign the results back to
        exists, content = cli.config_in_repo("123")
        assert exists is True

        cli.session = Session(content)

        # THEN the cli's session has empty signatures and blacklists
        assert cli.session.signatures == []
        assert cli.session.blacklists == []
