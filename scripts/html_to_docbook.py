import json
import logging as log
import os
import re
from pathlib import Path

import lib.bibliography as bglib
import lib.docbook_template as dbtemplate
import lib.html_normalizer as html_norm
from lib import footnote, herold

log.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=log.DEBUG)

BASE_P = Path("lesswrong.com/Rationality: A-Z")

BOOK_PATH = Path("lesswrong.com/book.english")
BOOK_EXT = ".dbk"


def collect_persons(book_info: dict, meta: dict) -> None:
    book_info.setdefault("user", {})
    book_info.setdefault("reviewer", {})

    if meta.get("user"):
        book_info["user"][meta["user"]] = book_info["user"].setdefault(meta["user"], 0) + 1

    if meta.get("reviewer"):
        book_info["reviewer"][meta["reviewer"]] = 1


def set_publication_date(book_info: dict, meta: dict) -> None:
    if meta["modified_at"] is None:
        return

    if book_info.get("modified_at") is None or book_info["modified_at"] < meta["modified_at"]:
        book_info["modified_at"] = meta["modified_at"]


def get_authors(book_info: dict) -> list:
    return sorted(
        book_info["user"].keys(),
        key=lambda x: book_info["user"][x],
        reverse=True,
    )


def get_reviewers(book_info: dict) -> list:
    return list(filter(lambda x: not book_info["user"].get(x), book_info["reviewer"]))


def title_to_filename(title: str) -> str:
    title = re.sub(r"[^\w\d\s]", "", title)
    title = re.sub(r"^\s+|\s+$", "", title)
    return re.sub(r"\s+", "_", title)


def make_item(item_dir: Path, level: int, book_info: dict) -> Path:
    log.info("make_item: %s", item_dir)
    meta_p = item_dir / "metadata"
    meta = meta_p.read_text()
    meta = json.loads(meta)

    collect_persons(book_info, meta)
    set_publication_date(book_info, meta)

    child_items = []
    for subdir in filter(lambda x: x.is_dir(), sorted(item_dir.iterdir())):
        child_p = make_item(subdir, level + 1, book_info)
        parent_p = item_dir if level else BOOK_PATH
        child_p = Path(os.path.relpath(child_p.as_posix(), parent_p.as_posix()))
        child_items.append(child_p)

    content_p = item_dir / "content.html"
    content = ""

    if content_p.exists():
        content = content_p.read_text()

        log.debug("normalize html: %s", item_dir)
        content = html_norm.normalize(content)

        log.debug("make markup for footnotes: %s", item_dir)
        content = footnote.make(content)

        log.debug("make markup for bibliography: %s", item_dir)
        content = bglib.make(content)

        log.debug("convert html to docbook markup: %s", item_dir)
        content = herold.convert(content)

    book_p = item_dir / f"content{BOOK_EXT}"

    if level == 0:
        authors = get_authors(book_info)
        meta["author"] = authors.pop(0)
        meta["coauthors"] = authors
        meta["reviewers"] = get_reviewers(book_info)
        meta["modified_at"] = book_info["modified_at"]
        book_p = BOOK_PATH / f'{title_to_filename(meta["title"])}{BOOK_EXT}'

    log.debug("wrap docbook fragment: %s", item_dir)
    content = dbtemplate.wrap(level, meta, content, child_items)

    book_p.write_text(content)
    return book_p


def main() -> None:
    for book_dir in filter(lambda x: x.is_dir(), sorted(BASE_P.iterdir())):
        make_item(book_dir, 0, dict())
    log.debug("All done!")


if __name__ == "__main__":
    main()
