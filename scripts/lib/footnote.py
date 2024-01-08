import re
from hashlib import md5
from re import Pattern

import lib.bibliography as bglib

FOOTNOTE_RE_FLAGS = re.MULTILINE | re.DOTALL
FOOTNOTES_RE = [
    {
        "reference": re.compile(item[0], FOOTNOTE_RE_FLAGS),
        "description": re.compile(item[1], FOOTNOTE_RE_FLAGS),
    }
    for item in (
        [
            r"""\s*?<sup><a[^>]+?href=["']#[^"']+?["'][^>]*?>([\d,]+)</a></sup>""",
            r"""<p><span><sup><a[^>]*?>(\d+)</a></sup></span>(.+?)</p>""",
        ],
        [
            r"""\s*?(?:<a[^>]*?>)?<sup>([\d,]+)</sup>(?:</a>)?""",
            r"""<p><sup>(\d+)\s*?</sup>(.+?)</p>""",
        ],
        [
            r"""\s*?\[([\d,]+)\]""",
            r"""<h6>\s*?(\d+)\.\s+?(.+?)</h6>""",
        ],
        [
            r"""\s*?(?:<a[^>]*?>)?<sup>([\d,]+)</sup>(?:</a>)?""",
            r"""<p><a[^>]*?><sup>(\d+)</sup></a>(.+?)</p>""",
        ],
        [
            r"""\s*?\[([\d,]+)\]""",
            r"""<p>\[(\d+)\]\s+?(.+?)</p>""",
        ],
        [
            r"""<span class="mjpage">.+?>(\d+)</span></span></span></span></span>""",
            r"""<p class="mjx-desc">(\d+)\s+?(.+?)</p>""",
        ],
    )
]

FOOTNOTE_ORIG_CLASS = "lwc_footnote"
FOOTNOTE_REF_CLASS = "lwc_footnoteref"
FOOTNOTE_TEMPLATE = {
    "original": f'<span class="{FOOTNOTE_ORIG_CLASS}" id="{{id}}">\
<span>{{text}}</span></span>',
    "reference": f'<span class="{FOOTNOTE_REF_CLASS}" data-href="{{id}}"/>',
    "lost": "<p>See also...{fn_list}</p>",
}


def parse_description(
    x: list,
    footnotes: dict,
    one_line_re: Pattern[str] = re.compile(r"[\n\r]+|\s{2,}"),
) -> None:
    footnotes[x[1]] = {
        "text": one_line_re.sub(" ", x[2]),
        "count": 0,
    }


def get_id(text: str) -> str:
    return "fn_" + md5(text.encode("UTF-8")).hexdigest()


def footnote_by_ref(
    x: list,
    footnotes: dict,
    separator_re: Pattern[str] = re.compile(r",\s*?"),
) -> list:
    return [footnotes[fn_id] for fn_id in separator_re.split(x[1]) if footnotes.get(fn_id)]


def form_footnote(x: list, footnotes: dict) -> str:
    fns = ""
    for fn in footnote_by_ref(x, footnotes):
        fn_type = "reference" if fn["count"] > 0 else "original"

        fns += FOOTNOTE_TEMPLATE[fn_type].format(
            id=get_id(fn["text"]),
            text=fn["text"],
        )
        fn["count"] += 1

    return fns


def form_bibliography_ref(x: list, footnotes: dict) -> str:
    fns = []
    for fn in footnote_by_ref(x, footnotes):
        fns.append(fn["text"])
        fn["count"] += 1

    return bglib.form_ref(fns)


def find_lost_footnotes(footnotes: dict) -> dict:
    return {k: v for k, v in footnotes.items() if v["count"] == 0}


def form_lost_footnotes(
    html: str,
    fn_re: dict,
    footnotes: dict,
) -> str:
    lost_fns = find_lost_footnotes(footnotes)

    if len(lost_fns) == 0:
        return html

    # footnote can be inside prepared footnotes
    (html, bibliograthy) = form_bibliography(html, fn_re, lost_fns)

    # really lost footnotes
    lost_fns = find_lost_footnotes(lost_fns)

    if len(lost_fns):
        html += FOOTNOTE_TEMPLATE["lost"].format(
            fn_list=form_footnote(
                [None, ",".join(lost_fns.keys())],
                footnotes,
            ),
        )

    if len(bibliograthy):
        html = bglib.add_content(bibliograthy, html)

    return html


def form_bibliography(
    html: str,
    fn_re: dict,
    footnotes: dict,
) -> str:
    html = fn_re["reference"].sub(
        lambda x: form_bibliography_ref(x, footnotes),
        html,
    )

    bibliography = bglib.form_content(
        [fn["text"] for fn in footnotes.values() if fn["count"]],
    )

    return (html, bibliography)


def make(html: str) -> str:
    footnotes = {}

    i = 0
    while len(footnotes) == 0 and i < len(FOOTNOTES_RE):
        html = FOOTNOTES_RE[i]["description"].sub(
            lambda x: parse_description(x, footnotes),
            html,
        )
        i += 1

    if len(footnotes) == 0:
        return html

    fn_re = FOOTNOTES_RE[i - 1]
    html = fn_re["reference"].sub(
        lambda x: form_footnote(x, footnotes),
        html,
    )

    return form_lost_footnotes(html, fn_re, footnotes)
