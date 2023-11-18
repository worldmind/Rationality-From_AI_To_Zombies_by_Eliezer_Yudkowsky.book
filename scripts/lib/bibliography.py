import re
from hashlib import md5

BIBLIOGRAPHY_REF_CLASS = "lwc_bibliographyref"
BIBLIOGRAPHY_ABBREV_CLASS = "lwc_bibliography_abbrev"
BIBLIOGRAPHY_BODY_CLASS = "lwc_bibliography"
BIBLIOGRAPHY_TEMPLATE = {
    "body": f'<span class="{BIBLIOGRAPHY_BODY_CLASS}">{{text}}</span>',
    "item": f'<span><span class="{BIBLIOGRAPHY_ABBREV_CLASS}">{{abbrev}}\
</span>{{text}}</span>',
    "reference": f'<span class="{BIBLIOGRAPHY_REF_CLASS}">{{abbrev}}</span>',
}

BIBLIOGRAPHY_RE_FLAGS = re.MULTILINE | re.DOTALL
BIBLIOGRAPHY_RE = {
    k: re.compile(v, BIBLIOGRAPHY_RE_FLAGS)
    for k, v in {
        "list": r"""<hr\s*?/?>((?:\s*?<p>.+?\(\d{4}\.?\).+?</p>\s*?)+?)\Z""",
        "item": r"""<p>(.+?)</p>""",
        "exists": BIBLIOGRAPHY_TEMPLATE["body"].format(text=r"""(?P<content>.+?)"""),
    }.items()
}


def get_id(text: str) -> str:
    return "bg_" + md5(text.encode("UTF-8")).hexdigest()


def form_ref(items: list) -> str:
    return "".join(
        BIBLIOGRAPHY_TEMPLATE["reference"].format(
            abbrev=get_id(item),
        )
        for item in items
    )


def form_content(items: list) -> str:
    return "".join(
        BIBLIOGRAPHY_TEMPLATE["item"].format(
            abbrev=get_id(item),
            text=item,
        )
        for item in items
    )


def add_content(content: str, html: str) -> str:
    if m := BIBLIOGRAPHY_RE["exists"].search(html):
        html = html.replace(m["content"], m["content"] + content)
    else:
        html += BIBLIOGRAPHY_TEMPLATE["body"].format(text=content)

    return html


def parse(x: list, bg: dict) -> None:
    bg["content"] = form_content(BIBLIOGRAPHY_RE["item"].findall(x[1]))


def make(html: str) -> str:
    bg = {"content": ""}

    html = BIBLIOGRAPHY_RE["list"].sub(
        lambda x: parse(x, bg),
        html,
    )

    if len(bg["content"]):
        html = add_content(bg["content"], html)

    return html
