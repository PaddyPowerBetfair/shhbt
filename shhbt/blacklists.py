import re
from abc import ABC, abstractmethod
from enum import Enum


class BlacklistItem(ABC):
    class Types(Enum):
        EXTENSION = "extension"
        PATH = "path"

    def __init__(self):
        super().__init__()

    @abstractmethod
    def match_item(self, file_path: str, extension: str) -> bool:
        pass


class Extension(BlacklistItem):
    def __init__(self, text: str):
        super().__init__()
        self.part = BlacklistItem.Types.EXTENSION
        self.text = text

    def match_item(self, file_path: str, extension: str) -> bool:
        return self.text == extension


class Path(BlacklistItem):
    def __init__(self, text: str):
        super().__init__()
        self.part = BlacklistItem.Types.PATH
        self.text = re.compile(f"^.*?(/{text}/).*?$")

    def match_item(self, file_path: str, extension: str) -> bool:
        return self.text.search(file_path) is not None
