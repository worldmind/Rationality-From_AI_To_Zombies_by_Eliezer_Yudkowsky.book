import os
import re
from pathlib import Path
from typing import TypeVar

Self = TypeVar("Self", bound="Config")

VARS_RE = re.compile(r"""^\s*?(?P<name>[\w_\d]+?)=(?P<value>.+?)$""")


class Config:
    _instance = None

    def __new__(cls: Self) -> Self:
        if Config._instance:
            return Config._instance

        Config._instance = super().__new__(cls)
        return Config._instance

    def __init__(self: Self) -> None:
        if hasattr(self, "data"):
            return

        file_p = Path(os.environ["CONFIG_FILE"])
        self.data = {}

        def load() -> None:
            with file_p.open() as f:
                while line := f.readline():
                    if m := VARS_RE.search(line):
                        self.data[m["name"]] = m["value"]

        load()

    def get(self: Self, varname: str) -> str:
        return self.data.get(varname)
