import json
import re
from pathlib import Path

from lib.config import Config
from lib.htmlbook import HTMLBook


def read_lw_links() -> dict:
    file_p = Path(__file__.replace(".py", ".json"))
    return json.loads(file_p.read_text())


def collect_crosslinks() -> dict:
    html_dir = Path(Config().get("SRC_HTML_DIR"))

    links = {}
    for book_dir in filter(lambda x: x.is_dir(), html_dir.iterdir()):
        book = HTMLBook(book_dir)
        links[book.url] = {
            "book_id": book.xml_id,
            "part_id": book.xml_id,
        }

        for part_dir in book_dir.glob(f"**/{HTMLBook.info_fn}"):
            part = HTMLBook(part_dir.parent)
            links[part.url] = {
                "book_id": book.xml_id,
                "part_id": part.xml_id,
            }

    return links


# some paths on the site have been changed and are now redirected to others
TO_UPDATE = read_lw_links()
# book parts URLs
CROSSLINKS = collect_crosslinks()


def update(m: re.Match) -> str:
    url = m[1]
    attrs = []

    if TO_UPDATE.get(url):
        url = TO_UPDATE[url]
        attrs.append(f'href="{url}"')

    if CROSSLINKS.get(url):
        attrs.append(f'data-targetdoc="{CROSSLINKS[url]["book_id"]}"')
        attrs.append(f'data-targetptr="{CROSSLINKS[url]["part_id"]}"')

    return f'<a {" ".join(attrs)}' if len(attrs) else m[0]


def set_crosslinks(html: str) -> str:
    return re.sub(
        r"""<a.+?href=["']([^'"]+?)['"]""",
        update,
        html,
        flags=(re.MULTILINE | re.DOTALL),
    )
