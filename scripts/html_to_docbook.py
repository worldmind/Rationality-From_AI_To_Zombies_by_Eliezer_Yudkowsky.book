import logging as log
import os
import re
from pathlib import Path

import lib.bibliography as bglib
import lib.docbook_template as dbtemplate
import lib.html_normalizer as html_norm
from lib import footnote, herold, lw_links
from lib.config import Config
from lib.htmlbook import HTMLBook

log.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=log.DEBUG)
conf = Config()

HTML_PATH = Path(conf.get("HTML_SRC_DIR"))
BOOK_PATH = Path(conf.get("BOOK_DIR"))
BOOK_EXT = conf.get("BOOK_EXT")


def collect_persons(book_info: dict, item: HTMLBook) -> None:
    book_info.setdefault("user", {})
    book_info.setdefault("reviewer", {})

    if item.user:
        book_info["user"][item.user] = book_info["user"].setdefault(item.user, 0) + 1

    if item.reviewer:
        book_info["reviewer"][item.reviewer] = 1


def set_publication_date(book_info: dict, item: dict) -> None:
    if item.modified_at is None:
        return

    if book_info.get("modified_at") is None or book_info["modified_at"] < item.modified_at:
        book_info["modified_at"] = item.modified_at


def get_authors(book_info: dict) -> list:
    return sorted(
        book_info["user"].keys(),
        key=lambda x: book_info["user"][x],
        reverse=True,
    )


def get_reviewers(book_info: dict) -> list:
    return list(filter(lambda x: not book_info["user"].get(x), book_info["reviewer"]))


def gen_filename(i: int, title: str) -> str:
    title = re.sub(r"[^\w\d\s]", "", title)
    title = re.sub(r"^\s+|\s+$", "", title)
    title = re.sub(r"\s+", "_", title)

    return f"{i:02}_{title}"


def prepare_content(level: int, item: HTMLBook, child_items: list[Path]) -> None:
    content = item.get_content()

    if content:
        log.debug("normalize html: %s", item.path)
        content = html_norm.normalize(content)

        log.debug("make markup for footnotes: %s", item.path)
        content = footnote.make(content)

        log.debug("make markup for bibliography: %s", item.path)
        content = bglib.make(content)

        log.debug("make markup for crosslinks: %s", item.path)
        content = lw_links.set_crosslinks(content)

        log.debug("convert html to docbook markup: %s", item.path)
        content = herold.convert(content)

    log.debug("wrap docbook fragment: %s", item.path)
    return dbtemplate.wrap(level, item, content, child_items)


def make_item(
    html_dir: Path,
    book_dir: Path,
    level: int,
    item_num: int,
    book_info: dict,
) -> Path:
    log.info("make_item: %s", html_dir)
    item = HTMLBook(html_dir)

    collect_persons(book_info, item)
    set_publication_date(book_info, item)

    book_dn = gen_filename(item_num, item.title)
    child_items = []
    html_subdirs = [d for d in sorted(html_dir.iterdir()) if d.is_dir()]

    if len(html_subdirs):
        book_subdir = book_dir / book_dn
        book_subdir.mkdir(parents=True, exist_ok=True)

        for i, html_subdir in enumerate(html_subdirs, 1):
            child_p = make_item(html_subdir, book_subdir, level + 1, i, book_info)
            # don't use pathlib "relative_to", return value is different in some cases
            child_p = Path(os.path.relpath(child_p.as_posix(), book_dir.as_posix()))
            child_items.append(child_p)

    if level == 0:
        authors = get_authors(book_info)
        item.author = authors.pop(0)
        item.coauthors = authors
        item.reviewers = get_reviewers(book_info)
        item.modified_at = book_info["modified_at"]

    content = prepare_content(level, item, child_items)
    book_p = book_dir / f"{book_dn}{BOOK_EXT}"
    book_p.write_text(content)

    return book_p


def main() -> None:
    for i, html_dir in enumerate(filter(lambda x: x.is_dir(), sorted(HTML_PATH.iterdir())), 1):
        make_item(html_dir, BOOK_PATH, 0, i, dict())

    log.debug("All done!")


if __name__ == "__main__":
    main()
