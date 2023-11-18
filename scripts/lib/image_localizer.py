import hashlib
import re
from mimetypes import guess_extension
from pathlib import Path
from warnings import warn

import requests

BOOK_DIR = Path("lesswrong.com/book.english")
IMAGES_DIR = Path("img")

REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}

BLANK_IMAGE = "data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HA\
wCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="


def download_image(url: str) -> Path:
    response = requests.get(url=url, timeout=REQUEST_TIMEOUT, allow_redirects=True, headers=HEADERS)

    if not response.ok:
        warn(f"Image {url} not downloaded: {response}", stacklevel=2)
        return None

    img_ext = guess_extension(response.headers["content-type"])
    img_name = hashlib.md5(url.encode("UTF-8")).hexdigest()
    img_p = BOOK_DIR / IMAGES_DIR / f"{img_name}{img_ext}"

    img_p.write_bytes(response.content)

    return img_p.relative_to(BOOK_DIR)


def localize(html_content: str) -> str:
    downloaded = []

    for src in re.findall(r"""<img.+?src=['"]([^'"]+?)['"].*?>""", html_content):
        file_p = download_image(src)
        downloaded.append([src, file_p])

    for img in downloaded:
        new_src = img[1] if img[1] else BLANK_IMAGE
        html_content = html_content.replace(img[0], str(new_src))

    return html_content
