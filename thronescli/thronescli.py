#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from json import load
from operator import itemgetter, eq, ne, gt, ge, lt, le
from os import mkdir, remove
from os.path import join, isfile
from re import compile as re_compile, IGNORECASE
from string import capwords
from sys import argv
from urllib.request import urlretrieve


from click import (
    ClickException,
    ParamType,
    argument,
    command,
    echo,
    get_app_dir,
    option,
    pass_context,
    secho,
    style,
)


__version__ = "2.6.1"


CARDS_URL = "http://thronesdb.com/api/public/cards/"
CARD_TYPES = ["agenda", "attachment", "character", "event", "location", "plot", "title"]
CARD_TYPES_LOYAL = ["attachment", "character", "event", "location", "plot"]
CARD_TYPES_UNIQUE = ["attachment", "character", "location"]
FACTIONS = {
    "baratheon": {},
    "greyjoy": {"alias": ["gj"]},
    "lannister": {},
    "martell": {},
    "neutral": {"name": "Neutral"},
    "stark": {},
    "targaryen": {},
    "thenightswatch": {
        "alias": ["nw", "night's watch", "the night's watch"],
        "name": "The Night's Watch",
    },
    "tyrell": {},
}
FACTION_ALIASES = {
    alias: faction
    for faction, data in FACTIONS.items()
    for alias in data.get("alias", []) + [faction]
}
ICONS = ["military", "intrigue", "power"]
KEYWORDS = [
    "ambush",
    "assault",
    "bestow",
    "insight",
    "intimidate",
    "limited",
    "no attachments",
    "pillage",
    "renown",
    "shadow",
    "stealth",
    "terminal",
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
    "type",
]
COUNT_KEYS = [
    "cost",
    "claim",
    "faction",
    "icon",
    "illustrator",
    "income",
    "initiative",
    "keyword",
    "loyal",
    "name",
    "reserve",
    "set",
    "str",
    "trait",
    "type",
    "unique",
]
DB_KEY_MAPPING = {
    "faction": "faction_code",
    "set": "pack_name",
    "str": "strength",
    "type": "type_code",
    "loyal": "is_loyal",
    "unique": "is_unique",
    "trait": "traits",
}
FIELD_NAME_MAPPING = {v: k for k, v in DB_KEY_MAPPING.items()}
DRAFT_PACKS = ["VDS"]
TEST_FALSE = ["include_draft"]
TAG_PATTERN = re_compile("<.*?>")


class IntComparison(ParamType):
    name = "NUMBER COMPARISON"
    operators = {"==": eq, "!=": ne, "<": lt, "<=": le, ">": gt, ">=": ge}
    parser = re_compile(r"^(==|!=|<|<=|>|>=)?\s*(\d+|[xX])$")

    def convert(self, value, param=None, ctx=None):
        """
        Return a function that implements the integer comparison formulated by
        `value`.

        Examples:
            >>> comparer = IntComparison()
            >>> comparer.convert("10")(10)
            True
            >>> comparer.convert("!=10")(10)
            False
            >>> comparer.convert("<10")(10)
            False
            >>> comparer.convert("<10")(0)
            True
            >>> comparer.convert("<=10")(10)
            True
            >>> comparer.convert(">10")(-1)
            False
            >>> try:
            ...     comparer.convert("foo")(0)
            ... except Exception as e:
            ...     print(str(e))
            Invalid integer comparison: foo
        """
        match = self.parser.match(value.strip())
        if not match:
            self.fail("Invalid integer comparison: {}".format(value))
        operator, number = match.groups()
        func = eq if operator is None else self.operators[operator]
        number = int(number) if number not in ("x", "X") else None

        def compare(x):
            try:
                return func(x, number)
            except TypeError:
                return False

        return compare


INT_COMPARISON = IntComparison()


@command()
@argument("search", nargs=-1)
@option("--brief", is_flag=True, default=False, help="Show brief card data.")
@option("--case", is_flag=True, default=False, help="Use case sensitive matching.")
@option(
    "--claim",
    type=INT_COMPARISON,
    multiple=True,
    help="Find cards whose claim matches the expression (inclusive).",
)
@option(
    "--cost",
    type=INT_COMPARISON,
    multiple=True,
    help="Find cards whose cost matches the expression (inclusive).",
)
@option(
    "--count",
    multiple=True,
    help=(
        "Show card count breakdown for given field. Increase verbosity to "
        "also show individual cards. Possible fields are: {}."
    ).format(", ".join(COUNT_KEYS)),
)
@option("--exact", is_flag=True, default=False, help="Use exact matching.")
@option(
    "--faction",
    "-f",
    multiple=True,
    help="Find cards with given faction (inclusive). Possible factions are: {}.".format(
        ", ".join(sorted(FACTION_ALIASES.keys()))
    ),
)
@option(
    "--faction-isnt",
    multiple=True,
    help="Find cards with other than given faction (exclusive).",
)
@option(
    "--group",
    multiple=True,
    help=(
        "Sort resulting cards by the given field and print group headers. "
        "Possible fields are: {}."
    ).format(", ".join(COUNT_KEYS)),
)
@option(
    "--illustrator",
    multiple=True,
    help="Find cards by the given illustrator (inclusive).",
)
@option(
    "--income",
    type=INT_COMPARISON,
    multiple=True,
    help="Find cards whose income matches the expression (inclusive).",
)
@option(
    "--initiative",
    type=INT_COMPARISON,
    multiple=True,
    help="Find cards whose initiative matches the expression (inclusive).",
)
@option(
    "--icon",
    multiple=True,
    help="Find cards with given icon (exclusive). Possible icons are: {}.".format(
        ", ".join(ICONS)
    ),
)
@option("--icon-isnt", multiple=True, help="Find cards without given icon (exclusive).")
@option(
    "--inclusive",
    is_flag=True,
    default=False,
    help=(
        "Treat multiple options of the same type as inclusive rather than exclusive. "
        "(Or-logic instead of and-logic.)"
    ),
)
@option(
    "--include-draft",
    is_flag=True,
    default=False,
    help="Include cards only legal in draft format.",
)
@option(
    "--name",
    multiple=True,
    help="Find cards with matching name. (This is the default search.)",
)
@option("--loyal", is_flag=True, help="Find loyal cards.")
@option("--non-loyal", is_flag=True, help="Find non-loyal cards.")
@option("--non-unique", is_flag=True, help="Find non-unique cards.")
@option(
    "--reserve",
    type=INT_COMPARISON,
    multiple=True,
    help="Find cards whose reserve matches the expression (inclusive).",
)
@option("--regex", "-r", is_flag=True, help="Use regular expression matching.")
@option(
    "--set",
    multiple=True,
    help=(
        "Find cards from matching expansion sets (inclusive). Implies --include-draft."
    ),
)
@option(
    "--show",
    multiple=True,
    help="Show only given fields in non-verbose mode. Possible fields are: {}.".format(
        ", ".join(COUNT_KEYS)
    ),
)
@option(
    "--sort",
    multiple=True,
    help="Sort resulting cards by the given field. Possible fields are: {}.".format(
        ", ".join(SORT_KEYS)
    ),
)
@option(
    "--str",
    type=INT_COMPARISON,
    multiple=True,
    help="Find cards whose strength matches the expression (inclusive).",
)
@option("--text", multiple=True, help="Find cards with matching text (exclusive).")
@option(
    "--text-isnt", multiple=True, help="Find cards without matching text (exclusive)."
)
@option("--trait", multiple=True, help="Find cards with matching trait (exclusive).")
@option(
    "--trait-isnt", multiple=True, help="Find cards without matching trait (exclusive)."
)
@option(
    "--keyword",
    multiple=True,
    help=(
        "Find cards with matching keyword (exclusive). Possible fields are: {}.".format(
            ", ".join(KEYWORDS)
        )
    ),
)
@option(
    "--keyword-isnt",
    multiple=True,
    help=(
        "Find cards without matching keyword (exclusive). "
        "Possible fields are: {}.".format(", ".join(KEYWORDS))
    ),
)
@option(
    "--type",
    "-t",
    multiple=True,
    help=(
        "Find cards with matching card type (inclusive). "
        "Possible types are: {}.".format(", ".join(CARD_TYPES))
    ),
)
@option("--unique", is_flag=True, help="Find unique cards.")
@option(
    "--update",
    is_flag=True,
    default=False,
    help="Fetch new card data from thronesdb.com.",
)
@option(
    "--verbose",
    "-v",
    count=True,
    help="Show more card data.",
)
@option(
    "--version",
    is_flag=True,
    default=False,
    help="Show the thronescli version: {}.".format(__version__),
)
@pass_context
def main(ctx, search, **options):
    """
    A command line interface for the thronesdb.com card database for A Game of
    Thrones LCG 2nd Ed.

    The default search argument matches cards against their name, text or
    traits. See below for more options.

    Options marked with inclusive or exclusive can be repeated to further
    include or exclude cards, respectively.

    For help and bug reports visit the project on GitHub:
    https://github.com/jimorie/thronescli
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
    if options["cost"]:
        options["type"] += ("character", "location", "attachment", "event")
    if options["str"] or options["icon"]:
        options["type"] += ("character",)
    if (
        options["income"]
        or options["reserve"]
        or options["claim"]
        or options["initiative"]
    ):
        options["type"] += ("plot",)
    cards = load_cards(options)
    cards = filter_cards(cards, options)
    cards = sort_cards(cards, options)
    cards = list(cards)
    counts, total = count_cards(cards, options)
    if options["count"]:
        options["verbose"] -= 1
    elif total == 1 and options["brief"] is False:
        options["verbose"] += 1
    if options["show"]:
        options["verbose"] = 0
        options["brief"] = False
    prevgroup = None
    groupkey = sortkey(*options["group"]) if options["group"] else None
    for card in cards:
        if options["verbose"] >= 0:
            if groupkey:
                thisgroup = groupkey(card)
                if thisgroup != prevgroup:
                    if prevgroup is not None and options["verbose"] < 1:
                        echo("")
                    secho(
                        "[ {} ]".format(
                            " | ".join(
                                format_card_field(card, group, color=False)
                                for group in options["group"]
                            )
                        ),
                        fg="yellow",
                        bold=True,
                    )
                    echo("")
                    prevgroup = thisgroup
            print_card(card, options)
    print_counts(counts, options, total)


def preprocess_options(search, options):
    """Preprocess all options."""
    preprocess_search(options, search)
    preprocess_regex(options)
    preprocess_case(options)
    preprocess_faction(options)
    preprocess_icon(options)
    preprocess_sort(options)
    preprocess_count(options)
    preprocess_type(options)
    preprocess_keyword(options)


def preprocess_search(options, search):
    """Treat non-option args as one string."""
    if search:
        options["name"] = [" ".join(search), *options["name"]]


def preprocess_regex(options):
    """Compile regex patterns for relevant options."""
    flags = IGNORECASE if not options["case"] else 0
    if options["regex"]:
        if options["name"]:
            options["name"] = [re_compile(x, flags=flags) for x in options["name"]]
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


def preprocess_case(options):
    """Preprocess relevant options for case comparison."""
    # These options are always case insensitive
    opts = ("set", "keyword", "keyword_isnt")
    for opt in opts:
        options[opt] = tuple(value.lower() for value in options[opt])
    if not options["case"] and not options["regex"]:
        # These options respect the case and regex options
        opts = ("text", "text_isnt", "trait", "trait_isnt", "illustrator")
        for opt in opts:
            options[opt] = tuple(value.lower() for value in options[opt])
        if options["name"]:
            options["name"] = [name.lower() for name in options["name"]]


def preprocess_faction(options):
    """Preprocess faction arguments to valid options."""

    def postprocess_faction_value(value):
        return FACTION_ALIASES[value]

    aliases = FACTION_ALIASES.keys()
    preprocess_field(
        options, "faction", aliases, postprocess_value=postprocess_faction_value
    )
    preprocess_field(
        options, "faction_isnt", aliases, postprocess_value=postprocess_faction_value
    )


def preprocess_icon(options):
    """Preprocess icon arguments to valid options."""
    preprocess_field(options, "icon", ICONS)
    preprocess_field(options, "icon_isnt", ICONS)


def preprocess_sort(options):
    """Preprocess sortable arguments to valid options."""
    preprocess_field(options, "group", COUNT_KEYS, postprocess_value=get_field_db_key)
    preprocess_field(options, "sort", SORT_KEYS, postprocess_value=get_field_db_key)
    preprocess_field(options, "show", COUNT_KEYS, postprocess_value=get_field_db_key)


def preprocess_count(options):
    """Preprocess count arguments to valid options."""
    preprocess_field(options, "count", COUNT_KEYS, postprocess_value=get_field_db_key)


def preprocess_type(options):
    """Preprocess type arguments to valid options."""
    preprocess_field(options, "type", CARD_TYPES)


def preprocess_keyword(options):
    """Preprocess keyword arguments to valid options."""
    preprocess_field(options, "keyword", KEYWORDS)
    preprocess_field(options, "keyword_isnt", KEYWORDS)


def preprocess_field(options, field, candidates, postprocess_value=None):
    """
    Preprocess value of `field` in `options` to the best match in `candidates`.
    """
    if options[field]:
        values = list(options[field])
        for i in range(len(values)):
            value = values[i]
            value = value.lower()
            value = get_single_match(value, candidates)
            if value is None:
                raise ClickException(
                    "no such --{} argument: {}.  (Possible arguments: {})".format(
                        get_field_name(field), values[i], ", ".join(candidates)
                    )
                )
            if postprocess_value:
                value = postprocess_value(value)
            values[i] = value
        options[field] = tuple(values)


def get_single_match(value, candidates):
    """
    Return the single member in `candidates` that starts with `value`, else
    `None`.

    Examples:
        >>> get_single_match("foo", ["foobar", "barfoo"])
        'foobar'
        >>> get_single_match("foo", ["foobar", "barfoo", "foobarfoo"]) is None
        True
        >>> get_single_match("foo", ["barfoo"]) is None
        True
        >>> get_single_match("foo", []) is None
        True
        >>> get_single_match("", []) is None
        True
        >>> get_single_match("", ["foobar"])
        'foobar'
        >>> get_single_match("", ["foobar", "barfoo"]) is None
        True
    """
    found = None
    for candidate in candidates:
        if candidate.startswith(value):
            if found:
                return None
            found = candidate
    return found


def get_field_name(field):
    """Return `field` without negating suffix."""
    return field[: -len("_isnt")] if field.endswith("_isnt") else field


def get_field_db_key(field):
    """Return the corresponding database field for `field`."""
    return DB_KEY_MAPPING.get(field, field)


def get_faction_name(faction_code):
    """Return a human friendly faction name for `faction_code`."""
    return FACTIONS[faction_code].get("name", "House {}".format(capwords(faction_code)))


def load_cards(options):
    """Return the card database loaded from file."""
    cards_file = get_cards_file()
    if not isfile(cards_file):
        update_cards()
    with open(cards_file, "r") as f:
        return load(f)


def update_cards():
    """Fetch a new card database and write it to file."""
    cards_file = get_cards_file()
    try:
        remove(cards_file)
    except OSError:
        pass
    urlretrieve(CARDS_URL, cards_file)


def get_cards_file():
    """Return the path of the card database file."""
    try:
        mkdir(get_app_dir("thronescli"))
    except OSError:
        pass
    return join(get_app_dir("thronescli"), "cards.json")


def filter_cards(cards, options):
    """Yield all members in `cards` that match the given `options`."""
    for card in cards:
        if test_card(card, options):
            yield card


def test_card(card, options):
    """Return `True` if `card` match the given `options`, else `False`."""
    for option_name, value in options.items():
        test = CardFilters.get_test(option_name)
        if test and (value or type(value) is int or option_name in TEST_FALSE):
            if not test(card, value, options):
                return False
    return True


class CardFilters(object):
    @classmethod
    def get_test(cls, option):
        try:
            return getattr(cls, "test_" + option)
        except AttributeError:
            return None

    @staticmethod
    def match_value(value, card_value, options):
        """
        Test if the requested `value` matches the `card_value`. Where `value`
        can be both a string or a regex object.

        Examples:
            >>> CardFilters.match_value("foo", "foo", defaultdict(bool))
            True
            >>> CardFilters.match_value("foo", "bar", defaultdict(bool))
            False
            >>> CardFilters.match_value("foo", "Foo", defaultdict(bool))
            True
            >>> CardFilters.match_value("foo", "Foo", defaultdict(bool, case=True))
            False
            >>> CardFilters.match_value("foo", "foofoo", defaultdict(bool))
            True
            >>> CardFilters.match_value("foo", "foofoo", defaultdict(bool, exact=True))
            False
            >>> CardFilters.match_value(re_compile("f[oaeu]+"), "foofoo", defaultdict(bool))
            True
            >>> CardFilters.match_value(re_compile("f[oaeu]+"), "boo", defaultdict(bool))
            False
            >>> CardFilters.match_value(re_compile("f[oaeu]+"), "foofoo", defaultdict(bool, exact=True))
            False
        """
        if card_value is None:
            return False
        if hasattr(value, "search"):
            match = value.search(card_value)
            if options["exact"]:
                return (
                    match is not None
                    and match.start() == 0
                    and match.end() == len(card_value)
                )
            else:
                return match is not None
        else:
            if not options["case"]:
                card_value = card_value.lower()
            return value == card_value if options["exact"] else value in card_value

    @staticmethod
    def test_claim(card, tests, options):
        return any(test(card["claim"]) for test in tests)

    @staticmethod
    def test_cost(card, tests, options):
        return any(test(card["cost"]) for test in tests)

    @staticmethod
    def test_faction(card, values, options):
        return any(card["faction_code"] == value for value in values)

    @staticmethod
    def test_faction_isnt(card, values, options):
        return all(card["faction_code"] != value for value in values)

    @staticmethod
    def test_income(card, tests, options):
        return any(test(card["income"]) for test in tests)

    @staticmethod
    def test_initiative(card, tests, options):
        return any(test(card["initiative"]) for test in tests)

    @staticmethod
    def test_illustrator(card, values, options):
        return any(
            CardFilters.match_value(value, card["illustrator"], options)
            for value in values
        )

    @staticmethod
    def test_icon(card, values, options):
        if card["type_code"] != "character":
            return False
        any_or_all = any if options["inclusive"] else all
        return any_or_all(card["is_{}".format(value)] for value in values)

    @staticmethod
    def test_icon_isnt(card, values, options):
        if card["type_code"] != "character":
            return False
        any_or_all = any if options["inclusive"] else all
        return any_or_all(not card["is_{}".format(value)] for value in values)

    @staticmethod
    def test_include_draft(card, value, options):
        return options["set"] or value or card["pack_code"] not in DRAFT_PACKS

    @staticmethod
    def test_name(card, value, options):
        return any(
            CardFilters.match_value(name, card["name"], options) for name in value
        )

    @staticmethod
    def test_loyal(card, values, options):
        return card["type_code"] in CARD_TYPES_LOYAL and card["is_loyal"] is True

    @staticmethod
    def test_non_loyal(card, values, options):
        return card["type_code"] in CARD_TYPES_LOYAL and card["is_loyal"] is False

    @staticmethod
    def test_unique(card, values, options):
        return card["type_code"] in CARD_TYPES_UNIQUE and card["is_unique"] is True

    @staticmethod
    def test_non_unique(card, values, options):
        return card["type_code"] in CARD_TYPES_UNIQUE and card["is_unique"] is False

    @staticmethod
    def test_reserve(card, tests, options):
        return any(test(card["reserve"]) for test in tests)

    @staticmethod
    def test_set(card, values, options):
        return any(
            CardFilters.match_value(value, card["pack_name"], options)
            for value in values
        ) or any(
            CardFilters.match_value(value, card["pack_code"], options)
            for value in values
        )

    @staticmethod
    def test_str(card, tests, options):
        return any(test(card["strength"]) for test in tests)

    @staticmethod
    def test_text(card, values, options):
        any_or_all = any if options["inclusive"] else all
        return any_or_all(
            CardFilters.match_value(value, strip_markup(card["text"]), options)
            for value in values
        )

    @staticmethod
    def test_text_isnt(card, values, options):
        any_or_all = any if options["inclusive"] else all
        return any_or_all(
            not CardFilters.match_value(value, strip_markup(card["text"]), options)
            for value in values
        )

    @staticmethod
    def test_trait(card, values, options):
        traits = [trait.strip() for trait in card["traits"].split(".")]
        any_or_all = any if options["inclusive"] else all
        return any_or_all(
            any(CardFilters.match_value(value, trait, options) for trait in traits)
            for value in values
        )

    @classmethod
    def test_trait_isnt(cls, card, values, options):
        return not cls.test_trait(card, values, options)

    @staticmethod
    def test_keyword(card, values, options):
        keywords = parse_keywords(card["text"])
        any_or_all = any if options["inclusive"] else all
        return any_or_all(
            any(
                CardFilters.match_value(value, keyword, options) for keyword in keywords
            )
            for value in values
        )

    @classmethod
    def test_keyword_isnt(cls, card, values, options):
        return not cls.test_keyword(card, values, options)

    @staticmethod
    def test_type(card, values, options):
        return any(card["type_code"].startswith(value.lower()) for value in values)


def sortkey(*sortfields):
    def _sortkey(card):
        sortkey = []
        for field in sortfields:
            if field == "traits":
                sortkey.append(len(card["traits"].split(".")))
            elif field in card:
                sortkey.append(card[field])
            elif field == "icon":
                iconscore = 0
                if card["is_military"]:
                    iconscore -= 12
                if card["is_intrigue"]:
                    iconscore -= 11
                if card["is_power"]:
                    iconscore -= 10
                sortkey.append(iconscore)
            else:
                sortkey.append(format_card_field(card, field, color=False))
        return sortkey

    return _sortkey


def sort_cards(cards, options):
    if options["sort"] or options["group"]:
        sortfields = options["group"] + options["sort"]
        return sorted(cards, key=sortkey(*sortfields))
    return cards


def count_cards(cards, options):
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
                elif count_field == "traits":
                    for trait in card["traits"].split("."):
                        if trait:
                            counts[count_field][trait.strip()] += 1
                elif count_field == "keyword":
                    for keyword in parse_keywords(card["text"]):
                        counts[count_field][keyword] += 1
                elif count_field in ["is_unique", "is_loyal"]:
                    if card[count_field]:
                        counts[count_field][format_field_name(count_field)] += 1
                    else:
                        counts[count_field][
                            "Non-" + format_field_name(count_field)
                        ] += 1
                elif card[count_field] or type(card[count_field]) is int:
                    counts[count_field][card[count_field]] += 1
    return counts, total


def print_card(card, options):
    if options["verbose"]:
        print_verbose_card(card, options)
    elif options["brief"]:
        secho(card["name"], fg="cyan", bold=True)
    elif options["show"]:
        print_brief_card(card, options, options["show"])
    else:
        print_brief_card(card, options)


def print_verbose_card(card, options):
    secho(card["name"], fg="cyan", bold=True)
    if card["traits"]:
        secho(card["traits"], fg="magenta", bold=True)
    if card["text"]:
        print_markup(card["text"])
    fields = []
    if card["type_code"] == "plot":
        fields += [
            ("Income", "income"),
            ("Initiative", "initiative"),
            ("Claim", "claim"),
            ("Reserve", "reserve"),
        ]
    if card["type_code"] in ("character", "location", "attachment", "event"):
        fields += [
            ("Cost", "cost"),
        ]
    if card["type_code"] in ("character"):
        fields += [
            ("STR", "strength"),
            ("Icons", "icon"),
        ]
    if options["verbose"] > 1:
        fields += [
            ("Faction", "faction_name"),
            ("Loyal", "is_loyal"),
            ("Unique", "is_unique"),
            ("Deck Limit", "deck_limit"),
            ("Expansion", "pack_name"),
            ("Card #", "position"),
            ("Illustrator", "illustrator"),
            ("Flavor Text", "flavor"),
        ]
    print_verbose_fields(card, fields)
    echo("")


def print_verbose_fields(card, fields):
    for name, field in fields:
        value = card.get(field)
        secho("{}: ".format(name), bold=True, nl=False)
        if field == "icon":
            secho(format_card_field(card, "icon"))
        elif value is None:
            echo("X")
        elif type(value) is bool:
            echo("Yes" if value else "No")
        elif field in ["flavor"]:
            print_markup(value)
        elif type(value) is int:
            echo(str(value))
        else:
            echo(value)


def print_brief_card(card, options, show=None):
    """Print `card` details on one line."""
    if show is None:
        show = ["unique", "loyal", "faction", "type"]
        if card["type_code"] == "character":
            show.extend(["cost", "str", "icon"])
        elif card["type_code"] == "plot":
            show.extend(["income", "initiative", "claim", "reserve"])
        else:
            show.extend(["cost"])
    secho(card["name"] + ":", fg="cyan", bold=True, nl=False)
    for field in show:
        tmp = format_card_field(card, field, show_negation=False)
        if tmp:
            if tmp.endswith("."):
                secho(" {}".format(tmp), nl=False)
            else:
                secho(" {}.".format(tmp), nl=False)
    secho("")


def print_markup(text):
    """Print `text` with HTML markup converted to ASCII escape codes."""
    for styled_text in parse_markup(text):
        echo(styled_text, nl=False)
    echo("")


def parse_markup(text):
    """
    Parse `text` as HTML and yield ASCII styled strings. Supports only basic
    HTML and does not handle nested tags.

    Examples:
        >>> list(parse_markup("foo"))
        ['foo\\x1b[0m']
        >>> list(parse_markup("<b>foo</b>"))
        ['\\x1b[1mfoo\\x1b[0m']
        >>> list(parse_markup("xxx<b>foo</b>yyy"))
        ['xxx\\x1b[0m', '\\x1b[1mfoo\\x1b[0m', 'yyy\\x1b[0m']
        >>> list(parse_markup("xxx<i>foo</i>yyy"))
        ['xxx\\x1b[0m', '\\x1b[35m\\x1b[1mfoo\\x1b[0m', 'yyy\\x1b[0m']
        >>> list(parse_markup("xxx<b>foo"))
        ['xxx\\x1b[0m', '\\x1b[1mfoo\\x1b[0m']
        >>> list(parse_markup("xxx</b>foo"))
        ['xxx\\x1b[0m', 'foo\\x1b[0m']
    """
    kwargs = {}
    beg = 0
    while True:
        end = text.find("<", beg)
        if end >= 0:
            if beg < end:
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
            if beg < len(text):
                yield style(text[beg:], **kwargs)
            break


def strip_markup(text):
    """Return a version of `text` without HTML tags."""
    return TAG_PATTERN.sub("", text)


def print_counts(counts, options, total):
    """Print a human friendly summary of the `counts` and `total`."""
    if options["verbose"] == 0:
        echo("")
    for count_field, count_data in counts.items():
        items = list(count_data.items())
        items.sort(key=itemgetter(1), reverse=True)
        secho(
            "[ {} counts ]".format(format_field_name(count_field)),
            fg="green",
            bold=True,
        )
        echo("")
        fill = 0
        for i in range(len(items)):
            items[i] = (format_field(count_field, items[i][0]), items[i][1])
            fill = max(fill, len(items[i][0]))
        for count_key, count_val in items:
            secho(count_key, bold=True, nl=False)
            echo(": ", nl=False)
            echo(" " * (fill - len(count_key)), nl=False)
            echo(str(count_val))
        echo("")
    secho("Total count: ", fg="green", bold=True, nl=False)
    echo(str(total))


def format_field_name(field):
    """Format a `field` name for human friendly output."""
    field = FIELD_NAME_MAPPING.get(field, field)
    if field in ["str"]:
        return field.upper()
    return capwords(field)


def format_field(field, value, show_negation=True):
    """Format a basic `field` and `value` for human friendly output."""
    if value is None:
        return "X {}".format(format_field_name(field))
    if type(value) is int:
        return "{} {}".format(value, format_field_name(field))
    if type(value) is bool:
        if show_negation or value:
            return "{}{}".format("" if value else "Non-", format_field_name(field))
        return None
    if field == "faction_code" or field == "faction":
        return get_faction_name(value)
    if isinstance(value, str):
        return capwords(value)
    return str(value)


def format_card_field(card, field, color=True, show_negation=True):
    """Format the value of `field` on `card` for human friendly output."""
    if field == "icon":
        icons = []
        if card["is_military"]:
            if color:
                icons.append(style("M", fg="red", bold=True))
            else:
                icons.append("M")
        if card["is_intrigue"]:
            if color:
                icons.append(style("I", fg="green", bold=True))
            else:
                icons.append("I")
        if card["is_power"]:
            if color:
                icons.append(style("P", fg="blue", bold=True))
            else:
                icons.append("P")
        return " ".join(icons) if icons else "No Icons"
    if field == "keyword":
        keywords = parse_keywords(card["text"])
        if keywords:
            return " ".join(capwords(kw) + "." for kw in keywords)
    db_key = get_field_db_key(field)
    return format_field(field, card.get(db_key), show_negation=show_negation)


def parse_keywords(text):
    """Return the list of valid keywords found at the start of `text`."""
    text = text.lower()
    keywords = []
    while True:
        for keyword in KEYWORDS:
            if text.startswith(keyword):
                keywords.append(keyword)
                text = text[text.find(".") + 1 :].strip()
                break
        else:
            break
    return keywords


if __name__ == "__main__":
    main()
