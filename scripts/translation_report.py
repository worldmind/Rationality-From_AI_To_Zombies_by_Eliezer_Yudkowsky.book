import logging as log
import os
import re
from pathlib import Path
from re import Pattern

from bigtree import Node, dict_to_tree, yield_tree
from lib.config import Config
from lxml import etree
from termcolor import colored

log.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=log.INFO)


def tree_to_str(el: Node) -> str:
    return etree.tostring(el, encoding="unicode", method="text")


def get_text(
    file: Path,
    year_re: Pattern[str] = re.compile(r"\D?(18|19|20)\d{2}\D?"),
    url_re: Pattern[str] = re.compile(r"https?://\S+"),
) -> str:
    root = etree.parse(str(file)).getroot()

    # title
    content = root.findtext("{*}info/{*}title")

    # description
    desc = root.find("{*}info/{*}abstract")
    if desc is not None:
        content += tree_to_str(desc)

    # remove elements that don't need to be translated
    for el_name in [
        "info",
        "bibliography",
        "indexterm",
        "informalfigure",
        "footnoteref",
        "inlinemediaobject",
        "inlineequation",
        "equation",
        "citation",
    ]:
        for el in root.findall(".//{*}" + el_name):
            el.getparent().remove(el)

    # remove footnotes containing books rather than notes
    for el in root.findall(".//{*}footnote"):
        txt = tree_to_str(el)

        if year_re.search(txt):
            el.getparent().remove(el)

    # body
    content += tree_to_str(root)

    return url_re.sub("", content)


def count_chars(
    txt: str,
    cyrillic_re: Pattern[str] = re.compile(r"[а-яА-ЯЁё]+"),
    latin_re: Pattern[str] = re.compile(r"[a-zA-Z]+"),
) -> dict:
    cnt_ru = len("".join(cyrillic_re.findall(txt)))
    cnt_en = len("".join(latin_re.findall(txt)))

    return {"ru": cnt_ru, "en": cnt_en}


def print_report_line(
    line: str,
    translated: float,
    terminal_width: int = os.get_terminal_size().columns,
    almost_done: float = 0.9,
) -> None:
    if translated is None:
        print(line)
        return

    # translated
    suffix = f"ru={translated * 100:.2f}% "

    # language
    if translated >= almost_done:
        suffix += colored("RU", "green", attrs=["bold"])
    else:
        suffix += colored("EN", "red", attrs=["bold"])

    # align right
    num_spaces = terminal_width - len(line) - len(suffix)
    num_spaces = max(1, num_spaces)

    line = line + " " * num_spaces + suffix

    print(line)


def print_report(report: dict) -> None:
    ftree_style = {
        "style": "custom",
        "custom_style": ("│     ", "├── ¤ ", "└── ¤ "),
    }
    all_ru = 0
    all_en = 0

    ftree = dict_to_tree(report)

    for branch, stem, node in yield_tree(ftree, **ftree_style):
        translated = None

        if node.is_leaf:
            if (node.ru + node.en) == 0:
                translated = 1
            else:
                all_ru += node.ru
                all_en += node.en
                translated = node.ru / (node.ru + node.en)

        print_report_line(f"{branch}{stem}{node.node_name}", translated)

    total_translated = all_ru / (all_ru + all_en)

    print()
    print_report_line("Total:", total_translated)


def main() -> None:
    conf = Config()
    book_path = Path(conf.get("BOOK_DIR"))
    book_ext = conf.get("BOOK_EXT")
    report = {}

    for file in sorted(book_path.glob(f"**/*{book_ext}")):
        log.debug("Process file: %s", file)

        txt = get_text(file)
        report[str(file)] = count_chars(txt)

    print_report(report)

    log.debug("All done!")


if __name__ == "__main__":
    main()
