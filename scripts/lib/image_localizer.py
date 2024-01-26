import hashlib
import os
import re
from mimetypes import guess_extension
from pathlib import Path
from warnings import warn

import requests

REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}

BLANK_IMAGE = "data:image/png;base64,\
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HA\
wCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="


def download_image(url: str, img_dir: Path, html_dir: Path) -> Path:
    response = requests.get(url=url, timeout=REQUEST_TIMEOUT, allow_redirects=True, headers=HEADERS)

    if not response.ok:
        warn(f"Image {url} not downloaded: {response}", stacklevel=2)
        return None

    img_ext = guess_extension(response.headers["content-type"])
    img_name = hashlib.md5(url.encode("UTF-8")).hexdigest()
    img_p = img_dir / f"{img_name}{img_ext}"

    img_p.write_bytes(response.content)

    # don't use pathlib "relative_to", return value is different in some cases
    return Path(os.path.relpath(img_p.as_posix(), html_dir.as_posix()))


def localize(html_content: str, html_dir: Path, img_dir: Path) -> str:
    downloaded = []

    for src in re.findall(r"""<img.+?src=['"]([^'"]+?)['"].*?>""", html_content):
        file_p = download_image(src, img_dir, html_dir)
        downloaded.append([src, file_p])

    for img in downloaded:
        new_src = img[1] if img[1] else BLANK_IMAGE
        html_content = html_content.replace(img[0], str(new_src))

    return html_content
