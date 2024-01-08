import re
import sys
from pathlib import Path

sys.path.append("scripts/")

from lib.config import Config

conf = Config()
CFG_FILE = Path(conf.get("FOP_CONF"))
FONTS_DIR = Path(conf.get("FONTS_DIR"))

TEMPLATE_CFG = {
    "base": """<?xml version="1.0"?>
<fop version="1.0">
    <complex-scripts disabled="true"/>
    <font-base>../</font-base>
    <renderers>
        <renderer mime="application/pdf">
            <fonts>
{fonts}
            </fonts>
        </renderer>
    </renderers>
</fop>
""",
    "font": """{0:<16}<font embed-url="{path}">\n{triplets}{0:<16}</font>\n""",
    "triplet": """{0:<20}<font-triplet name="{name}" \
style="{style}" weight="{weight}"/>\n""",
}

# tutorial
# https://xmlgraphics.apache.org/fop/2.6/fonts.html

FONTS_INFO = [
    {
        "family_name": ["Times", "Times Roman", "Times-Roman", "serif", "any"],
        "file_pref": "CharisSIL",
    },
    {
        "family_name": ["Helvetica", "sans-serif", "SansSerif"],
        "file_pref": "PTSans",
    },
    {
        "family_name": ["Courier", "monospace", "Monospaced"],
        "file_pref": "CourierPrime",
    },
    {
        "family_name": ["Symbol", "ZapfDingbats"],
        "file_pref": "NotoSansSymbols2",
    },
    {
        "family_name": ["Symbol"],
        "file_pref": "NotoSansMath",
    },
]

FONT_STYLE_MATCHING = {
    "Regular": ["normal", "normal"],
    "Bold": ["normal", "bold"],
    "Italic": ["italic", "normal"],
    "BoldItalic": ["italic", "bold"],
}
FONT_STYLE_RE = re.compile(f'-({"|".join(FONT_STYLE_MATCHING.keys())})\\.')


def collect(font_info: str) -> str:
    fonts = ""
    for f in FONTS_DIR.rglob(f'{font_info["file_pref"]}-*'):
        style_key = FONT_STYLE_RE.search(f.name)

        if not style_key:
            continue

        triplets = ""
        for name in font_info["family_name"]:
            style = FONT_STYLE_MATCHING[style_key[1]]
            triplets += TEMPLATE_CFG["triplet"].format(
                "",
                name=name,
                style=style[0],
                weight=style[1],
            )

        fonts += TEMPLATE_CFG["font"].format(
            "",
            path=str(f),
            triplets=triplets,
        )

    return fonts


def main() -> None:
    fonts = ""
    for font in FONTS_INFO:
        fonts += collect(font)

    CFG_FILE.write_text(TEMPLATE_CFG["base"].format(fonts=fonts))


if __name__ == "__main__":
    main()
