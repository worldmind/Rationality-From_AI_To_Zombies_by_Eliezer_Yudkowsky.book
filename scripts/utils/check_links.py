import hashlib
import json
import logging as log
import pathlib
import re
import urllib.parse as url_parser
from http import HTTPStatus

import requests

log.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=log.INFO)

SEARCH_IN_DIR = "lesswrong.com/"

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}
REQUEST_TIMEOUT = 30

_CACHE = {}


def is_broken(url: str) -> bool:
    md5 = hashlib.md5(url.encode("UTF-8")).hexdigest()

    if md5 in _CACHE:
        log.info("%s: missed as not first attempt: %s", url, _CACHE[md5]["status"])
        return _CACHE[md5]["is_broken"]

    try:
        response = requests.head(
            url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            headers=REQUEST_HEADERS,
        )

        # Not allowed method HEAD
        if response.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                headers=REQUEST_HEADERS,
            )

        _CACHE[md5] = {
            "is_broken": not response.ok,
            "status": f"{response.status_code} {response.reason}",
        }
    except requests.exceptions.RequestException as err:
        _CACHE[md5] = {
            "is_broken": True,
            "status": str(err),
        }

    log.info("%s: %s", url, _CACHE[md5]["status"])
    return _CACHE[md5]["is_broken"]


def check(file: pathlib.Path) -> None:
    html = file.read_text()

    meta = file.with_name("metadata").read_text()
    meta = json.loads(meta)
    base_url = meta["url"]

    for link in re.findall(
        r"""(<a.+?href=["']([^'"]+?)["'][^>]*?>.+?</a>)""",
        html,
    ):
        if re.match(r"^#", link[1]):
            continue

        url = url_parser.urljoin(base_url, link[1])

        if is_broken(url):
            print(base_url, "\t", link[0])


def main() -> None:
    p = pathlib.Path(SEARCH_IN_DIR)

    print("page\tlink")
    for f in p.glob("**/*.html"):
        check(f)


if __name__ == "__main__":
    main()
