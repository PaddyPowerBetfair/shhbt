import os
import re
from unittest import TestCase
from unittest.mock import patch

import pytest

from shhbt.session import Session
from shhbt.signatures import SimpleSignature, PatternSignature


class TestUtilsSignatures(TestCase):
    test_dir_data = f"{os.path.dirname(__file__)}/data"

    def test_raises_if_wrong_details_are_passed_to_Simple(self):
        with pytest.raises(AttributeError):
            SimpleSignature(match="valid match", part="", name="")

        with pytest.raises(AttributeError):
            SimpleSignature(match="", part="valid part", name="valid name")

    def test_raises_if_wrong_details_are_passed_to_Pattern(self):
        with pytest.raises(AttributeError):
            PatternSignature(regex="valid regex", part="", name="")

        with pytest.raises(AttributeError):
            PatternSignature(regex="", part="valid part", name="valid name")

    def test_can_match_extension(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_extension_match.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)

                self.assertEqual(1, len(session.signatures))
                sig = session.signatures[0]

                match, part = sig.match(
                    path="/sample/path/fake_cert.pem",
                    filename="fake_cert.pem",
                    extension="pem",
                    content="",
                )
                self.assertTrue(isinstance(sig, SimpleSignature))
                self.assertEqual(part, "extension")
                self.assertEqual("pem", sig.to_match)

    def test_can_match_filename(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_filename_match.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)
                self.assertEqual(1, len(session.signatures))
                sig = session.signatures[0]
                match, part = sig.match(
                    path="/sample/path/filezilla.xml",
                    filename="filezilla.xml",
                    extension="xml",
                    content="",
                )

                self.assertTrue(isinstance(sig, SimpleSignature))
                self.assertEqual(part, "filename")
                self.assertEqual("filezilla.xml", sig.to_match)

    def test_can_match_path_part(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_path_match.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)
                self.assertEqual(1, len(session.signatures))
                sig = session.signatures[0]

                match, part = sig.match(
                    path="/purple/accounts.yml",
                    filename="accounts.yml",
                    extension=".yml",
                    content="",
                )

                self.assertTrue(isinstance(sig, SimpleSignature))
                self.assertEqual(part, "path")
                self.assertEqual("/purple/accounts.yml", sig.to_match)

    def test_can_match_regex_in_path(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_path_regex.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)
                self.assertEqual(1, len(session.signatures))
                sig = session.signatures[0]

                match, part = sig.match(
                    path="/sample/path/purple/accounts.xml",
                    filename="accounts.xml",
                    extension=".xml",
                    content="",
                )
                self.assertTrue(isinstance(sig, PatternSignature))
                self.assertEqual(part, "path")
                self.assertEqual(re.compile(r"\.?purple/accounts\.xml$"), sig.regex)

    def test_can_match_regex_in_extension(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_extension_regex.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)
                self.assertEqual(1, len(session.signatures))
                sig = session.signatures[0]

                match, part = sig.match(
                    path="/sample/path/x.keystore",
                    filename="x.keystore",
                    extension="keystore",
                    content="",
                )
                self.assertTrue(isinstance(sig, PatternSignature))
                self.assertEqual(part, "extension")
                self.assertEqual(re.compile("^key(store|ring)$"), sig.regex)

    def test_can_match_regex_in_filename(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_filename_regex.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)
                self.assertEqual(1, len(session.signatures))
                sig = session.signatures[0]

                match, part = sig.match(
                    path="/sample/path/.myhtpasswd",
                    filename=".htpasswd",
                    extension="htpasswd",
                    content="",
                )
                self.assertTrue(isinstance(sig, PatternSignature))
                self.assertEqual(part, "filename")
                self.assertEqual(re.compile(r"^\.?htpasswd$"), sig.regex)

    def test_can_match_regex_in_content(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_content_regex.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)
                self.assertEqual(1, len(session.signatures))
                sig = session.signatures[0]

                match, part = sig.match(
                    path=f"{self.test_dir_data}/file_key.txt",
                    filename="file_key.txt",
                    extension="txt",
                    content="-----BEGIN RSA PRIVATE KEY----\nSome fake RSA ID KEYADFADF\nNVJtV3JB83faCtSbiP7nn1ooLOY27yfKaKjlNJWgJMKUu853DkcniExXf1\n-----END OPENSSH PRIVATE KEY-----",
                )
                self.assertTrue(isinstance(sig, PatternSignature))
                self.assertEqual(part, "contents")
                self.assertEqual(re.compile("-----BEGIN (EC|RSA|DSA|OPENSSH) PRIVATE KEY----"), sig.regex)

    def test_handles_weird_config_nicely(self):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_unknown_part.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)

                assert len(session.signatures) == 2

                sig = session.signatures[0]

                match, part = sig.match(
                    path="/sample/path/filezilla.xml",
                    filename="filezilla.xml",
                    extension="xml",
                    content="",
                )

                assert isinstance(sig, SimpleSignature)
                assert match is False
                assert part is ""

                sig_2 = session.signatures[1]

                match, part = sig.match(
                    path="/sample/path/filezilla.xml",
                    filename="filezilla.xml",
                    extension="xml",
                    content="",
                )

                assert isinstance(sig_2, PatternSignature)
                assert match is False
                assert part is ""

    @patch("logging.Logger.exception")
    def test_parsing_back_signatures_returns_error(self, log_mock):
        with patch("os.environ", {"SCANNER_CONFIG_LOCATION": f"{self.test_dir_data}/config_with_invalid_regex.yaml"}):
            with open(file=os.getenv("SCANNER_CONFIG_LOCATION"), mode="r") as f:
                session = Session(f)  # GIVEN a config file with a single, yet invalid regex

            # THEN an error is catched and logged
            log_mock.assert_called_with(
                "Failed loading signature. Offending entry: %s",
                {
                    "part": "contents",
                    "regex": "(?i)linkedin(.{0,20})?(?-i)[''\"][0-9a-z]{12}[''\"]",
                    "name": "No in-the-middle global modifiers for Python.",
                },
            )

            # AND GIVEN there was only one signature in the file
            # THEN no signatures were loaded into the config file
            assert len(session.signatures) == 0
