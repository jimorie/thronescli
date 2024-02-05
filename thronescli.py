#!/usr/bin/env python

from __future__ import annotations

import contextlib
import json
import os
import os.path
import typing
import urllib.request

import click
from clicksearch import (
    Choice,
    DelimitedText,
    Flag,
    JsonLineReader,
    MarkupText,
    MissingField,
    ModelBase,
    Number,
    Text,
)

if typing.TYPE_CHECKING:
    from typing import Iterable


__version__ = "3.0.0"


CARDS_URL = "https://thronesdb.com/api/public/cards/"


class ThronesReader(JsonLineReader):
    def __init__(self, options: dict):
        if options["update"]:
            self.update_cards()
            click.echo("Card database updated. Thank you thronesdb.com!")
        self.filenames = [self.get_cards_file()]

    @classmethod
    def get_cards_file(cls):
        """Return the path of the card database file."""
        with contextlib.suppress(OSError):
            os.mkdir(click.get_app_dir("thronescli"))
        return os.path.join(click.get_app_dir("thronescli"), "cards-v3.json")

    @classmethod
    def update_cards(cls):
        """Fetch a new card database and write it to file."""
        try:
            cards_file = cls.get_cards_file()
            input_file = cards_file + ".input"
            output_file = cards_file + ".output"
            urllib.request.urlretrieve(CARDS_URL, input_file)
            with open(input_file) as inp, open(output_file, "w") as out:
                for item in json.load(inp):
                    out.write(json.dumps(item))
                    out.write("\n")
            os.remove(input_file)
            os.remove(cards_file)
            os.rename(output_file, cards_file)
        except Exception as exc:
            msg = f"Failed to update card database: {exc}"
            raise click.ClickException(msg) from exc

    @classmethod
    def make_params(cls) -> Iterable[click.Parameter]:
        """Yields all options offered by the reader."""
        yield click.Option(["--update"], is_flag=True, help="Update card database")


class Keyword(MarkupText, DelimitedText):
    KEYWORDS = [
        "Ambush",
        "Assault",
        "Bestow",
        "Insight",
        "Intimidate",
        "Limited",
        "No attachments",
        "Pillage",
        "Renown",
        "Shadow",
        "Stealth",
        "Terminal",
    ]

    def parse_keywords(self, value: str, short: bool = False) -> Iterable[str]:
        while True:
            for keyword in self.KEYWORDS:
                if value.startswith(keyword):
                    fullkeyword, value = value.split(".", 1)
                    value = value.lstrip()
                    yield keyword if short else fullkeyword
                    break
            else:
                break

    def fetch(self, item: Mapping, default: Any | type = MissingField) -> Any:
        keywords = list(
            self.parse_keywords(super(Keyword, self).fetch(item, default=default))
        )
        if len(keywords) == 0:
            raise MissingField("No keywords")
        return keywords

    def parts(self, value: Any) -> Iterable[str]:
        """Parts have already been split."""
        return value

    def format_value(self, value: Any) -> str | None:
        """Return a string representation of `value`."""
        if value:
            return (
                ". ".join(
                    super(Keyword, self).format_value(keyword) for keyword in value
                )
                + "."
            )
        return None

    def count(self, item: Mapping, counts: collections.Counter):
        """
        Increments the count of each part in the `DelimitedText`
        individually.
        """
        try:
            for keyword in self.parse_keywords(super(Keyword, self).fetch(item), True):
                counts[keyword] += 1
        except MissingField:
            pass

    @classmethod
    def strip_value(cls, value: Any) -> Any:
        """Return a version of `value` without HTML tags."""
        return [MarkupText.strip_value(keyword) for keyword in value]


class ThronesModel(ModelBase):
    __version__ = __version__

    # Basic card properties
    name = Text(optalias="-n", redirect_args=True)
    traits = DelimitedText(
        optname="trait",
        delimiter=".",
        verbosity=1,
        unlabeled=True,
        styles={"fg": "magenta"},
    )
    text = MarkupText(
        optalias="-x", verbosity=1, unlabeled=True, styles={"fg": "white"}
    )
    keywords = Keyword(keyname="text", optname="keyword", verbosity=None)
    faction = Choice(
        {
            "Baratheon": "House Baratheon",
            "Greyjoy": "House Greyjoy",
            "GJ": "House Greyjoy",
            "Lannister": "House Lannister",
            "Martell": "House Martell",
            "Neutral": "Neutral",
            "Stark": "House Stark",
            "Targaryen": "House Targaryen",
            "Night's Watch": "The Night's Watch",
            "The Night's Watch": "The Night's Watch",
            "NW": "The Night's Watch",
            "Tyrell": "House Tyrell",
        },
        keyname="faction_name",
        optalias="-f",
    )
    type_name = Choice(
        ["Agenda", "Attachment", "Character", "Event", "Location", "Plot", "Title"],
        realname="Type",
        optalias="-t",
    )
    loyal = Flag(keyname="is_loyal")
    unique = Flag(keyname="is_unique")
    cost = Number(inclusive=True)

    # Characters
    strength = Number(realname="STR", implied="--type character")

    # Plots
    claim = Number(implied="--type plot", inclusive=True)
    income = Number(implied="--type plot", inclusive=True)
    initiative = Number(implied="--type plot", inclusive=True)
    reserve = Number(implied="--type plot", inclusive=True)

    # Non-default fields
    illustrator = Text(inclusive=True, verbosity=2)
    pack_name = Text(realname="Set", inclusive=True, verbosity=2)


def main():
    ThronesModel.cli(reader=ThronesReader)


if __name__ == "__main__":
    main()
