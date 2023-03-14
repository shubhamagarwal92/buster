from abc import ABC, abstractmethod
import argparse
from dataclasses import dataclass
from typing import Type
import urllib.parse

from bs4 import BeautifulSoup


from buster.documents.sqlite.populate import File, PopulateDB
from buster.documents.sqlite.schema import open_db


@dataclass
class Parser(ABC):
    url_base: str | None = None
    file_base: str | None = None

    def get_url(self, name: str) -> str:
        """Get the URL for a file."""
        if self.file_base:
            if name.index(self.file_base) != 0:
                raise ValueError("Expected to have prefix '{self.file_Base}' at the start of filename '{name}'")

            name = name[len(self.file_base) :]

        if self.url_base:
            url = urllib.parse.urljoin(self.url_base, name)
        else:
            url = name
        return url

    @abstractmethod
    def __call__(self, soup: BeautifulSoup, url: str) -> File:
        ...


def main(parse_cls: Type[Parser]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--url_base", type=str)
    parser.add_argument("--file_base", type=str)
    parser.add_argument("name", type=str)
    parser.add_argument("dest", type=str)
    parser.add_argument("sources", type=argparse.FileType("r"), nargs="+")
    args = parser.parse_args()

    file_parser = parse_cls(args.url_base, args.file_base)

    files = (
        file_parser(BeautifulSoup(source, features="lxml"), file_parser.get_url(source.name)) for source in args.sources
    )
    with open_db(args.dest) as connection:
        db = PopulateDB(connection)
        source = db.get_source(args.name)
        if source is None:
            source = db.create_source(args.name)
        source.new_version(files)

    return
