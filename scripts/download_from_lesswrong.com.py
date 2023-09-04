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
    dirname = dirname.replace("/", "|").strip().replace(" ", "_")

    # numerated directory name
    return f"{i:02}_{dirname}"


def collection_data(collection: dict) -> dict:
    data = {
        "id": collection["_id"],
        "title": collection["title"],
        "modified_at": collection["createdAt"],
        "url": f"{lw.SITE_URL}/{COLLECTION_SLUG}",
        "user": collection["user"]["displayName"],
        "author": None,
        "organizers": [],
        "coauthors": [],
        "reviewer": None,
        "tags": [],
        "content": None,
    }

    if collection.get("contents"):
        data["content"] = collection["contents"]["html"]
        data["reviewer"] = collection["contents"]["user"]["displayName"]

    return data


def book_data(book: dict) -> dict:
    data = {
        "id": book["_id"],
        "title": book["title"],
        "modified_at": book["createdAt"],
        "url": f'{lw.SITE_URL}/{COLLECTION_SLUG}#{book["_id"]}',
        "user": None,
        "author": None,
        "organizers": [],
        "coauthors": [],
        "reviewer": None,
        "tags": [],
        "content": None,
    }

    if book.get("contents"):
        data["content"] = book["contents"]["html"]
        data["reviewer"] = book["contents"]["user"]["displayName"]

    return data


def sequence_data(sequence: dict) -> dict:
    data = {
        "id": sequence["_id"],
        "title": sequence["title"],
        "modified_at": None,
        "url": f'{lw.SITE_URL}/s/{sequence["_id"]}',
        "user": sequence["user"]["displayName"],
        "author": None,
        "organizers": [],
        "coauthors": [],
        "reviewer": None,
        "tags": [],
        "content": None,
    }

    if sequence.get("contents"):
        data["modified_at"] = sequence["contents"]["editedAt"]
        data["content"] = sequence["contents"]["html"]
        data["reviewer"] = sequence["contents"]["user"]["displayName"]

    return data


def post_data(post: dict) -> dict:
    data = {
        "id": post["_id"],
        "title": post["title"],
        "modified_at": post["modifiedAt"] or post["postedAt"],
        "url": post["pageUrl"],
        "user": post["user"]["displayName"],
        "content": post["contents"]["html"],
        "author": post["author"],
    }

    data["organizers"] = [o["displayName"] for o in post["organizers"]]
    data["coauthors"] = [c["displayName"] for c in post["coauthors"]]
    data["reviewer"] = (
        post["reviewedByUser"]["displayName"] if post.get("reviewedByUser") else None
    )

    data["tags"] = [t["name"] for t in post["tags"]]

    return data


def write_collection(path: Path, collection: dict) -> dict:
    log.info(
        "Create data files for collection[%s] at '%s'",
        collection["_id"],
        path.absolute(),
    )
    write_data(path, collection_data(collection))

    posts_for_download = {}

    for book_i, book in enumerate(collection["books"]):
        book_dirname = format_dirname(book_i + 1, book["title"])
        book_p = path / book_dirname

        log.info(
            "Create data files for book[%s] at '%s'",
            book["_id"],
            book_p.absolute(),
        )
        write_data(book_p, book_data(book))

        for sequence_i, sequence in enumerate(book["sequences"]):
            sequence_dirname = format_dirname(sequence_i + 1, sequence["title"])
            sequence_p = book_p / sequence_dirname

            log.info(
                "Create data files for sequence[%s] at '%s'",
                sequence["_id"],
                sequence_p.absolute(),
            )
            write_data(sequence_p, sequence_data(sequence))

            post_i = 1

            for chapter in sequence["chapters"]:
                for post in chapter["posts"]:
                    post_dirname = format_dirname(post_i, post["title"])
                    post_p = sequence_p / post_dirname
                    posts_for_download[post["_id"]] = post_p
                    post_i += 1

    return posts_for_download


def write_data(path: Path, data: dict) -> None:
    path.mkdir(parents=True, exist_ok=True)

    content = data.pop("content")

    p = path / "metadata"
    p.write_text(json.dumps(data))

    if content:
        p = path / "content.html"
        p.write_text(content)


def main() -> None:
    log.info("Download collection '%s'", COLLECTION_SLUG)
    collection = lw.download_collection(COLLECTION_SLUG)

    base_p = ROOT / collection["title"]

    log.info("Create directory tree at '%s'", base_p.absolute())
    posts_for_download = write_collection(base_p, collection)

    for post_id, path in posts_for_download.items():
        log.info("Download post _id=%s", post_id)
        post = lw.download_post(post_id)

        log.info("Create data files for a post[%s] at '%s'", post_id, path.absolute())
        write_data(path, post_data(post))
        sleep(1)

    log.info("All done")


if __name__ == "__main__":
    main()
