import os
from unittest import TestCase
from unittest.mock import patch

import pytest

from shhbt.session import Session


class TestSession(TestCase):
    test_dir_data = f"{os.path.dirname(__file__)}/data"

    @patch("shhbt.session.Session._parse_signatures")
    def test_loads_config_if_it_exists(self, _):
        # Override settings location for testing purposes
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config.yaml"}):
            # GIVEN a config file that exists
            assert os.path.exists(os.getenv("SCANNER_CONFIG_LOCATION")) is True

            # AND GIVEN that file only contains one entrie -> test: "field"
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as file:
                init_pos = file.tell()
                line1 = file.readline()
                line2 = ""
                assert 'test: "field"' == line1
                assert "" == line2
                file.seek(init_pos)

                # WHEN the session class is instanciated
                session = Session(file)

                # THEN the session object should contain a config attribute with the same fields
                assert session.signatures is not None

    def test_raises_error_if_tokens_missing(self):
        # Override settings location for testing purposes
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/wrong_config.yaml"}):
            # GIVEN a config file missing gitlab tokens
            assert os.path.exists(os.getenv("SCANNER_CONFIG_LOCATION")) is False

            # WHEN the session class is instanciated
            # THEN an AttributeError is raised because the file does not exist
            with pytest.raises(FileNotFoundError), open(os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as file:
                Session(file)

    def test_can_parse_many_signatures(self):
        # Override settings location for testing purposes
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_sig.yaml"}):
            # GIVEN a config file with some signatures
            assert os.path.exists(os.getenv("SCANNER_CONFIG_LOCATION")) is True

            # WHEN the session is initialized
            with open(os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as file:
                session = Session(file)

            # THEN it should create 6 signatures
            assert session.signatures is not None
            assert len(session.signatures) == 6
