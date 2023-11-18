import re
import urllib.parse as url_parser
from re import Pattern

FOR_REMOVING = [
    "</?html>",
    "<head>.*</head>",
    "</?body>",
    '<a id="more"></a>',
    r"<p>&nbsp\s*?</p>",
    '</h6><h6>(?=<a href="https://nickbostrom.com/ethics/)',
    "<h6></h6>",
    "<p>&lt;/rant&gt;</p>",
    r"-(?=\.html)",
    # no destination
    '<a href="#fn2x25"><sup>2</sup></a>',
    # copy of previous footnote
    '<p><sup>4</sup><a href="#cite.0.Tversky.1983"> Ibid.</a></p>',
]

FOR_REPLACING = [
    ["https://www.<em>lessw</em>", "https://www.lessw"],
    ["<p>1. Edwin T. Jaynes, <em><a href", "<h6>1. Edwin T. Jaynes, <em><a href"],
    [
        "Cambridge University Press, 2003).</p>",
        "Cambridge University Press, 2003).</h6>",
    ],
    ['<p class="Reference">', "<p>"],
    [
        '<a href="#cite.0.Tversky.1983"> “Extensional Versus Intuitive Reasoning.”</a>',
        " (1983). “Extensional Versus Intuitive Reasoning.”",
    ],
    ['<a href="#fn4x7"><sup>4</sup></a>', "<sup>3</sup>"],  # copy of previous footnote
    [
        '<a href="#cite.0.Buehler.2002"> “Inside the Planning Fallacy.”</a>',
        " (2002). “Inside the Planning Fallacy.”",
    ],
    [chr(0x2715), chr(0x00D7)],
]

SUPERSCRIPT_DIGITS = [0x2070, 0xB9, 0xB2, 0xB3, *list(range(0x2074, 0x207A))]  # 0-9
SUPERSCRIPT_RE = re.compile(
    f"""[{"".join(chr(x) for x in SUPERSCRIPT_DIGITS)}]+?""",
)
SUPERSCRIPT_DICT = {d: ord(str(i)) for i, d in enumerate(SUPERSCRIPT_DIGITS)}

POTENTIAL_FOOTNOTES_RE = [
    re.compile(fn_re, re.MULTILINE | re.DOTALL)
    for fn_re in (
        r"""<hr class="dividerBlock"><p>(\d+\.\s+?.+?)</p>$""",  # Mere Reality
        r"""^(\d+?)\.""",  # Mere Reality
        r"""^<p>Yesterday, I""",  # The Machine in the Ghost
        r"""<p>\d+\s+?.+?</p>""",  # The Machine in the Ghost
    )
]


def remove_tags(html: str) -> str:
    for regex in FOR_REMOVING:
        html = re.sub(regex, "", html)

    return html


def replace_blocks(html: str) -> str:
    for r in FOR_REPLACING:
        html = html.replace(*r)

    return html


def rel_to_abs_url(link: str, base_url: str, rel: str) -> str:
    abs_url = url_parser.urljoin(base_url, rel)
    return link.replace(rel, abs_url)


def abs_urls(html: str, html_url: str) -> str:
    return re.sub(
        r"""(href|src)=["']([^#][^'"]+?)['"]""",
        lambda x: rel_to_abs_url(x[0], html_url, x[2]),
        html,
    )


def url_escape(m: re.Match) -> str:
    return re.sub(r"&(?=[\w\d]+?=)", "&amp;", m[0])


def xml_urls(html: str) -> str:
    return re.sub(r"""<a.+?href=["'][^'"]+?['"]""", url_escape, html)


def anchors(html: str) -> str:
    return re.sub(
        r"""<a.+?(id=["'][^'"]+?['"]).*?>""",
        lambda x: f"{x[0]}<span {x[1]}/>",
        html,
    )


def translate_symbols(html: str) -> str:
    return SUPERSCRIPT_RE.sub(
        lambda x: f"""<sup>{x[0].translate(SUPERSCRIPT_DICT)}</sup>""",
        html,
    )


def flag_potential_footnotes(
    html: str,
    fn_re: Pattern[str] = POTENTIAL_FOOTNOTES_RE,
) -> str:
    if m := fn_re[0].search(html):
        fn_set = []
        for fn_orig in m[1].split("<br>"):
            fn = fn_re[1].sub(lambda x: f"[{x[1]}]", fn_orig)
            fn_set.append(f"<p>{fn}</p>")

        html = fn_re[0].sub("".join(fn_set), html)

    if fn_re[2].search(html):
        html = fn_re[3].sub(lambda x: x[0].replace("<p>", '<p class="mjx-desc">'), html)

    return html


def normalize(html: str, url: str) -> str:
    html = remove_tags(html)
    html = replace_blocks(html)

    html = abs_urls(html, url)
    html = xml_urls(html)
    html = flag_potential_footnotes(html)
    return translate_symbols(html)
