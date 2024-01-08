import urllib.parse as parser
from datetime import datetime
from pathlib import Path

from lib.htmlbook import HTMLBook

TEMPLATES = dict(
    book="""<?xml version="1.0" encoding="UTF-8"?>
<book xml:id="{ITEM_ID}"
      xmlns="http://docbook.org/ns/docbook"
      version="5.0"
      doc_status="final;draft"
      xml:lang="en"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xi="http://www.w3.org/2001/XInclude"
      xmlns:xl="http://www.w3.org/1999/xlink">
  <info>
    <title>{ITEM_TITLE}</title>
    <abstract>{ITEM_CONTENT}</abstract>
    <authorgroup>
      <author>{AUTHOR_DESC}</author>
      {COAUTHORS}
      {REVIEWERS}
    </authorgroup>
    <bibliosource class="uri">
      <link xlink:href="{ITEM_URL}"></link>
    </bibliosource>
    <pubdate>{PUBLICATION_DATE}</pubdate>
  </info>
  {INCLUDE_ITEMS}
  <index/>
</book>
""",
    person="""<personname>
<firstname>{PERSON_NAME}</firstname><surname>{PERSON_SURNAME}</surname>
</personname>
""",
    coauthor='<othercredit role="coauthor">{COAUTHOR_DESC}</othercredit>',
    reviewer='<othercredit role="reviewer" doc_status="draft">{REVIEWER_DESC}</othercredit>',
    incl_item='<xi:include href="{ITEM_PATH}"/>',
    chapter="""<chapter xml:id="{ITEM_ID}"
      xmlns="http://docbook.org/ns/docbook"
      version="5.0"
      xml:lang="en"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xi="http://www.w3.org/2001/XInclude"
      xmlns:xl="http://www.w3.org/1999/xlink">
  <info>
    <title>{ITEM_TITLE}</title>
    <bibliosource class="uri">
      <link xlink:href="{ITEM_URL}"></link>
    </bibliosource>
    <pubdate doc_status="draft">{PUBLICATION_DATE}</pubdate>
  </info>
  {ITEM_TAG_LIST}
  {ITEM_CONTENT}
  {INCLUDE_ITEMS}
</chapter>
""",
    section="""<section xml:id="{ITEM_ID}"
      xmlns="http://docbook.org/ns/docbook"
      version="5.0"
      xml:lang="en"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xi="http://www.w3.org/2001/XInclude"
      xmlns:xl="http://www.w3.org/1999/xlink">
  <info>
    <title>{ITEM_TITLE}</title>
    <bibliosource class="uri">
      <link xlink:href="{ITEM_URL}"></link>
    </bibliosource>
    <pubdate doc_status="draft">{PUBLICATION_DATE}</pubdate>
  </info>
  {ITEM_TAG_LIST}
  {ITEM_CONTENT}
  {INCLUDE_ITEMS}
</section>
""",
    item_tag="<indexterm><primary>{TAG_NAME}</primary></indexterm>",
)


def level_to_part_type(level: int) -> str:
    part_types = ["book", "chapter", "section"]

    return part_types[level] if level < len(part_types) else part_types[-1]


def get_date(iso_dt: str) -> str:
    if iso_dt is None:
        return ""

    iso_dt = iso_dt.replace("Z", "+00:00")
    date = datetime.fromisoformat(iso_dt)
    return date.astimezone().strftime("%Y-%m-%d")


def get_person(full_name: str) -> list:
    person = full_name.split()

    if len(person) == 1:
        person.append("")

    return TEMPLATES["person"].format(
        PERSON_NAME=person[0],
        PERSON_SURNAME=person[1],
    )


def path_escape(text: str) -> str:
    return parser.quote(text)


def xml_escape(text: str) -> str:
    return text.replace("&", "&amp;")


def wrap_book(item: HTMLBook, xml_content: str, child_items: list[Path]) -> str:
    data = dict(
        ITEM_ID=item.xml_id,
        ITEM_TITLE=xml_escape(item.title),
        ITEM_URL=item.url,
        PUBLICATION_DATE=get_date(item.modified_at),
        AUTHOR_DESC=get_person(item.author),
        ITEM_CONTENT=xml_content,
    )

    coauthors = [TEMPLATES["coauthor"].format(COAUTHOR_DESC=get_person(a)) for a in item.coauthors]
    data["COAUTHORS"] = "\n".join(coauthors)

    reviewers = [TEMPLATES["reviewer"].format(REVIEWER_DESC=get_person(r)) for r in item.reviewers]
    data["REVIEWERS"] = "\n".join(reviewers)

    child_items_xml = [TEMPLATES["incl_item"].format(ITEM_PATH=path_escape(str(child_p))) for child_p in child_items]
    data["INCLUDE_ITEMS"] = "\n".join(child_items_xml)

    return TEMPLATES["book"].format(**data)


def wrap_part(
    part_type: str,
    item: HTMLBook,
    xml_content: str,
    child_items: list,
) -> str:
    data = dict(
        ITEM_ID=item.xml_id,
        ITEM_TITLE=xml_escape(item.title),
        ITEM_URL=item.url,
        PUBLICATION_DATE=get_date(item.modified_at),
        ITEM_CONTENT=xml_content,
    )

    child_items_xml = [TEMPLATES["incl_item"].format(ITEM_PATH=path_escape(str(child_p))) for child_p in child_items]
    data["INCLUDE_ITEMS"] = "\n".join(child_items_xml)

    tags_xml = [TEMPLATES["item_tag"].format(TAG_NAME=xml_escape(tag)) for tag in item.tags]
    data["ITEM_TAG_LIST"] = "\n".join(tags_xml)

    return TEMPLATES[part_type].format(**data)


def wrap(level: int, item: HTMLBook, xml_content: str, child_items: list[Path]) -> str:
    part_type = level_to_part_type(level)

    return (
        wrap_book(item, xml_content, child_items)
        if part_type == "book"
        else wrap_part(part_type, item, xml_content, child_items)
    )
