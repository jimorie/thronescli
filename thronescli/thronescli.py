#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from json import load
from operator import itemgetter
from os import mkdir, remove
from os.path import join, isfile
from re import compile as re_compile, IGNORECASE
from sys import argv

# Try import py3 libs first, fall back to py2
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

from click import (
    ClickException,
    argument,
    command,
    echo,
    get_app_dir,
    option,
    pass_context,
    secho,
    style
)


__version__ = "1.2.4"


CARDS_URL = "http://thronesdb.com/api/public/cards/"
CARD_TYPES = [
    "agenda",
    "attachment",
    "character",
    "event",
    "location",
    "plot",
    "title"
]
FACTIONS = {
    "baratheon": {},
    "greyjoy": {
        "alias": ["gj"]
    },
    "lannister": {},
    "martell": {},
    "neutral": {
        "name": "Neutral"
    },
    "stark": {},
    "targaryen": {},
    "thenightswatch": {
        "alias": ["nw", "night's watch", "the night's watch"],
        "name": "The Night's Watch"
    },
    "tyrell": {}
}
FACTION_ALIASES = {
    alias: faction
    for faction, data in FACTIONS.items()
    for alias in data.get("alias", []) + [faction]
}
ICONS = [
    "military",
    "intrigue",
    "power"
]
SORT_KEYS = [
    "cost",
    "claim",
    "faction",
    "income",
    "illustrator",
    "initiative",
    "name",
    "reserve",
    "set",
    "str",
    "traits",
    "type"
]
COUNT_KEYS = [
    "cost",
    "claim",
    "faction",
    "icon",
    "illustrator",
    "income",
    "initiative",
    "loyal",
    "name",
    "reserve",
    "set",
    "str",
    "trait",
    "type",
    "unique"
]
DB_KEY_MAPPING = {
    "faction": "faction_code",
    "set"    : "pack_name",
    "str"    : "strength",
    "type"   : "type_code"
}
DRAFT_PACKS = [
    "VDS"
]
TEST_FALSE = [
    "include_draft"
]
TAG_PATTERN = re_compile("<.*?>")


@command()
@argument(
    "search",
    nargs=-1
)
@option(
    "--brief",
    is_flag=True,
    default=False,
    help="Show brief card data."
)
@option(
    "--case",
    is_flag=True,
    default=False,
    help="Use case sensitive matching."
)
@option(
    "--claim",
    type=int,
    multiple=True,
    help="Find cards with given claim (inclusive)."
)
@option(
    "--claim-gt",
    type=int,
    help="Find cards with greater than given claim."
)
@option(
    "--claim-lt",
    type=int,
    help="Find cards with lower than given claim."
)
@option(
    "--cost",
    type=int,
    multiple=True,
    help="Find cards with given cost (inclusive)."
)
@option(
    "--cost-gt",
    type=int,
    help="Find cards with greater than given cost."
)
@option(
    "--cost-lt",
    type=int,
    help="Find cards with lower than given cost."
)
@option(
    "--count",
    multiple=True,
    help="Show card count breakdown for given field. Possible fields are: {}.".format(", ".join(COUNT_KEYS))
)
@option(
    "--count-only",
    is_flag=True,
    default=False,
    help="Show card count breakdowns only."
)
@option(
    "--exact",
    is_flag=True,
    default=False,
    help="Use exact matching."
)
@option(
    "--faction",
    "-f",
    multiple=True,
    help="Find cards with given faction (inclusive). Possible factions are: {}.".format(
        ", ".join(sorted(FACTION_ALIASES.keys()))
    )
)
@option(
    "--faction-isnt",
    multiple=True,
    help="Find cards with other than given faction (exclusive)."
)
@option(
    "--illustrator",
    multiple=True,
    help="Find cards by the given illustrator (inclusive)."
)
@option(
    "--income",
    type=int,
    multiple=True,
    help="Find cards with given income (inclusive)."
)
@option(
    "--income-gt",
    type=int,
    help="Find cards with greater than given income."
)
@option(
    "--income-lt",
    type=int,
    help="Find cards with lower than given income."
)
@option(
    "--initiative",
    type=int,
    multiple=True,
    help="Find cards with given initiative (inclusive)."
)
@option(
    "--initiative-gt",
    type=int,
    help="Find cards with greater than given initiative."
)
@option(
    "--initiative-lt",
    type=int,
    help="Find cards with lower than given initiative."
)
@option(
    "--icon",
    multiple=True,
    help="Find cards with given icon (exclusive). Possible icons are: {}.".format(", ".join(ICONS))
)
@option(
    "--icon-isnt",
    multiple=True,
    help="Find cards without given icon (exclusive)."
)
@option(
    "--inclusive",
    is_flag=True,
    default=False,
    help="Treat multiple options of the same type as inclusive rather than exclusive. (Or-logic instead of and-logic.)"
)
@option(
    "--include-draft",
    is_flag=True,
    default=False,
    help="Include cards only legal in draft format."
)
@option(
    "--name",
    help="Find cards with matching name. (This is the default search.)"
)
@option(
    "--name-only",
    is_flag=True,
    help="Show only card names."
)
@option(
    "--loyal",
    is_flag=True,
    help="Find loyal cards."
)
@option(
    "--non-loyal",
    is_flag=True,
    help="Find non-loyal cards."
)
@option(
    "--non-unique",
    is_flag=True,
    help="Find non-unique cards."
)
@option(
    "--reserve",
    type=int,
    help="Find cards with given reserve."
)
@option(
    "--reserve-gt",
    type=int,
    help="Find cards with greater than given reserve."
)
@option(
    "--reserve-lt",
    type=int,
    help="Find cards with lower than given reserve."
)
@option(
    "--regex",
    "-r",
    is_flag=True,
    help="Use regular expression matching."
)
@option(
    "--set",
    multiple=True,
    help="Find cards from matching expansion sets (inclusive). Implies --include-draft."
)
@option(
    "--sort",
    multiple=True,
    help="Sort resulting cards by the given field. Possible fields are: {}.".format(", ".join(SORT_KEYS))
)
@option(
    "--str",
    type=int,
    help="Find cards with given strength."
)
@option(
    "--str-gt",
    type=int,
    help="Find cards with greater than given strength."
)
@option(
    "--str-lt",
    type=int,
    help="Find cards with lower than given strength."
)
@option(
    "--text",
    multiple=True,
    help="Find cards with matching text (exclusive)."
)
@option(
    "--text-isnt",
    multiple=True,
    help="Find cards without matching text (exclusive)."
)
@option(
    "--trait",
    multiple=True,
    help="Find cards with matching trait (exclusive)."
)
@option(
    "--trait-isnt",
    multiple=True,
    help="Find cards without matching trait (exclusive)."
)
@option(
    "--type",
    "-t",
    multiple=True,
    help="Find cards with matching card type (inclusive). Possible types are: {}.".format(", ".join(CARD_TYPES))
)
@option(
    "--unique",
    is_flag=True,
    help="Find unique cards."
)
@option(
    "--update",
    is_flag=True,
    default=False,
    help="Fetch new card data from thronesdb.com."
)
@option(
    "--verbose",
    "-v",
    count=True,
    help="Show verbose card data. Use twice (-vv) for all data."
)
@option(
    "--version",
    is_flag=True,
    default=False,
    help="Show the thronescli version: {}.".format(__version__)
)
@pass_context
def main (ctx, search, **options):
    """
    A command line interface for the thronesdb.com card database for A Game of Thrones LCG 2nd Ed.

    The default search argument matches cards against their name, text or traits. See below for more options.

    Options marked with inclusive or exclusive can be repeated to further include or exclude cards, respectively.

    For help and bug reports visit the project on GitHub: https://github.com/jimorie/thronescli
    """
    preprocess_options(search, options)
    if options["version"]:
        echo(__version__)
        return
    if options["update"]:
        update_cards()
        echo("Card database updated. Thank you thronesdb.com!")
        return
    if len(argv) == 1:
        echo(ctx.get_usage())
        return
    cards = load_cards(options)
    cards = filter_cards(cards, options)
    cards = sort_cards(cards, options)
    cards = list(cards)
    counts, total = count_cards(cards, options)
    if options["verbose"] == 0 and options["brief"] is False and total == 1:
        options["verbose"] = 1
    for card in cards:
        if not options["count_only"]:
            print_card(card, options)
    print_counts(counts, options, total)


def preprocess_options (search, options):
    preprocess_search(options, search)
    preprocess_regex(options)
    preprocess_case(options)
    preprocess_faction(options)
    preprocess_icon(options)
    preprocess_sort(options)
    preprocess_count(options)
    preprocess_type(options)


def preprocess_search (options, search):
    options["name"] = " ".join(search) if search else None


def preprocess_regex (options):
    flags = IGNORECASE if not options["case"] else 0
    if options["regex"]:
        if options["name"]:
            options["name"] = re_compile(options["name"], flags=flags)
        if options["trait"]:
            options["trait"] = tuple(
                re_compile(value, flags=flags) for value in options["trait"]
            )
        if options["text"]:
            options["text"] = tuple(
                re_compile(value, flags=flags) for value in options["text"]
            )
        if options["text_isnt"]:
            options["text_isnt"] = tuple(
                re_compile(value, flags=flags) for value in options["text_isnt"]
            )


def preprocess_case (options):
    if not options["case"] and not options["regex"]:
        if options["name"]:
            options["name"] = options["name"].lower()
        if options["trait"]:
            options["trait"] = tuple(value.lower() for value in options["trait"])
        if options["text"]:
            options["text"] = tuple(value.lower() for value in options["text"])
        if options["text_isnt"]:
            options["text_isnt"] = tuple(value.lower() for value in options["text_isnt"])
        if options["illustrator"]:
            options["illustrator"] = tuple(value.lower() for value in options["illustrator"])
        if options["set"]:
            options["set"] = tuple(value.lower() for value in options["set"])


def preprocess_faction (options):
    def postprocess_faction_value (value):
        return FACTION_ALIASES[value]
    aliases = FACTION_ALIASES.keys()
    preprocess_field(options, "faction", aliases, postprocess_value=postprocess_faction_value)
    preprocess_field(options, "faction_isnt", aliases, postprocess_value=postprocess_faction_value)


def preprocess_icon (options):
    preprocess_field(options, "icon", ICONS)
    preprocess_field(options, "icon_isnt", ICONS)


def preprocess_sort (options):
    preprocess_field(options, "sort", SORT_KEYS, postprocess_value=get_field_db_key)


def preprocess_count (options):
    preprocess_field(options, "count", COUNT_KEYS, postprocess_value=get_field_db_key)


def preprocess_type (options):
    preprocess_field(options, "type", CARD_TYPES)


def preprocess_field (options, field, candidates, postprocess_value=None):
    if options[field]:
        values = list(options[field])
        for i in range(len(values)):
            value = values[i]
            value = value.lower()
            value = get_single_match(value, candidates)
            if value is None:
                raise ClickException("no such --{} argument: {}.  (Possible arguments: {})".format(
                    get_field_name(field),
                    values[i],
                    ", ".join(candidates)
                ))
            if postprocess_value:
                value = postprocess_value(value)
            values[i] = value
        options[field] = tuple(values)


def get_single_match (value, candidates):
    found = None
    for candidate in candidates:
        if candidate.startswith(value):
            if found:
                return None
            found = candidate
    return found


def get_field_name (field):
    return field[:-len("_isnt")] if field.endswith("_isnt") else field


def get_field_db_key (field):
    return DB_KEY_MAPPING.get(field, field)


def get_faction_name (faction_code):
    return FACTIONS[faction_code].get("name", "House {}".format(faction_code.title()))


def load_cards (options):
    cards_file = get_cards_file()
    if not isfile(cards_file):
        update_cards()
    with open(cards_file, "r") as f:
        return load(f)


def update_cards ():
    cards_file = get_cards_file()
    try:
        remove(cards_file)
    except OSError:
        pass
    urlretrieve(CARDS_URL, cards_file)


def get_cards_file ():
    try:
        mkdir(get_app_dir("thronescli"))
    except OSError:
        pass
    return join(get_app_dir("thronescli"), "cards.json")


def filter_cards (cards, options):
    for card in cards:
        if test_card(card, options):
            yield card


def test_card (card, options):
    for option_name, value in options.items():
        test = CardFilters.get_test(option_name)
        if test and (value or type(value) is int or option_name in TEST_FALSE):
            if not test(card, value, options):
                return False
    return True


class CardFilters (object):
    @classmethod
    def get_test (cls, option):
        try:
            return getattr(cls, "test_" + option)
        except AttributeError:
            return None

    @staticmethod
    def match_value (value, card_value, options):
        if card_value is None:
            return False
        if hasattr(value, "search"):
            match = value.search(card_value)
            if options["exact"]:
                return match is not None and match.start() == 0 and match.end() == len(card_value)
            else:
                return match is not None
        else:
            if not options["case"]:
                card_value = card_value.lower()
            return value == card_value if options["exact"] else value in card_value

    @staticmethod
    def test_claim (card, values, options):
        return any(card["claim"] == value for value in values)

    @staticmethod
    def test_claim_gt (card, value, options):
        return type(card["claim"]) is int and card["claim"] > value

    @staticmethod
    def test_claim_lt (card, value, options):
        return type(card["claim"]) is int and card["claim"] < value

    @staticmethod
    def test_cost (card, values, options):
        return any(card["cost"] == value for value in values)

    @staticmethod
    def test_cost_gt (card, value, options):
        return type(card["cost"]) is int and card["cost"] > value

    @staticmethod
    def test_cost_lt (card, value, options):
        return type(card["cost"]) is int and card["cost"] < value

    @staticmethod
    def test_faction (card, values, options):
        return any(card["faction_code"] == value for value in values)

    @staticmethod
    def test_faction_isnt (card, values, options):
        return all(not card["faction_code"].startswith(value.lower()) for value in values)

    @staticmethod
    def test_income (card, values, options):
        return any(card["income"] == value for value in values)

    @staticmethod
    def test_income_gt (card, value, options):
        return type(card["income"]) is int and card["income"] > value

    @staticmethod
    def test_income_lt (card, value, options):
        return type(card["income"]) is int and card["income"] < value

    @staticmethod
    def test_initiative (card, values, options):
        return any(card["initiative"] == value for value in values)

    @staticmethod
    def test_initiative_gt (card, value, options):
        return type(card["initiative"]) is int and card["initiative"] > value

    @staticmethod
    def test_initiative_lt (card, value, options):
        return type(card["initiative"]) is int and card["initiative"] < value

    @staticmethod
    def test_illustrator (card, values, options):
        return any(CardFilters.match_value(value, card["illustrator"], options) for value in values)

    @staticmethod
    def test_icon (card, values, options):
        any_or_all = any if options["inclusive"] else all
        return any_or_all(card["is_{}".format(value)] for value in values)

    @staticmethod
    def test_icon_isnt (card, values, options):
        any_or_all = any if options["inclusive"] else all
        return any_or_all(not card["is_{}".format(value)] for value in values)

    @staticmethod
    def test_include_draft (card, value, options):
        return options["set"] or value or card["pack_code"] not in DRAFT_PACKS

    @staticmethod
    def test_name (card, value, options):
        return CardFilters.match_value(value, card["name"], options)

    @staticmethod
    def test_loyal (card, values, options):
        return card["is_loyal"] is True

    @staticmethod
    def test_non_loyal (card, values, options):
        return card["is_loyal"] is False

    @staticmethod
    def test_non_unique (card, values, options):
        return card["is_unique"] is False

    @staticmethod
    def test_reserve (card, values, options):
        return any(card["reserve"] == value for value in values)

    @staticmethod
    def test_reserve_gt (card, value, options):
        return type(card["reserve"]) is int and card["reserve"] > value

    @staticmethod
    def test_reserve_lt (card, value, options):
        return type(card["reserve"]) is int and card["reserve"] < value

    @staticmethod
    def test_set (card, values, options):
        return (
            any(CardFilters.match_value(value, card["pack_name"], options) for value in values)
            or any(CardFilters.match_value(value, card["pack_code"], options) for value in values)
        )

    @staticmethod
    def test_str (card, values, options):
        return any(card["strength"] == value for value in values)

    @staticmethod
    def test_str_gt (card, value, options):
        return type(card["strength"]) is int and card["strength"] > value

    @staticmethod
    def test_str_lt (card, value, options):
        return type(card["strength"]) is int and card["strength"] < value

    @staticmethod
    def test_text (card, values, options):
        any_or_all = any if options["inclusive"] else all
        return any_or_all(
            CardFilters.match_value(value, strip_markup(card["text"]), options)
            for value in values
        )

    @staticmethod
    def test_text_isnt (card, values, options):
        any_or_all = any if options["inclusive"] else all
        return any_or_all(
            not CardFilters.match_value(value, strip_markup(card["text"]), options)
            for value in values
        )

    @staticmethod
    def test_trait (card, values, options):
        traits = [trait.strip() for trait in card["traits"].split(".")]
        any_or_all = any if options["inclusive"] else all
        return any_or_all(any(CardFilters.match_value(value, trait, options) for trait in traits) for value in values)

    @staticmethod
    def test_trait_isnt (card, values, options):
        traits = [trait.strip() for trait in card["traits"].split(".")]
        any_or_all = any if options["inclusive"] else all
        return any_or_all(
            not any(CardFilters.match_value(value, trait, options) for trait in traits) for value in values
        )

    @staticmethod
    def test_type (card, values, options):
        return any(card["type_code"].startswith(value.lower()) for value in values)

    @staticmethod
    def test_unique (card, values, options):
        return card["is_unique"] is True


def sort_cards (cards, options):
    if options["sort"]:
        return sorted(cards, key=itemgetter(*options["sort"]))
    return cards


def count_cards (cards, options):
    counts = defaultdict(lambda: defaultdict(int))
    total = 0
    for card in cards:
        total += 1
        if options["count"]:
            for count_field in options["count"]:
                if count_field == "icon":
                    for icon in ICONS:
                        if card["is_" + icon]:
                            counts[count_field][icon] += 1
                elif count_field == "trait":
                    for trait in card["traits"].split("."):
                        if trait:
                            counts[count_field][trait.strip()] += 1
                elif count_field in ["unique", "loyal"]:
                    if card["is_" + count_field]:
                        counts[count_field][count_field.title()] += 1
                    else:
                        counts[count_field]["Non-" + count_field.title()] += 1
                elif card[count_field] or type(card[count_field]) is int:
                    counts[count_field][card[count_field]] += 1
    return counts, total


def print_card (card, options):
    if options["verbose"]:
        print_verbose_card(card, options)
    elif options["brief"]:
        secho(card["name"], fg="cyan", bold=True)
    else:
        print_brief_card(card, options)


def print_verbose_card (card, options):
    secho(card["name"], fg="cyan", bold=True)
    if card["traits"]:
        secho(card["traits"], fg="magenta", bold=True)
    if card["text"]:
        print_markup(card["text"])
    print_verbose_fields(card, [
        ("Income",     "income"),
        ("Initiative", "initiative"),
        ("Claim",      "claim"),
        ("Reserve",    "reserve"),
        ("Cost",       "cost"),
        ("STR",        "strength")
    ])
    if card["type_code"] == "character":
        secho("Icons:", bold=True, nl=False)
        if card["is_military"]:
            secho(" M", fg="red", nl=False)
        if card["is_intrigue"]:
            secho(" I", fg="green", nl=False)
        if card["is_power"]:
            secho(" P", fg="blue", nl=False)
        echo("")
    if options["verbose"] > 1:
        print_verbose_fields(card, [
            ("Faction",    "faction_name"),
            ("Loyal",      "is_loyal"),
            ("Unique",     "is_unique"),
            ("Deck Limit",  "deck_limit"),
            ("Expansion",   "pack_name"),
            ("Card #",      "position"),
            ("Illustrator", "illustrator"),
            ("Flavor Text", "flavor")
        ])
    echo("")


def print_verbose_fields (card, fields):
    for name, field in fields:
        value = card.get(field)
        if value is not None:
            secho("{}: ".format(name), bold=True, nl=False)
            if type(value) is bool:
                echo("Yes" if value else "No")
            elif field in ["flavor"]:
                print_markup(value)
            elif type(value) is int:
                echo(str(value))
            else:
                echo(value)


def print_brief_card (card, options):
    secho(card["name"] + ":", fg="cyan", bold=True, nl=False)
    if card["is_unique"] is True:
        secho(" Unique.", nl=False)
    if card["is_loyal"] is True:
        secho(" Loyal.", nl=False)
    secho(" " + card["faction_name"] + ".", nl=False)
    secho(" " + card["type_name"] + ".", nl=False)
    if card["cost"] is not None:
        secho(" " + str(card["cost"]) + " Cost.", nl=False)
    if card["type_code"] == "character":
        secho(" " + str(card["strength"]) + " STR.", nl=False)
        if card["is_military"]:
            secho(" M", fg="red", bold=True, nl=False)
        if card["is_intrigue"]:
            secho(" I", fg="green", bold=True, nl=False)
        if card["is_power"]:
            secho(" P", fg="blue", bold=True, nl=False)
        if any(card[x] for x in ("is_military", "is_intrigue", "is_power")):
            secho(".", nl=False)
    if card["type_code"] == "plot":
        secho(" " + str(card["income"]) + " Gold.", nl=False)
        secho(" " + str(card["initiative"]) + " Init.", nl=False)
        secho(" " + str(card["claim"]) + " Claim.", nl=False)
        secho(" " + str(card["reserve"]) + " Reserve.", nl=False)
    secho("")


def print_markup (text):
    for styled_text in parse_markup(text):
        echo(styled_text, nl=False)
    echo("")


def parse_markup (text):
    """Very simple markup parser. Does not support nested tags."""
    kwargs = {}
    beg = 0
    while True:
        end = text.find("<", beg)
        if end >= 0:
            yield style(text[beg:end], **kwargs)
            beg = end
            end = text.index(">", beg) + 1
            tag = text[beg:end]
            if tag == "<b>":
                kwargs["bold"] = True
            elif tag == "</b>":
                kwargs.clear()
            elif tag == "<i>":
                kwargs["fg"] = "magenta"
                kwargs["bold"] = True
            elif tag == "</i>":
                kwargs.clear()
            beg = end
        else:
            yield style(text[beg:], **kwargs)
            break


def strip_markup (text):
    return TAG_PATTERN.sub("", text)


def print_counts (counts, options, total):
    if not options["verbose"] and not options["count_only"]:
        echo("")
    for count_field, count_data in counts.items():
        items = list(count_data.items())
        items.sort(key=itemgetter(1), reverse=True)
        secho("{} counts".format(get_pretty_name(count_field)), fg="green", bold=True)
        fill = 0
        for i in range(len(items)):
            items[i] = (get_pretty_name(items[i][0], meta=count_field) + ": ", items[i][1])
            fill = max(fill, len(items[i][0]))
        for count_key, count_val in items:
            secho(count_key, bold=True, nl=False)
            echo(" " * (fill - len(count_key)), nl=False)
            echo(str(count_val))
        echo("")
    secho("Total count: ", fg="green", bold=True, nl=False)
    echo(str(total))


def get_pretty_name (field, meta=None):
    if type(field) is int:
        if meta:
            return "{} {}".format(field, get_pretty_name(meta))
        else:
            return str(field)
    if field in FACTIONS:
        return get_faction_name(field)
    elif field.endswith("_code"):
        return field[:-len("_code")].title()
    elif field == "strength":
        return "STR"
    else:
        return field.title()


if __name__ == '__main__':
    main()
