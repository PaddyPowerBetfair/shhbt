from enum import Enum
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

import requests

from shhbt.session import Session

class CommitStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class GitClient(ABC):
    def __init__(self, hostname: str, token: str) -> None:
        super().__init__()

        if hostname == "" or token == "" or not hostname or not token:
            raise ValueError("Client cannot be instantiated without a valid hostname and token.")

        self.logger = logging.getLogger(__name__ + "." + self.__module__.split(".")[-1])
        self.http_session = requests.Session()
        self.hostname = hostname
        self.token = token

    @abstractmethod
    def handle_event(self, event: Dict[str, Any]):
        pass

    @abstractmethod
    def config_in_repo(self, proj_id: str) -> Tuple[bool, Optional[str]]:
        pass

class Options:
    """
    The purpose of this class is to define params for specific behaviors in the clients.
    Pass the kwargs from the instantiated Client to override the default params.
    """
    def __init__(self, **kwargs):
        self.threads = kwargs.get("threads", 4)