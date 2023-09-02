import requests

API_URL = "https://www.lesswrong.com/graphql"

API_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
}

API_COLLECTION_QUERY = '{collection (input: {selector:{slug:"C_SLUG"}}) \
{result {title version books {title sequences {_id title user {displayName} \
contents {editedAt html} chapters {posts {title _id}}}}}}}'

API_POST_QUERY = '{post(input:{selector:{_id:"POST_ID"}}) \
{result{_id title author user{displayName}modifiedAt postedAt pageUrl \
contents{html} tags{name} organizers{displayName} coauthors{displayName} \
reviewedByUser{displayName}}}}'


def download_collection(slug: str) -> dict:
    payload = {"query": None, "variables": None, "operationName": None}
    payload["query"] = API_COLLECTION_QUERY.replace("C_SLUG", slug)

    response = requests.post(url=API_URL, json=payload, headers=API_HEADERS)
    collection = response.json()

    if collection is None or not isinstance(collection, dict):
        error = f"Invalid data {collection}"
        raise RuntimeError(error)

    if "errors" in collection:
        error = (
            "Invalid API request: "
            + collection["errors"][0]["message"]
            + " / "
            + collection["errors"][0]["extensions"]["code"]
        )
        raise RuntimeError(error)

    collection["data"] = collection["data"]["collection"]["result"]

    return collection


def download_post(post_id: str) -> dict:
    payload = {"query": None, "variables": None, "operationName": None}
    payload["query"] = API_POST_QUERY.replace("POST_ID", post_id)

    response = requests.post(url=API_URL, json=payload, headers=API_HEADERS)
    post = response.json()

    if post is None or not isinstance(post, dict):
        error = f"Invalid data {post}"
        raise RuntimeError(error)

    if "errors" in post:
        error = (
            "Invalid API request: "
            + post["errors"][0]["message"]
            + " / "
            + post["errors"][0]["extensions"]["code"]
        )
        raise RuntimeError(error)

    post["data"] = post["data"]["post"]["result"]

    return post
