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

```console
$ thronescli --help
Usage: thronescli [OPTIONS] [TEXT]...

Options:
  --update       Update card database
  -v, --verbose  Show more data.
  --brief        Show one line of data, regardless the level of verbose.
  --long         Show multiple lines of data, regardless the level of verbose.
  --show FIELD   Show given field only. Can be repeated to show multiple
                 fields in given order.
  --case         Use case sensitive filtering.
  --exact        Use exact match filtering.
  --regex        Use regular rexpressions when filtering.
  --or FIELD     Treat multiple tests for given field with logical
                 disjunction, i.e. OR-logic instead of AND-logic.
  --inclusive    Treat multiple tests for different fields with logical
                 disjunction, i.e. OR-logic instead of AND-logic.
  --sort FIELD   Sort results by given field.
  --desc         Sort results in descending order.
  --group FIELD  Group results by given field.
  --count FIELD  Print a breakdown of all values for given field.
  --version      Show the version and exit.
  --help         Show this message and exit.

Field filters:
  -n, --name TEXT         Filter on matching name.
  --trait TEXT            Filter on matching traits.
  -x, --text TEXT         Filter on matching text.
  --keyword TEXT          Filter on matching keywords.
  --unique                Filter on unique.
  --non-unique            Filter on non-unique.
  --loyal                 Filter on loyal.
  --non-loyal             Filter on non-loyal.
  -f, --faction FACTION   Filter on matching faction.
  --faction-isnt FACTION  Filter on non-matching faction.
  -t, --type TYPE         Filter on matching type.
  --type-isnt TYPE        Filter on non-matching type.
  --cost NUMBER           Filter on matching cost (number comparison).
  --str NUMBER            Filter on matching str (number comparison).
  --icon ICON             Filter on having given icon.
  --icon-isnt ICON        Filter on not having given icon.
  --claim NUMBER          Filter on matching claim (number comparison).
  --income NUMBER         Filter on matching income (number comparison).
  --initiative NUMBER     Filter on matching initiative (number comparison).
  --reserve NUMBER        Filter on matching reserve (number comparison).
  --illustrator TEXT      Filter on matching illustrator.
  --set TEXT              Filter on matching set.

Where:
  FACTION  One of: baratheon, gj, greyjoy, lannister, martell, neutral,
           night's watch, nw, stark, targaryen, the night's watch, tyrell.
  FIELD    One of: claim, cost, faction, icons, illustrator, income,
           initiative, keywords, loyal, name, reserve, set, str, text, traits,
           type, unique.
  ICON     One of: military, intrigue, power. A combination of the letters
           'MIP' can be used to define multiple respective icons.
  NUMBER   A number optionally prefixed by one of the supported comparison
           operators: ==, =, !=, !, <=, <, >=, >. With == being the default if
           only a number is given.
  TEXT     A text partially matching the field value. The --case, --regex and
           --exact options can be applied. If prefixed with ! the match is
           negated.
  TYPE     One of: agenda, attachment, character, event, location, plot,
           title.
```

Examples
--------

Find a card by its name:

```console
$ thronescli Asha
Asha Greyjoy: Unique. House Greyjoy. Character. 5 Cost. 4 STR. M P.
Asha Greyjoy: Unique. Loyal. House Greyjoy. Character. 7 Cost. 5 STR. M I P.
Asha Greyjoy: Unique. House Greyjoy. Character. 6 Cost. 5 STR. M P.

Total count: 3
```

Print more of the cards' information:

```console
$ thronescli Asha -v
Asha Greyjoy
Ironborn. Lady.
Stealth.
Reaction: After you win an unopposed challenge in which Asha Greyjoy is participating, stand her.
Unique: Yes
Loyal: No
Faction: House Greyjoy
Type: Character
Cost: 5
STR: 4
Icons: M P

Asha Greyjoy
Captain. Ironborn. Lady.
Pillage. Stealth.
Reaction: After Asha Greyjoy discards a card using pillage, search the top X cards of your deck for a card and add it to your hand. Shuffle your deck. X is the number of cards in the losing opponent's
discard pile.
Unique: Yes
Loyal: Yes
Faction: House Greyjoy
Type: Character
Cost: 7
STR: 5
Icons: M I P

Asha Greyjoy
Captain. Ironborn. Lady.
Pillage. Stealth.
Each other unique Ironborn character you control gains stealth.
Unique: Yes
Loyal: No
Faction: House Greyjoy
Type: Character
Cost: 6
STR: 5
Icons: M P

Total count: 3
```

Find all Greyjoy characters with an intrigue icon, grouped by STR:

```console
$ thronescli -f gj --icon i --group str
[ 1 STR ]

Lordsport Shipwright: House Greyjoy. Character. 2 Cost. 1 STR. I.
The Reader's Septon: House Greyjoy. Character. 2 Cost. 1 STR. I P.
Harlaw Scout: House Greyjoy. Character. 2 Cost. 1 STR. M I.

[ 2 STR ]

Alannys Greyjoy: Unique. House Greyjoy. Character. 3 Cost. 2 STR. I P.
Priest of the Drowned God: House Greyjoy. Character. 3 Cost. 2 STR. I P.
Esgred: Unique. House Greyjoy. Character. 5 Cost. 2 STR. M I P.
Wex Pyke: Unique. House Greyjoy. Character. 2 Cost. 2 STR. M I.
Drowned God Fanatic: Loyal. House Greyjoy. Character. 3 Cost. 2 STR. M I.
Maester Murenmure: Unique. House Greyjoy. Character. 3 Cost. 2 STR. I P.
Old Grey Gull: Unique. Loyal. House Greyjoy. Character. 3 Cost. 2 STR. I P.
Drowned God Fanatic: Loyal. House Greyjoy. Character. 3 Cost. 2 STR. M I.
Cragorn: Unique. House Greyjoy. Character. 2 Cost. 2 STR. I.

[ 3 STR ]

Drowned God's Apostle: House Greyjoy. Character. 4 Cost. 3 STR. I P.
Aeron Damphair: Unique. Loyal. House Greyjoy. Character. 5 Cost. 3 STR. I P.
Hotho Humpback: Unique. House Greyjoy. Character. 4 Cost. 3 STR. I P.
Left-Hand Lucas Codd: Unique. House Greyjoy. Character. 4 Cost. 3 STR. M I.
Ralf Kenning: Unique. Loyal. House Greyjoy. Character. 4 Cost. 3 STR. M I.

[ 4 STR ]

The Reader: Unique. Loyal. House Greyjoy. Character. 5 Cost. 4 STR. I P.
Aeron Damphair: Unique. House Greyjoy. Character. 6 Cost. 4 STR. I P.
Tarle the Thrice-Drowned: Unique. Loyal. House Greyjoy. Character. 5 Cost. 4 STR. I P.
Euron Crow's Eye: Unique. Loyal. House Greyjoy. Character. 6 Cost. 4 STR. M I P.
Alannys Greyjoy: Unique. Loyal. House Greyjoy. Character. 5 Cost. 4 STR. I P.
King's Landing Proselyte: House Greyjoy. Character. 4 Cost. 4 STR. I P.
Euron Crow's Eye: Unique. Loyal. House Greyjoy. Character. 6 Cost. 4 STR. M I P.
Dagmer Cleftjaw: Unique. House Greyjoy. Character. 5 Cost. 4 STR. M I.

[ 5 STR ]

Asha Greyjoy: Unique. Loyal. House Greyjoy. Character. 7 Cost. 5 STR. M I P.
Tarle the Thrice-Drowned: Unique. Loyal. House Greyjoy. Character. 6 Cost. 5 STR. I P.

[ 6 STR ]

Euron Crow's Eye: Unique. Loyal. House Greyjoy. Character. 7 Cost. 6 STR. M I P.

Total count: 28
```

Find all non-limited income providing cards:

```console
$ thronescli --text "\+\d+ Income" --text "!Limited" --regex
Littlefinger: Unique. Neutral. Character. 5 Cost. 4 STR. I P.
Tywin Lannister: Unique. Loyal. House Lannister. Character. 7 Cost. 6 STR. M I P.
Paxter Redwyne: Unique. Loyal. House Tyrell. Character. 4 Cost. 3 STR. I.
Master of Coin: Neutral. Title.
The God's Eye: Unique. Neutral. Location. 3 Cost.
Shield of Lannisport: Unique. Loyal. House Lannister. Attachment. 3 Cost.
Mace Tyrell: Unique. Loyal. House Tyrell. Character. 6 Cost. 4 STR. I P.
Northern Armory: Loyal. House Stark. Location. 2 Cost.
Stormlands Fiefdom: Loyal. House Baratheon. Location. 2 Cost.
Tycho Nestoris: Unique. Neutral. Character. 6 Cost. 3 STR. P.
Miner's Pick: Loyal. The Night's Watch. Attachment. 1 Cost.
Gold Mine: Loyal. House Lannister. Location. 2 Cost.
Summer Sea Port: Loyal. House Martell. Location. 2 Cost.
Tithe Collector: House Lannister. Character. 3 Cost. 3 STR. I.
Meereenese Market: Loyal. House Targaryen. Location. 2 Cost.
Refurbished Hulk: Loyal. House Greyjoy. Location. 2 Cost.
Arbor Marketplace: Loyal. House Tyrell. Location. 2 Cost.
Knights of the Hollow Hill: Neutral. Agenda.
The Red Keep: Unique. House Lannister. Location. 4 Cost.
The Red Keep: Unique. House Lannister. Location. 4 Cost.
Ser Harys Swyft: Unique. House Lannister. Character. 4 Cost. 4 STR. P.
Fair Isle: Unique. Loyal. House Lannister. Location. 3 Cost.
The Green Fork: Unique. Neutral. Location. 2 Cost.
Garth Greenhand: Unique. Loyal. House Tyrell. Attachment. 3 Cost.

Total count: 24
```

Find the best faction for using [Street of Silk](http://thronesdb.com/card/02118):

```console
$ thronescli --trait ally --trait companion --or trait --count faction
[ Faction counts ]

House Targaryen:   29
Neutral:           27
House Lannister:   22
House Martell:     16
House Baratheon:   14
The Night's Watch: 14
House Stark:       14
House Tyrell:      12
House Greyjoy:     11

Total count: 159
```

Find all 1 cost characters and get a breakdown of their trait and icon spread.

```console
$ thronescli --cost 1 -t char --count icon --count trait
[ Icons counts ]

Power:       13
Intrigue:    7
Military:    3

[ Traits counts ]

Ally:        13
Steward:     4
Merchant:    3
Raven:       2
Lord:        2
Mercenary:   2
Companion:   2
Builder:     1
Maester:     1
Fool:        1
House Frey:  1
House Arryn: 1
Recruit:     1

Total count: 24
```

Credits
-------

* All card data is copyright by [Fantasy Flight Games](https://www.fantasyflightgames.com/).
* All card data is provided by [thronesdb.com](http://thronesdb.com/).
* Thrones CLI is written by [Petter Nyström](mailto:jimorie@gmail.com).
