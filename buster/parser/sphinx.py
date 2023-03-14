import re
from bs4 import BeautifulSoup, NavigableString
from buster.documents.sqlite.populate import Block, File, Section
from buster.parser.base import Parser, main


class SphinxParser(Parser):
    """Parse Sphinx formated documentation trees."""

    def __call__(self, soup: BeautifulSoup, url: str) -> File:
        title = soup.find("title").get_text()
        document = soup.find("div", {"itemprop": "articleBody"})
        sections = [self.parse_section(section) for section in document.find_all("section", recursive=False)]
        return File(title, url, sections)

    def parse_section(self, section: BeautifulSoup) -> Section:
        title, href = self.parse_header(section.find(re.compile("^h[0-9]$")))

        children = []
        for child in section.children:
            if child.name is not None and re.match("^h[0-9]$", child.name):
                continue
            elif child.name == "span":
                continue
            elif child.name in {"p", "div"}:
                children.append(Block("p", child.get_text()))
            elif child.name == "section":
                children.append(self.parse_section(child))
            elif child.name in {"table", "dl", "ul", "ol"}:
                children.append(Block(child.name, str(child)))
            elif child.name == "blockquote":
                children.append(Block("code", str(child)))
            elif isinstance(child, NavigableString):
                assert not child.string.strip()
            elif child.name in {"hr", "img"}:
                continue
            else:
                assert False, child.name
        return Section(title, href, children)

    def parse_header(self, header):
        titles = []
        href = None
        for child in header.children:
            if isinstance(child, NavigableString):
                titles.append(child.string)
            elif child.name == "a":
                href = child.attrs["href"]
            else:
                titles.append(child.get_text())
        return "".join(titles), href


if __name__ == "__main__":
    main(SphinxParser)
