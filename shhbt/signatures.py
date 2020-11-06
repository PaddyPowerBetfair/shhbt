import re

from abc import ABC, abstractmethod
from typing import Tuple, List


class Signature(ABC):
    TYPE_SIMPLE = "simple"
    TYPE_PATTERN = "pattern"

    PART_EXTENSION = "extension"
    PART_FILENAME = "filename"
    PART_PATH = "path"
    PART_CONTENTS = "contents"

    def __init__(self, part: str, name: str):
        super().__init__()
        if part == "" or name == "":
            raise AttributeError("Invalid signature in config")
        self.part = part
        self.name = name

    @abstractmethod
    def match(self, path: str, filename: str, extension: str, content: str) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def get_content_matches(self, file_path: str) -> List[str]:
        pass


class SimpleSignature(Signature):
    def __init__(self, match: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if match == "":
            raise AttributeError("Invalid signature in config")
        self.to_match = match

    def match(self, path: str, filename: str, extension: str, content: str) -> Tuple[bool, str]:
        haystack = ""
        match_part = ""

        if self.part == self.PART_PATH:
            haystack = path
            match_part = self.PART_PATH
        elif self.part == self.PART_FILENAME:
            haystack = filename
            match_part = self.PART_FILENAME
        elif self.part == self.PART_EXTENSION:
            haystack = extension
            match_part = self.PART_EXTENSION
        else:
            return False, match_part

        return self.to_match == haystack, match_part

    def get_content_matches(self, file_content) -> List[str]:
        return []


class PatternSignature(Signature):
    def __init__(self, regex: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if regex == "":
            raise AttributeError("Invalid signature in config")
        self.regex = re.compile(regex)

    def match(self, path: str, filename: str, extension: str, content: str) -> Tuple[bool, str]:
        haystack = ""
        match_part = ""

        if self.part == self.PART_PATH:
            haystack = path
            match_part = self.PART_PATH
        elif self.part == self.PART_FILENAME:
            haystack = filename
            match_part = self.PART_FILENAME
        elif self.part == self.PART_EXTENSION:
            haystack = extension
            match_part = self.PART_EXTENSION
        elif self.part == self.PART_CONTENTS:
            haystack = content
            match_part = self.PART_CONTENTS
        else:
            return False, match_part

        return self.regex.search(haystack) is not None, match_part

    def get_content_matches(self, content: str) -> List[str]:
        matches = []
        for match in self.regex.finditer(content):
            matches.append(str(match[0]))

        return matches
