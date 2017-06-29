#!/usr/bin/python

from collections import defaultdict
from json import load
from operator import itemgetter
from os import remove
from os.path import dirname, join, realpath, isfile
from sys import argv
from urllib import urlretrieve

from click import (
    ClickException,
    argument,
    command,
    echo,
    option,
    pass_context,
    secho,
    style
)


CARDS_FILE = join(dirname(realpath(__file__)), "cards.json")
CARDS_URL = "http://thronesdb.com/api/public/cards/"
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
ICONS = [
    "military",
    "intrigue",
    "power"
]
SORT_KEYS = [
    "cost",
    "faction",
    "name",
    "str"
]
COUNT_KEYS = [
    "cost",
    "faction",
    "str",
    "type"
]
DB_KEY_MAPPING = {
    "faction": "faction_code",
    "str"    : "strength",
    "type"   : "type_code"
}
DRAFT_PACKS = [
    "VDS"
]
TEST_FALSE = [
    "include_draft"
]


@command()
@argument(
    "search",
    nargs=-1
)
@option(
    "--case",
    is_flag=True,
    default=False,
    help="Use case sensitive searching (default is not to)."
)
@option(
    "--cost",
    type=int,
    multiple=True,
    help="Return cards with given cost (inclusive)."
)
@option(
    "--cost-gt",
    type=int,
    help="Return cards with greater than given cost."
)
@option(
    "--cost-lt",
    type=int,
    help="Return cards with lower than given cost."
)
@option(
    "--count",
    multiple=True,
    help="Print card count breakdown for given field."
)
@option(
    "--count-only",
    is_flag=True,
    default=False,
    help="Print card count breakdowns only."
)
@option(
    "--exact",
    is_flag=True,
    default=False,
    help="Use exact matching (default is to use partial matching)."
)
@option(
    "--faction",
    "-f",
    multiple=True,
    help="Return cards with given faction (inclusive)."
)
@option(
    "--faction-isnt",
    multiple=True,
    help="Return cards with other than given faction (exclusive)."
)
@option(
    "--icon",
    multiple=True,
    help="Return cards with given icon (exclusive)."
)
@option(
    "--icon-isnt",
    multiple=True,
    help="Return cards without given icon (exclusive)."
)
@option(
    "--include-draft",
    is_flag=True,
    default=False,
    help="Include cards only legal in draft format (default is not to)."
)
@option(
    "--name",
    "-n",
    help="Return cards with matching name."
)
@option(
    "--name-only",
    is_flag=True,
    help="Print only the card name."
)
@option(
    "--loyal",
    is_flag=True,
    help="Return loyal cards."
)
@option(
    "--non-loyal",
    is_flag=True,
    help="Return non-loyal cards."
)
@option(
    "--non-unique",
    is_flag=True,
    help="Return non-unique cards."
)
@option(
    "--sort",
    multiple=True,
    help="Sort returned cards by the given field."
)
@option(
    "--str",
    type=int,
    help="Return cards with given strength."
)
@option(
    "--str-gt",
    type=int,
    help="Return cards with greater than given strength."
)
@option(
    "--str-lt",
    type=int,
    help="Return cards with lower than given strength."
)
@option(
    "--text",
    multiple=True,
    help="Return cards with matching text (exclusive)."
)
@option(
    "--text-isnt",
    multiple=True,
    help="Return cards without matching text (exclusive)."
)
@option(
    "--trait",
    multiple=True,
    help="Return cards with matching trait (exclusive)."
)
@option(
    "--trait-isnt",
    multiple=True,
    help="Return cards without matching trait (exclusive)."
)
@option(
    "--type",
    "-t",
    multiple=True,
    help="Return cards with matching card type (inclusive)."
)
@option(
    "--unique",
    is_flag=True,
    help="Return unique cards."
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
    is_flag=True,
    default=False,
    help="Print verbose card data."
)
@pass_context
def main (ctx, search, **options):
    """
    A simple command line search tool for A Game of Thrones LCG.

    The default search argument matches cards against their name, text or
    traits. See --help for more advanced search options.
    """
    preprocess_options(search, options)
    if options["update"]:
        update_cards()
        echo("Card database updated. Thank you thronesdb.com!")
        return
    if not check_options(options):
        echo(ctx.get_usage())
        return
    cards = load_cards(options)
    cards = filter_cards(cards, options)
    cards = sort_cards(cards, options)
    counts = defaultdict(lambda: defaultdict(int))
    total = 0
    for card in cards:
        if not options["count_only"]:
            print_card(card, options)
        count_card(card, options, counts)
        total += 1
    print_counts(counts, options, total)


def preprocess_options (search, options):
    preprocess_search(options, search)
    preprocess_case(options)
    preprocess_faction(options)
    preprocess_icon(options)
    preprocess_sort(options)
    preprocess_count(options)


def preprocess_search (options, search):
    options["search"] = " ".join(search) if search else None


def preprocess_case (options):
    if not options["case"]:
        if options["search"]:
            options["search"] = options["search"].lower()
        if options["name"]:
            options["name"] = options["name"].lower()
        if options["text"]:
            options["text"] = tuple(value.lower() for value in options["text"])
        if options["text_isnt"]:
            options["text_isnt"] = tuple(value.lower() for value in options["text_isnt"])


def preprocess_faction (options):
    alias_mapping = {
        alias: faction_db_key
        for faction_db_key, data in FACTIONS.iteritems()
        for alias in data.get("alias", []) + [faction_db_key]
    }
    def postprocess_faction_value (value):
        return alias_mapping[value]
    aliases = alias_mapping.keys()
    preprocess_field(options, "faction", aliases, postprocess_value=postprocess_faction_value)
    preprocess_field(options, "faction_isnt", aliases, postprocess_value=postprocess_faction_value)


def preprocess_icon (options):
    preprocess_field(options, "icon", ICONS)
    preprocess_field(options, "icon_isnt", ICONS)


def preprocess_sort (options):
    preprocess_field(options, "sort", SORT_KEYS, postprocess_value=get_field_db_key)


def preprocess_count (options):
    preprocess_field(options, "count", COUNT_KEYS, postprocess_value=get_field_db_key)


def preprocess_field (options, field, candidates, postprocess_value=None):
    if options[field]:
        values = list(options[field])
        for i in xrange(len(values)):
            value = values[i]
            value = value.lower()
            value = get_single_match(value, candidates)
            if value is None:
                raise ClickException("Bad {} argument: {}".format(
                    get_field_name(field),
                    values[i]
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


def get_faction_name (faction_code):
    return FACTIONS[faction_code].get("name", "House {}".format(faction_code.title()))


def check_options (options):
    try:
        return not test_card(None, options)
    except TypeError:
        return True


def load_cards (options):
    if not isfile(CARDS_FILE):
        update_cards()
    with open(CARDS_FILE, "r") as f:
        return load(f)


def sort_cards (cards, options):
    if options["sort"]:
        return sorted(cards, key=itemgetter(*options["sort"]))
    return cards


def update_cards ():
    try:
        remove(CARDS_FILE)
    except OSError:
        pass
    urlretrieve(CARDS_URL, CARDS_FILE)


def print_card (card, options):
    if options["verbose"]:
        print_verbose_card(card, options)
    elif options["name_only"]:
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
        ("Faction",    "faction_name"),
        ("Loyal",      "is_loyal"),
        ("Unique",     "is_unique"),
        ("Income",     "income"),
        ("Initiative", "income"),
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
    print_verbose_fields(card, [
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
            else:
                echo(unicode(value))


def print_brief_card (card, options):
    secho(card["name"], fg="cyan", bold=True, nl=False)
    secho(":", nl=False)
    if card["is_unique"] is True:
        secho(" Unique.", nl=False)
    secho(" " + card["faction_name"] + ".", nl=False)
    secho(" " + card["type_name"] + ".", nl=False)
    if card["cost"] is not None:
        secho(" " + str(card["cost"]) + " Cost.", nl=False)
    if card["type_code"] == "character":
        secho(" " + str(card["strength"]) + " STR.", nl=False)
        if card["is_military"]:
            secho(" M", fg="red", bold=True, nl=False)
            secho(".", nl=False)
        if card["is_intrigue"]:
            secho(" I", fg="green", bold=True, nl=False)
            secho(".", nl=False)
        if card["is_power"]:
            secho(" P", fg="blue", bold=True, nl=False)
            secho(".", nl=False)
    if card["type_code"] == "plot":
        secho(" " + str(card["income"]) + " Gold.", nl=False)
        secho(" " + str(card["initiative"]) + " Init.", nl=False)
        secho(" " + str(card["claim"]) + " Claim.", nl=False)
        secho(" " + str(card["reserve"]) + " Reserve.", nl=False)
    secho("")


def print_counts (counts, options, total):
    if not options["verbose"] and not options["count_only"]:
        echo("")
    for count_field, count_data in counts.iteritems():
        items = count_data.items()
        for i in xrange(len(items)):
            items[i] = (get_pretty_name(items[i][0], meta=count_field) + ":", items[i][1])
        fill = max(len(item[0]) for item in items)
        items.sort(key=itemgetter(1), reverse=True)
        secho("{} counts:".format(get_pretty_name(count_field)), fg="green", bold=True)
        for count_key, count_val in items:
            secho("  {count_key: <{fill}} ".format(count_key=count_key, fill=fill), bold=True, nl=False)
            echo(str(count_val))
        echo("")
    secho("Total count: {}".format(total), fg="green", bold=True)


def filter_cards (cards, options):
    for card in cards:
        if test_card(card, options):
            yield card


def test_card (card, options):
    for option, value in options.iteritems():
        try:
            test = getattr(CardFilters, "test_" + option)
        except AttributeError:
            test = None
        if test and (value or option in TEST_FALSE):
            if not test(card, value, options):

                return False
    return True


def count_card (card, options, counts):
    if options["count"]:
        for count_field in options["count"]:
            if card[count_field]:
                counts[count_field][card[count_field]] += 1


def match_value (value, card_value, options):
    if card_value is None:
        return False
    if not options["case"]:
        card_value = card_value.lower()
    if options["exact"]:
        return value == card_value
    else:
        return value in card_value


class CardFilters (object):
    @staticmethod
    def test_cost (card, values, options):
        return any(card["cost"] == value for value in values)

    @staticmethod
    def test_cost_gt (card, value, options):
        return card["cost"] > value

    @staticmethod
    def test_cost_lt (card, value, options):
        return card["cost"] < value

    @staticmethod
    def test_faction (card, values, options):
        return any(card["faction_code"] == value for value in values)

    @staticmethod
    def test_faction_isnt (card, values, options):
        return all(not card["faction_code"].startswith(value.lower()) for value in values)

    @staticmethod
    def test_icon (card, values, options):
        return all(card["is_{}".format(value)] for value in values)

    @staticmethod
    def test_icon_isnt (card, values, options):
        return all(not card["is_{}".format(value)] for value in values)

    @staticmethod
    def test_include_draft (card, value, options):
        return value or card["pack_code"] not in DRAFT_PACKS

    @staticmethod
    def test_name (card, value, options):
        return match_value(value, card["name"], options)

    @staticmethod
    def test_loyal (card, values, options):
        return card["is_loyal"] == True

    @staticmethod
    def test_non_loyal (card, values, options):
        return card["is_loyal"] == False

    @staticmethod
    def test_non_unique (card, values, options):
        return card["is_unique"] == False

    @staticmethod
    def test_search (card, value, options):
        return (
            CardFilters.test_name(card, value, options)
            or CardFilters.test_text(card, (value,), options)
            or CardFilters.test_trait(card, (value,), options)
        )

    @staticmethod
    def test_str (card, values, options):
        return any(card["strength"] == value for value in values)

    @staticmethod
    def test_str_gt (card, value, options):
        return card["strength"] > value

    @staticmethod
    def test_str_lt (card, value, options):
        return card["strength"] < value

    @staticmethod
    def test_text (card, values, options):
        return all(match_value(value, card["text"], options) for value in values)

    @staticmethod
    def test_text_isnt (card, values, options):
        return all(not match_value(value, card["text"], options) for value in values)

    @staticmethod
    def test_trait (card, values, options):
        traits = [trait.strip().lower() for trait in card["traits"].split(".")]
        return all(any(match_value(value, trait, options) for trait in traits) for value in values)

    @staticmethod
    def test_trait_isnt (card, values, options):
        traits = card["traits"].lower()
        return all(value.lower() not in traits for value in values)

    @staticmethod
    def test_type (card, values, options):
        return any(card["type_code"].startswith(value.lower()) for value in values)

    @staticmethod
    def test_unique (card, values, options):
        return card["is_unique"] == True


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


if __name__ == '__main__':
    main()
