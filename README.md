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

Options
-------

Thrones CLI has the following options as given by the --help option:

    Options:
      --brief                      Show brief card data.
      --case                       Use case sensitive matching.
      --claim INT COMPARISON       Find cards whose claim matches the expression
                                   (inclusive).
      --cost INT COMPARISON        Find cards whose cost matches the expression
                                   (inclusive).
      --count TEXT                 Show card count breakdown for given field.
                                   Possible fields are: cost, claim, faction,
                                   icon, illustrator, income, initiative, keyword,
                                   loyal, name, reserve, set, str, trait, type,
                                   unique.
      --count-only                 Show card count breakdowns only.
      --exact                      Use exact matching.
      -f, --faction TEXT           Find cards with given faction (inclusive).
                                   Possible factions are: baratheon, gj, greyjoy,
                                   lannister, martell, neutral, night's watch, nw,
                                   stark, targaryen, the night's watch,
                                   thenightswatch, tyrell.
      --faction-isnt TEXT          Find cards with other than given faction
                                   (exclusive).
      --group TEXT                 Sort resulting cards by the given field and
                                   print group headers. Possible fields are: cost,
                                   claim, faction, icon, illustrator, income,
                                   initiative, keyword, loyal, name, reserve, set,
                                   str, trait, type, unique.
      --illustrator TEXT           Find cards by the given illustrator
                                   (inclusive).
      --income INT COMPARISON      Find cards whose income matches the expression
                                   (inclusive).
      --initiative INT COMPARISON  Find cards whose initiative matches the
                                   expression (inclusive).
      --icon TEXT                  Find cards with given icon (exclusive).
                                   Possible icons are: military, intrigue, power.
      --icon-isnt TEXT             Find cards without given icon (exclusive).
      --inclusive                  Treat multiple options of the same type as
                                   inclusive rather than exclusive. (Or-logic
                                   instead of and-logic.)
      --include-draft              Include cards only legal in draft format.
      --name TEXT                  Find cards with matching name. (This is the
                                   default search.)
      --loyal                      Find loyal cards.
      --non-loyal                  Find non-loyal cards.
      --non-unique                 Find non-unique cards.
      --reserve INT COMPARISON     Find cards whose reserve matches the expression
                                   (inclusive).
      -r, --regex                  Use regular expression matching.
      --set TEXT                   Find cards from matching expansion sets
                                   (inclusive). Implies --include-draft.
      --show TEXT                  Show only given fields in non-verbose mode.
                                   Possible fields are: cost, claim, faction,
                                   icon, illustrator, income, initiative, keyword,
                                   loyal, name, reserve, set, str, trait, type,
                                   unique.
      --sort TEXT                  Sort resulting cards by the given field.
                                   Possible fields are: cost, claim, faction,
                                   income, illustrator, initiative, name, reserve,
                                   set, str, traits, type.
      --str INT COMPARISON         Find cards whose strength matches the
                                   expression (inclusive).
      --text TEXT                  Find cards with matching text (exclusive).
      --text-isnt TEXT             Find cards without matching text (exclusive).
      --trait TEXT                 Find cards with matching trait (exclusive).
      --trait-isnt TEXT            Find cards without matching trait (exclusive).
      --keyword TEXT               Find cards with matching keyword (exclusive).
                                   Possible fields are: ambush, insight,
                                   intimidate, limited, no attachments, pillage,
                                   renown, shadow, stealth, terminal.
      --keyword-isnt TEXT          Find cards without matching keyword
                                   (exclusive). Possible fields are: ambush,
                                   insight, intimidate, limited, no attachments,
                                   pillage, renown, shadow, stealth, terminal.
      -t, --type TEXT              Find cards with matching card type (inclusive).
                                   Possible types are: agenda, attachment,
                                   character, event, location, plot, title.
      --unique                     Find unique cards.
      --update                     Fetch new card data from thronesdb.com.
      -v, --verbose                Show verbose card data. Use twice (-vv) for all
                                   data.
      --version                    Show the thronescli version: 1.6.1.
      --help                       Show this message and exit.

Examples
--------

Find a card by its name:

    $ thronescli Asha
    Asha Greyjoy: Unique. House Greyjoy. Character. 5 Cost. 4 STR. M P.
    Asha Greyjoy: Unique. Loyal. House Greyjoy. Character. 7 Cost. 5 STR. M I P.

    Total count: 2

Use the --verbose flag to show all the card data:

    $ thronescli Asha -v
    Asha Greyjoy
    Ironborn. Lady.
    Stealth.
    Reaction: After you win an unopposed challenge in which Asha Greyjoy is participating, stand her.
    Cost: 5
    STR: 4
    Icons: M P

    Asha Greyjoy
    Captain. Ironborn. Lady.
    Pillage. Stealth.
    Reaction: After Asha Greyjoy discards a card using pillage, search the top X cards of your deck for a card and add it to your hand. Shuffle your deck. X is the number of cards in the losing opponent's discard pile.
    Cost: 7
    STR: 5
    Icons: M I P

    Total count: 2

    $ thronescli Asha -vv
    Asha Greyjoy
    Ironborn. Lady.
    Stealth.
    Reaction: After you win an unopposed challenge in which Asha Greyjoy is participating, stand her.
    Cost: 5
    STR: 4
    Icons: M P
    Faction: House Greyjoy
    Loyal: No
    Unique: Yes
    Deck Limit: 3
    Expansion: Core Set
    Card #: 67
    Illustrator: Mark Behm
    Flavor Text: "I am Asha of House Greyjoy, aye. Opinions differ on whether I'm a lady."

    Asha Greyjoy
    Captain. Ironborn. Lady.
    Pillage. Stealth.
    Reaction: After Asha Greyjoy discards a card using pillage, search the top X cards of your deck for a card and add it to your hand. Shuffle your deck. X is the number of cards in the losing opponent's discard pile.
    Cost: 7
    STR: 5
    Icons: M I P
    Faction: House Greyjoy
    Loyal: Yes
    Unique: Yes
    Deck Limit: 3
    Expansion: Kingsmoot
    Card #: 51
    Illustrator: Magali Villeneuve
    Flavor Text:

    Total count: 2

Find all Greyjoy characters with an intrigue icon, grouped by STR:

    $ thronescli -f gj --icon i --group str
    [ 1 STR ]

    Lordsport Shipwright: House Greyjoy. Character. 2 Cost. 1 STR. I.

    [ 2 STR ]

    Alannys Greyjoy: Unique. House Greyjoy. Character. 3 Cost. 2 STR. I P.
    Priest of the Drowned God: House Greyjoy. Character. 3 Cost. 2 STR. I P.
    Esgred: Unique. House Greyjoy. Character. 5 Cost. 2 STR. M I P.
    Wex Pyke: Unique. House Greyjoy. Character. 2 Cost. 2 STR. M I.

    [ 3 STR ]

    Drowned God's Apostle: House Greyjoy. Character. 4 Cost. 3 STR. I P.

    [ 4 STR ]

    The Reader: Unique. Loyal. House Greyjoy. Character. 5 Cost. 4 STR. I P.
    Aeron Damphair: Unique. House Greyjoy. Character. 6 Cost. 4 STR. I P.
    Tarle the Thrice-Drowned: Unique. Loyal. House Greyjoy. Character. 5 Cost. 4 STR. I P.

    [ 5 STR ]

    Asha Greyjoy: Unique. Loyal. House Greyjoy. Character. 7 Cost. 5 STR. M I P.

    [ 6 STR ]

    Euron Crow's Eye: Unique. Loyal. House Greyjoy. Character. 7 Cost. 6 STR. M I P.

    Total count: 11

Find all non-limited income providing cards:

    $ thronescli --text "\+\d+ Income" --text-isnt "Limited" --regex
    Littlefinger: Unique. Neutral. Character. 5 Cost. 4 STR. I P.
    Tywin Lannister: Unique. Loyal. House Lannister. Character. 7 Cost. 6 STR. M I P.
    Paxter Redwyne: Unique. Loyal. House Tyrell. Character. 4 Cost. 3 STR. I.
    Master of Coin: Neutral. Title. No Cost.
    The God's Eye: Unique. Neutral. Location. 3 Cost.
    Shield of Lannisport: Unique. Loyal. House Lannister. Attachment. 3 Cost.
    Northern Armory: Loyal. House Stark. Location. 2 Cost.
    Stormlands Fiefdom: Loyal. House Baratheon. Location. 2 Cost.
    Tycho Nestoris: Unique. Neutral. Character. 6 Cost. 3 STR. P.
    Refurbished Hulk: Loyal. House Greyjoy. Location. 2 Cost.

    Total count: 10

Find the best faction for using [Street of Silk](http://thronesdb.com/card/02118):

    $ thronescli --trait ally --trait companion --inclusive --count faction --count-only
    [ Faction counts ]

    House Targaryen:   15
    House Lannister:   14
    Neutral:           10
    House Baratheon:   10
    House Martell:     10
    House Greyjoy:     8
    House Stark:       8
    House Tyrell:      7
    The Night's Watch: 6

    Total count: 88

Find all 1 cost characters and get a breakdown of their trait and icon spread.

    $ thronescli --cost 1 -t char --count icon --count trait
    Dragonstone Faithful: Baratheon. Character. 1 Cost. 1 STR. P.
    Iron Islands Fishmonger: Greyjoy. Character. 1 Cost. 1 STR. P.
    Lannisport Merchant: Lannister. Character. 1 Cost. 1 STR. P.
    Desert Scavenger: Martell. Character. 1 Cost. 1 STR. P.
    Messenger Raven: Loyal. Thenightswatch. Character. 1 Cost. 1 STR. No Icons.
    Steward at the Wall: Thenightswatch. Character. 1 Cost. 1 STR. I.
    Winterfell Steward: Stark. Character. 1 Cost. 1 STR. P.
    Viserys Targaryen: Unique. Loyal. Targaryen. Character. 1 Cost. 1 STR. P.
    Targaryen Loyalist: Targaryen. Character. 1 Cost. 1 STR. P.
    Garden Caretaker: Tyrell. Character. 1 Cost. 1 STR. P.
    Bronn: Unique. Lannister. Character. 1 Cost. 5 STR. M.
    Rickon Stark: Unique. Stark. Character. 1 Cost. 1 STR. No Icons.
    Builder at the Wall: Thenightswatch. Character. 1 Cost. 1 STR. P.
    Planky Town Trader: Martell. Character. 1 Cost. 1 STR. P.

    [ Trait counts ]

    Ally:      8
    Steward:   3
    Merchant:  2
    Lord:      2
    Builder:   1
    Mercenary: 1
    Raven:     1

    [ Icon counts ]

    Power:    10
    Military: 1
    Intrigue: 1

    Total count: 14

Credits
-------

* All card data is copyright by [Fantasy Flight Games](https://www.fantasyflightgames.com/).
* All card data is provided by [thronesdb.com](http://thronesdb.com/).
* Thrones CLI is written by [Petter Nyström](mailto:jimorie@gmail.com).
