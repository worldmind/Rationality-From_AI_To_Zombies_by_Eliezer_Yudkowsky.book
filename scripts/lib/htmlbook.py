#
# it's a draft version of html book class
#

import json
from pathlib import Path
from typing import TypeVar

Self = TypeVar("Self", bound="HTMLBook")


class HTMLBook:
    info_fn = "metadata"
    content_fn = "content.html"

    def __init__(
        self: Self,
        book_dir: Path,
    ) -> None:
        self._content_p = book_dir / self.content_fn
        self._content = None

        info = json.loads((book_dir / self.info_fn).read_text())

        self.xml_id = f'item_{info["id"]}'
        self.path = book_dir
        self.reviewers = []

        for k in [
            "title",
            "url",
            "modified_at",
            "author",
            "coauthors",
            "tags",
            "user",
            "reviewer",
        ]:
            setattr(self, k, info.get(k))

    def get_content(self: Self) -> str:
        if self._content is None:
            if self._content_p.exists():
                self._content = self._content_p.read_text()
            else:
                self._content = ""

        return self._content
