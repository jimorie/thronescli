Thrones CLI
===========

A command line interface for browsing cards from [A Game of Thrones LCG 2nd Ed](https://www.fantasyflightgames.com/en/products/a-game-of-thrones-the-card-game-second-edition/).

Why?
----

[Thronesdb.com](http://thronesdb.com/) is a great web site, but sometimes it's just nice to do things from the command line.

Thrones CLI also has the ability produce card count breakdowns based on a selected field, with the --count option.

Install
-------

Thrones CLI can be installed from [PyPI](https://pypi.python.org/pypi/thronescli) using pip:

    sudo pip install thronescli

If you download the Python script from [here on GitHub](https://raw.githubusercontent.com/jimorie/thronescli/master/thronescli/thronescli.py) note that there is a third-party dependency on the [Click framework](http://click.pocoo.org/).

Options
-------

Thrones CLI has the following options as given by the --help option:

    Options:
      --brief                  Show brief card data.
      --case                   Use case sensitive matching.
      --claim INTEGER          Find cards with given claim (inclusive).
      --claim-gt INTEGER       Find cards with greater than given claim.
      --claim-lt INTEGER       Find cards with lower than given claim.
      --cost INTEGER           Find cards with given cost (inclusive).
      --cost-gt INTEGER        Find cards with greater than given cost.
      --cost-lt INTEGER        Find cards with lower than given cost.
      --count TEXT             Show card count breakdown for given field. Possible
                               fields are: cost, claim, faction, icon,
                               illustrator, income, initiative, loyal, name,
                               reserve, set, str, trait, type, unique.
      --count-only             Show card count breakdowns only.
      --exact                  Use exact matching.
      -f, --faction TEXT       Find cards with given faction (inclusive). Possible
                               factions are: baratheon, gj, greyjoy, lannister,
                               martell, neutral, night's watch, nw, stark,
                               targaryen, the night's watch, thenightswatch,
                               tyrell.
      --faction-isnt TEXT      Find cards with other than given faction
                               (exclusive).
      --illustrator TEXT       Find cards by the given illustrator (inclusive).
      --income INTEGER         Find cards with given income (inclusive).
      --income-gt INTEGER      Find cards with greater than given income.
      --income-lt INTEGER      Find cards with lower than given income.
      --initiative INTEGER     Find cards with given initiative (inclusive).
      --initiative-gt INTEGER  Find cards with greater than given initiative.
      --initiative-lt INTEGER  Find cards with lower than given initiative.
      --icon TEXT              Find cards with given icon (exclusive). Possible
                               icons are: military, intrigue, power.
      --icon-isnt TEXT         Find cards without given icon (exclusive).
      --inclusive              Treat multiple options of the same type as
                               inclusive rather than exclusive. (Or-logic instead
                               of and-logic.)
      --include-draft          Include cards only legal in draft format.
      --name TEXT              Find cards with matching name. (This is the default
                               search.)
      --name-only              Show only card names.
      --loyal                  Find loyal cards.
      --non-loyal              Find non-loyal cards.
      --non-unique             Find non-unique cards.
      --reserve INTEGER        Find cards with given reserve.
      --reserve-gt INTEGER     Find cards with greater than given reserve.
      --reserve-lt INTEGER     Find cards with lower than given reserve.
      -r, --regex              Use regular expression matching.
      --set TEXT               Find cards from matching expansion sets
                               (inclusive). Implies --include-draft.
      --sort TEXT              Sort resulting cards by the given field. Possible
                               fields are: cost, claim, faction, income,
                               illustrator, initiative, name, reserve, set, str,
                               traits, type.
      --str INTEGER            Find cards with given strength.
      --str-gt INTEGER         Find cards with greater than given strength.
      --str-lt INTEGER         Find cards with lower than given strength.
      --text TEXT              Find cards with matching text (exclusive).
      --text-isnt TEXT         Find cards without matching text (exclusive).
      --trait TEXT             Find cards with matching trait (exclusive).
      --trait-isnt TEXT        Find cards without matching trait (exclusive).
      -t, --type TEXT          Find cards with matching card type (inclusive).
                               Possible types are: agenda, attachment, character,
                               event, location, plot, title.
      --unique                 Find unique cards.
      --update                 Fetch new card data from thronesdb.com.
      -v, --verbose            Show verbose card data. Use twice (-vv) for all
                               data.
      --version                Show the thronescli version: 1.2.
      --help                   Show this message and exit.

Examples
--------

Find a card by its name:

    $ thronescli Asha
    Asha Greyjoy: Unique. House Greyjoy. Character. 5 Cost. 4 STR. M. P.

    Total count: 1

Use the --verbose flag to show all the card data:

    $ thronescli Asha -v
    Asha Greyjoy
    Ironborn. Lady.
    Stealth.
    Reaction: After you win an unopposed challenge in which Asha Greyjoy is participating, stand her.
    Faction: House Greyjoy
    Loyal: No
    Unique: Yes
    Cost: 5
    STR: 4
    Icons: M P
    Deck Limit: 3
    Expansion: Core Set
    Card #: 67
    Illustrator: Mark Behm
    Flavor Text: "I am Asha of House Greyjoy, aye. Opinions differ on whether I'm a lady."

    Total count: 1

Find all Greyjoy characters with an intrigue icon, sorted by STR:

    $ thronescli -f gj --icon i --sort str
    Lordsport Shipwright: House Greyjoy. Character. 2 Cost. 1 STR. I.
    Alannys Greyjoy: Unique. House Greyjoy. Character. 3 Cost. 2 STR. I. P.
    Priest of the Drowned God: House Greyjoy. Character. 3 Cost. 2 STR. I. P.
    Esgred: Unique. House Greyjoy. Character. 5 Cost. 2 STR. M. I. P.
    Wex Pyke: Unique. House Greyjoy. Character. 2 Cost. 2 STR. M. I.
    The Reader: Unique. House Greyjoy. Character. 5 Cost. 4 STR. I. P.
    Aeron Damphair: Unique. House Greyjoy. Character. 6 Cost. 4 STR. I. P.
    Euron Crow's Eye: Unique. House Greyjoy. Character. 7 Cost. 6 STR. M. I. P.

    Total count: 8

Find all non-limited income providing cards:

    $ thronescli --text "\+\d+ Income" --text-isnt "Limited" --regex
    Littlefinger: Unique. Neutral. Character. 5 Cost. 4 STR. I. P.
    Tywin Lannister: Unique. House Lannister. Character. 7 Cost. 6 STR. M. I. P.
    Paxter Redwyne: Unique. House Tyrell. Character. 4 Cost. 3 STR. I.
    Master of Coin: Neutral. Title.
    The God's Eye: Unique. Neutral. Location. 3 Cost.
    Shield of Lannisport: Unique. House Lannister. Attachment. 3 Cost.

    Total count: 6

Find the best faction for using [Street of Silk](http://thronesdb.com/card/02118):

    $ thronescli --trait ally --trait companion --inclusive --count faction --count-only
    Faction counts
    House Lannister:   12
    House Targaryen:   9
    Neutral:           8
    House Martell:     8
    House Greyjoy:     6
    House Stark:       6
    House Tyrell:      5
    House Baratheon:   5
    The Night's Watch: 4

    Total count: 63

Find all 1 cost characters and get a breakdown of their trait and icon spread.

    $ thronescli --cost 1 -t char --count icon --count trait
    Dragonstone Faithful: House Baratheon. Character. 1 Cost. 1 STR. P.
    Iron Islands Fishmonger: House Greyjoy. Character. 1 Cost. 1 STR. P.
    Lannisport Merchant: House Lannister. Character. 1 Cost. 1 STR. P.
    Desert Scavenger: House Martell. Character. 1 Cost. 1 STR. P.
    Messenger Raven: The Night's Watch. Character. 1 Cost. 1 STR.
    Steward at the Wall: The Night's Watch. Character. 1 Cost. 1 STR. I.
    Winterfell Steward: House Stark. Character. 1 Cost. 1 STR. P.
    Viserys Targaryen: Unique. House Targaryen. Character. 1 Cost. 1 STR. P.
    Targaryen Loyalist: House Targaryen. Character. 1 Cost. 1 STR. P.
    Garden Caretaker: House Tyrell. Character. 1 Cost. 1 STR. P.
    Bronn: Unique. House Lannister. Character. 1 Cost. 5 STR. M.
    Rickon Stark: Unique. House Stark. Character. 1 Cost. 1 STR.
    Builder at the Wall: The Night's Watch. Character. 1 Cost. 1 STR. P.

    Trait counts
    Ally:      8
    Steward:   3
    Lord:      2
    Mercenary: 1
    Merchant:  1
    Builder:   1
    Raven:     1

    Icon counts
    Power:    9
    Intrigue: 1
    Military: 1

    Total count: 13

Credits
-------

* All card data is copyright by [Fantasy Flight Games](https://www.fantasyflightgames.com/).
* All card data is provided by [thronesdb.com](http://thronesdb.com/).
* Thrones CLI is written by [Petter Nyström](mailto:jimorie@gmail.com).
