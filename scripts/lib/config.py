import os
import re
from pathlib import Path
from typing import TypeVar

Self = TypeVar("Self", bound="Config")

VARS_RE = re.compile(r"""^\s*?(?P<name>[\w_\d]+?)=(?P<value>.+?)$""")


class Config:
    def __init__(self: Self) -> None:
        self.file = os.environ["CONFIG_FILE"]
        self.data = {}

        def load() -> None:
            with Path(self.file).open() as f:
                while line := f.readline():
                    if m := VARS_RE.search(line):
                        self.data[m["name"]] = m["value"]

        load()

    def get(self: Self, varname: str) -> str:
        return self.data.get(varname)
