import logging
from typing import Dict, List

import yaml

from .blacklists import BlacklistItem, Extension, Path
from .signatures import Signature, SimpleSignature, PatternSignature


class Session:
    def __init__(self, config_content):
        self._logger = logging.getLogger(__name__ + "." + self.__module__.split(".")[-1])
        self._config = self._load_config(config_content)
        self.signatures = self._parse_signatures()
        self.blacklists = self._parse_blacklists()

    def _load_config(self, contents) -> Dict:
        return yaml.safe_load(contents)

    def _parse_signatures(self) -> List[Signature]:
        signatures = []

        for signature in self._config.get("signatures", {}):
            if signature.get("match", "") != "":
                signatures.append(
                    SimpleSignature(
                        name=signature.get("name"),
                        part=signature.get("part"),
                        match=signature.get("match"),
                    )
                )
            else:
                signatures.append(
                    PatternSignature(
                        name=signature.get("name"),
                        part=signature.get("part"),
                        regex=signature.get("regex"),
                    )
                )
        return signatures

    def _parse_blacklists(self) -> List[BlacklistItem]:
        blacklist = []

        for item in self._config.get("blacklists", {}).get("extensions", []):
            blacklist.append(Extension(text=item))

        for item in self._config.get("blacklists", {}).get("paths", []):
            blacklist.append(Path(text=item))

        return blacklist
