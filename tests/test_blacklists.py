from unittest import TestCase

from shhbt.blacklists import Extension, Path


class TestUtilsConfig(TestCase):
    def test_can_match_extension(self):
        # GIVEN an extension we want to exclude
        extension = "pem"

        # WHEN the blacklist item is created
        ext = Extension(text=extension)
        self.assertIsNotNone(ext)

        # AND WHEN the match function is called
        result = ext.match_item(file_path="something", extension="pem")

        # THEN it should return True
        self.assertTrue(result)

    def test_can_match_path(self):
        # GIVEN a path we want to exclude
        path = "tests"

        # WHEN the blacklist item is created
        path = Path(text=path)

        # AND WHEN the match function is called
        result = path.match_item(file_path="/a/b/s/tests/f/c.java", extension="java")

        # THEN it should return True
        self.assertTrue(result)

        # BUT WHEN the match function is called with a path that does not contain the path
        result = path.match_item(file_path="a/b/notests/f/a.java", extension="java")

        # THEN it should return False
        self.assertFalse(result)
