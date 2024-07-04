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
    Count,
    DelimitedText,
    FieldBase,
    Flag,
    JsonLineReader,
    MarkupText,
    MissingField,
    ModelBase,
    Text,
    fieldfilter,
)

if typing.TYPE_CHECKING:
    from typing import Any, Iterable, Mapping
    import collections


__version__ = "3.1.4"


CARDS_URL = "https://thronesdb.com/api/public/cards/"
CARDS_ENV = "THRONESCLI_DATA"


class ThronesReader(JsonLineReader):
    def __init__(self, options: dict):
        if options["update"]:
            self.update_cards()
            click.echo("Card database updated. Thank you thronesdb.com!")
            raise SystemExit(0)

    @property
    def filenames(self):
        cards_file = self.get_cards_file()
        if not os.path.exists(cards_file):
            self.update_cards()
        yield cards_file

    @classmethod
    def get_cards_file(cls):
        """Return the path of the card database file."""
        if CARDS_ENV in os.environ:
            return os.environ[CARDS_ENV]
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
                    # Detect X values
                    xvalues = [
                        ("cost", {"Character", "Attachment", "Location", "Event"}),
                        ("strength", {"Character"}),
                        ("claim", {"Plot"}),
                        ("reserve", {"Plot"}),
                        ("initiative", {"Plot"}),
                        ("income", {"Plot"}),
                    ]
                    for fieldname, typenames in xvalues:
                        if (
                            item[fieldname] is None
                            and "X" in item["text"]
                            and item["type_name"] in typenames
                        ):
                            item[fieldname] = "X"
                    # Write item one per line
                    out.write(json.dumps(item))
                    out.write("\n")
            os.remove(input_file)
            with contextlib.suppress(FileNotFoundError):
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
        """
        Yield all keywords listed in `value`. If `short` is true,
        any additional keyword parameters is excluded.
        """
        for part in value.split("."):
            part = part.strip()
            for keyword in self.KEYWORDS:
                if part.startswith(keyword):
                    yield keyword if short else part
                    break

    def fetch(self, item: Mapping, default: Any | type = MissingField) -> Any:
        """
        Return a list of all keywords defined by `item`. Raise a
        `MissingField` exception if there are no keywords.
        """
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


class ChallengeIcons(FieldBase):
    name = "ICON"

    icons = {
        "military": click.style("M", fg="red"),
        "intrigue": click.style("I", fg="green"),
        "power": click.style("P", fg="blue"),
    }
    iconkeys = {icon: f"is_{icon}" for icon in icons}

    def fetch(
        self, item: Mapping, default: Any | type = MissingField
    ) -> dict[str, bool]:
        """Returns all icon values in `item` as a dict."""
        if item["type_name"] != "Character":
            raise MissingField("Not a character")
        return {icon: bool(item.get(key)) for icon, key in self.iconkeys.items()}

    def convert(
        self, optarg: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> list[str]:
        """
        Converts the option argument `optarg` to a list of matching icons. If
        no choice matches, then print an error message and exit.
        """
        optarg = optarg.lower()
        if all(c in "mip" for c in optarg):
            optarg = [c for c in optarg]
        else:
            optarg = [optarg]
        icons = []
        for arg in optarg:
            for icon in self.icons:
                if icon.startswith(arg):
                    icons.append(icon)
                    break
            else:
                self.fail(
                    (
                        f"Valid choices are: {', '.join(self.icons)}. A combination of "
                        "the letters 'MIP' can be used to define multiple respective icons."
                    ),
                    param=param,
                    ctx=ctx,
                )
        return icons

    @fieldfilter("--icon")
    def filter_icon(self, arg: list[str], value: dict, options: dict) -> bool:
        """Filter on having given icon."""
        return all(value[icon] for icon in arg)

    @fieldfilter("--icon-isnt")
    def filter_icon_isnt(self, arg: list[str], value: dict, options: dict) -> bool:
        """Filter on not having given icon."""
        return all(not value[icon] for icon in arg)

    def format_value(self, value: dict) -> str:
        """Return a string representation of `value`."""
        return (
            " ".join(self.icons[icon] for icon, state in value.items() if state)
            or "No Icons"
        )

    def count(self, item: Mapping, counts: collections.Counter):
        """Increments the `counts` of each individual icon."""
        try:
            for icon, value in self.fetch(item).items():
                counts[icon.title()] += value
        except MissingField:
            pass

    def get_metavar_help(self):
        """
        Return a longer description of the option argument for this field used
        in `--help`.
        """
        return (
            f"One of: {', '.join(self.icons)}. A combination of the letters "
            "'MIP' can be used to define multiple respective icons."
        )


class Loyal(Flag):
    """
    Field class for card loyalty. Non-Loyal is by default not shown in brief
    format.

    Examples:

        >>> ThronesModel.cli('--trait Recruit', reader=ThronesReader)
        Arry: Unique. Loyal. The Night's Watch. Character. 4 Cost. 3 STR. M I.
        Recruit from the Dungeons: The Night's Watch. Character. 3 Cost. 2 STR. No Icons.
        Highborn Recruit: The Night's Watch. Character. 1 Cost. 1 STR. P.
        <BLANKLINE>
        Total count: 3

        >>> ThronesModel.cli('--trait Recruit --show loyal', reader=ThronesReader)
        Arry: Loyal.
        Recruit from the Dungeons: Non-Loyal.
        Highborn Recruit: Non-Loyal.
        <BLANKLINE>
        Total count: 3
    """

    def fetch(self, item: Mapping, default: Any | type = MissingField) -> Any:
        if item["faction_code"] == "neutral":
            raise MissingField("Irrelevant for neutral")
        return super().fetch(item, default)

    def format_brief(self, value: Any, show: bool = False) -> str:
        return super().format_brief(value, show=show) if value or show else ""


class Unique(Flag):
    """
    Field class for card uniqueness. Non-Unique is by default not shown in
    brief format.

    Examples:

        >>> ThronesModel.cli('--trait Recruit', reader=ThronesReader)
        Arry: Unique. Loyal. The Night's Watch. Character. 4 Cost. 3 STR. M I.
        Recruit from the Dungeons: The Night's Watch. Character. 3 Cost. 2 STR. No Icons.
        Highborn Recruit: The Night's Watch. Character. 1 Cost. 1 STR. P.
        <BLANKLINE>
        Total count: 3

        >>> ThronesModel.cli('--trait Recruit --show unique', reader=ThronesReader)
        Arry: Unique.
        Recruit from the Dungeons: Non-Unique.
        Highborn Recruit: Non-Unique.
        <BLANKLINE>
        Total count: 3
    """

    def fetch(self, item: Mapping, default: Any | type = MissingField) -> Any:
        if item["type_name"] not in {"Character", "Location", "Attachment"}:
            raise MissingField("Irrelevant for type")
        return super().fetch(item, default)

    def format_brief(self, value: Any, show: bool = False) -> str:
        return super().format_brief(value, show=show) if value or show else ""


class Cost(Count):
    def is_missing(self, value: Any) -> bool:
        """Don't report `None` as a missing value."""
        return False

    def fetch(self, item: Mapping, default: Any | type = MissingField) -> Any:
        """Report as missing based on card type."""
        if item["type_name"] not in {"Character", "Location", "Event", "Attachment"}:
            raise MissingField("Irrelevant for card type")
        return super().fetch(item, default=default)

    def sortkey(self, item: Mapping) -> Any:
        """
        Returns a comparable-type version of this field's value in `item`, used
        for sorting. For `Number` objects this is guaranteed to be an `int`
        or `float`.
        """
        try:
            value = self.fetch(item)
        except MissingField:
            return -3
        if value is None:
            return -2
        if value == "X":
            return -1
        return value


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
    unique = Unique(keyname="is_unique")
    loyal = Loyal(keyname="is_loyal")
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
        autofilter=True,
        inclusive=True,
    )
    type_name = Choice(
        ["Agenda", "Attachment", "Character", "Event", "Location", "Plot", "Title"],
        realname="Type",
        optalias="-t",
        inclusive=True,
    )
    cost = Cost(specials=["X"], autofilter=True)

    # Characters
    strength = Count(specials=["X"], realname="STR", autofilter=True)
    icons = ChallengeIcons(autofilter=True)

    # Plots
    claim = Count(specials=["X"], autofilter=True)
    income = Count(specials=["X"], autofilter=True)
    initiative = Count(specials=["X"], autofilter=True)
    reserve = Count(specials=["X"], autofilter=True)

    # Non-default fields
    illustrator = Text(inclusive=True, verbosity=2)
    pack_name = Text(realname="Set", inclusive=True, verbosity=2)


def main():
    ThronesModel.cli(reader=ThronesReader)


if __name__ == "__main__":
    main()
