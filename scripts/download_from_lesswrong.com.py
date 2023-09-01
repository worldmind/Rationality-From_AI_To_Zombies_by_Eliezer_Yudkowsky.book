import json
import logging as log
from pathlib import Path
from time import sleep

import lib.lesswrong as lw

log.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=log.INFO)

ROOT = Path("lesswrong.com/")
COLLECTION_SLUG = "rationality"


def format_dirname(i: int, dirname: str) -> str:
    # for dirname like "Abc/Bcd"
    dirname = dirname.replace("/", "|").replace(" ", "_")

    # numerated directory name
    return f"{i:02}_{dirname}"


def get_intro(sequence: dict) -> dict:
    return {
        "title": "Intro",
        "contents": {"html": sequence["contents"]["html"]},
        "modifiedAt": sequence["contents"]["editedAt"],
        "_id": sequence["_id"],
        "user": sequence["user"],
        "pageUrl": "https://www.lesswrong.com/s/" + sequence["_id"],
        "author": None,
        "organizers": [],
        "coauthors": [],
        "reviewedByUser": None,
        "tags": [],
    }


def write_collection(path: Path, collection: dict) -> dict:
    posts_for_download = {}

    for book_i, book in enumerate(collection["books"]):
        book_dirname = format_dirname(book_i + 1, book["title"])

        for sequence_i, sequence in enumerate(book["sequences"]):
            sequence_dirname = format_dirname(sequence_i + 1, sequence["title"])

            post_i = 1

            if sequence.get("contents"):
                post_i = 0
                intro_post = get_intro(sequence)
                sequence["chapters"][0]["posts"].insert(0, intro_post)

            for chapter in sequence["chapters"]:
                for post in chapter["posts"]:
                    post_dirname = format_dirname(post_i, post["title"])
                    post_p = path / book_dirname / sequence_dirname / post_dirname

                    post_p.mkdir(parents=True, exist_ok=True)

                    if post_i == 0:
                        log.info(
                            "Create data files for a fake 'Intro' post at '%s'",
                            post_p.absolute(),
                        )
                        write_post(post_p, post)
                    else:
                        posts_for_download[post["_id"]] = post_p

                    post_i += 1

    return posts_for_download


def write_post(path: Path, post: dict) -> None:
    metadata = {
        "id": post["_id"],
        "modified_at": post["modifiedAt"] or post["postedAt"],
        "url": post["pageUrl"],
        "user": post["user"]["displayName"],
        "author": post["author"],
    }

    metadata["organizers"] = [o["displayName"] for o in post["organizers"]]
    metadata["coauthors"] = [c["displayName"] for c in post["coauthors"]]
    metadata["reviewer"] = (
        post["reviewedByUser"]["displayName"] if post.get("reviewedByUser") else None
    )

    metadata["tags"] = [t["name"] for t in post["tags"]]

    p = path / "metadata"
    p.write_text(json.dumps(metadata))

    p = path / "content.html"
    p.write_text(post["contents"]["html"])


def main() -> None:
    log.info("Download collection '%s'", COLLECTION_SLUG)
    collection = lw.download_collection(COLLECTION_SLUG)

    collection = collection["data"]
    base_p = ROOT / collection["title"]

    log.info("Create directory tree at '%s'", base_p.absolute())
    posts_for_download = write_collection(base_p, collection)

    for post_id, path in posts_for_download.items():
        log.info("Download post _id=%s", post_id)
        post = lw.download_post(post_id)

        log.info("Create data files for a post[%s] at '%s'", post_id, path.absolute())
        write_post(path, post["data"])
        sleep(1)


if __name__ == "__main__":
    main()
