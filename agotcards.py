#!/usr/bin/python

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
FACTIONS = [
    "baratheon",
    "greyjoy",
    "lannister",
    "martell",
    "neutral",
    "stark",
    "targaryen",
    "thenightswatch",
    "tyrell"
]
SORT_KEYS = [
    "cost",
    "faction",
    "name",
    "str"
]


@command()
@argument(
    "search",
    nargs=-1
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
    "--case",
    is_flag=True,
    default=False,
    help="Use case sensitive searching (default is not to)."
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
    """A simple command line search tool for A Game of Thrones LCG."""
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
    for card in cards:
        print_card(card, options)


def preprocess_options (search, options):
    search = " ".join(search)
    if not options["case"]:
        search = search.lower()
        if options["name"]:
            options["name"] = options["name"].lower()
        if options["text"]:
            options["text"] = tuple(value.lower() for value in options["text"])
        if options["text_isnt"]:
            options["text_isnt"] = tuple(value.lower() for value in options["text_isnt"])
    options["search"] = search
    preprocess_faction(options)


def preprocess_faction (options):
    if options["faction"]:
        values = list(options["faction"])
        for i in xrange(len(values)):
            value = values[i]
            value = value.lower()
            value = value.replace("'", "")
            value = value.replace(" ", "")
            if value == "nw" or value.startswith("ni"):
                value = "thenightswatch"
            elif value == "gj":
                value = "greyjoy"
            else:
                value = get_single_match(value, FACTIONS)
                if value is None:
                    raise ClickException("Bad faction: {}".format(
                        values[i]
                    ))
            values[i] = value
        options["faction"] = tuple(values)


def sort_cards (cards, options):
    if options["sort"]:
        key_chain = list(options["sort"])
        for i in xrange(len(key_chain)):
            key = get_single_match(key_chain[i], SORT_KEYS)
            if key is None:
                raise ClickException("Bad sort field: {}".format(
                    key
                ))
            if key == "faction":
                key = "faction_code"
            elif key == "str":
                key = "strength"
            key_chain[i] = key
        return sorted(cards, key=itemgetter(*key_chain))
    return cards


def get_single_match (value, candidates):
    found = None
    for candidate in candidates:
        if candidate.startswith(value):
            if found:
                return None
            found = candidate
    return found


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
        if test and value:
            if not test(card, value, options):
                return False
    return True


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
    def test_name (card, value, options):
        name = card["name"] if options["case"] else card["name"].lower()
        return value in name

    @staticmethod
    def test_non_unique (card, values, options):
        return card["is_unique"] == False

    @staticmethod
    def test_search (card, value, options):
        name   = card["name"]
        text   = card["text"] or ""
        traits = card["traits"] or ""
        if not options["case"]:
            name = name.lower()
            text = text.lower()
            traits = traits.lower()
        return value in name or value in text or value in traits

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
        text = card["text"]
        if not text:
            return False
        if not options["case"]:
            text = text.lower()
        return all(value in text for value in values)

    @staticmethod
    def test_text_isnt (card, values, options):
        text = card["text"]
        if not text:
            return True
        if not options["case"]:
            text = text.lower()
        return all(value not in text for value in values)

    @staticmethod
    def test_trait (card, values, options):
        traits = card["traits"].lower()
        return all(value.lower() in traits for value in values)

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
