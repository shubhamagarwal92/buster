"""Populate the db with a new parse."""


from dataclasses import dataclass
import sqlite3
from typing import NamedTuple, Union

from pyparsing import Iterable


@dataclass
class Block:
    block_type: str
    content: str


@dataclass
class Section:
    title: str
    href: str
    children: list[Union["Section", Block]]


@dataclass
class File:
    title: str
    url: str
    sections: list[Section]


class ParseKey(NamedTuple):
    source_id: int
    version_id: int


@dataclass
class Source:
    source_id: int
    connection: sqlite3.Connection

    def update_note(self, note: str):
        """Update the source's note field."""
        self.connection.execute("UPDATE sources (note) VALUES (?) WHERE id = ?", (note, self.source_id))
        return

    def get_current_version(self) -> int | None:
        """Get the current version of a source."""
        cur = self.connection.execute("SELECT version FROM latest_version WHERE source = ?", (self.source_id,))
        row = cur.fetchone()
        if row is None:
            return None
        (vid,) = row
        return vid

    def new_version(self, files: Iterable[File]):
        """Create a new version for a source."""
        vid = self.get_current_version()
        if vid is None:
            vid = 0
        else:
            vid = vid + 1
        cur = self.connection.execute("INSERT INTO versions (source, version) VALUES (?, ?)", (self.source_id, vid))
        key = ParseKey(self.source_id, vid)
        next_section_id = 0
        for file_ in files:
            next_section_id = self.insert_file(next_section_id, file_, key)

    def insert_file(self, section_id: int, item: File, key: ParseKey) -> int:
        """Add a file to a source and return the next section id."""
        self.connection.execute(
            "INSERT INTO sections (source, version, section, title, url) VALUES (?, ?, ?, ?, ?)",
            (key.source_id, key.version_id, section_id, item.title, item.url),
        )
        next_section_id = section_id + 1
        for order, section in enumerate(item.sections):
            next_section_id = self.insert_section(next_section_id, section_id, item.url, order, section, key)
        return next_section_id

    def insert_section(
        self, section_id: int, parent: int, url: str, order: int, section: Section, key: ParseKey, depth: int = 0
    ) -> int:
        """Add a section to a file, and return the next section id."""
        self.connection.execute(
            "INSERT INTO sections (source, version, section, title, url) VALUES (?, ?, ?, ?, ?)",
            (key.source_id, key.version_id, section_id, section.title, url + section.href),
        )
        self.connection.execute(
            "INSERT INTO structure (source, version, parent, section, sequence, depth) VALUES (?, ?, ?, ?, ?, ?)",
            (key.source_id, key.version_id, parent, section_id, order, depth),
        )
        next_section_id = section_id + 1
        for order, child in enumerate(section.children):
            if isinstance(child, Section):
                next_section_id = self.insert_section(next_section_id, section_id, url, order, child, key, depth + 1)
            elif isinstance(child, Block):
                self.connection.execute(
                    "INSERT INTO blocks (source, version, section, sequence, type, content) VALUES (?, ?, ?, ?, ?, ?)",
                    (key.source_id, key.version_id, section_id, order, child.block_type, child.content),
                )
        return next_section_id


@dataclass
class PopulateDB:
    connection: sqlite3.Connection

    def get_source(self, source: str) -> Source | None:
        """Get a source from the db, of None if it does not exists."""
        cur = self.connection.execute("SELECT id FROM sources WHERE name = ?", (source,))
        row = cur.fetchone()
        if row is None:
            return None
        (sid,) = row
        return Source(sid, self.connection)

    def create_source(self, source: str, note: str = None) -> Source:
        """Add a new source to the db."""
        cur = self.connection.execute("INSERT INTO sources (name, note) VALUES (?, ?)", (source, note))
        cur = self.connection.execute("SELECT id FROM sources WHERE name = ?", (source,))
        row = cur.fetchone()
        (sid,) = row
        return Source(sid, self.connection)
