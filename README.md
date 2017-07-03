Thrones CLI
===========

A command line interface for the [thronesdb.com](http://thronesdb.com/) card database for [A Game of Thrones LCG 2nd Ed](https://www.fantasyflightgames.com/en/products/a-game-of-thrones-the-card-game-second-edition/).

Install
-------

Thrones CLI can be installed from [PyPI](https://pypi.python.org/pypi/thronescli) using pip:

    sudo pip install thronescli

Or you can just download the Python script [here on GitHub](https://raw.githubusercontent.com/jimorie/thronescli/master/thronescli/thronescli.py).

Why?
----

Thrones CLI offers one (and only one) feature not found on [thronesdb.com](http://thronesdb.com/) and that is the --count option. The --count option gives you a card count breakdown based on a given field for the found cards.

For example you can quickly find the best factions to use [Street of Silk](http://thronesdb.com/card/02118) with:

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

Or find out what are the most common traits and icons on characters with renown:

    $ thronescli --text Renown. --case --count trait --count icon --count-only
    Icon counts
    Military: 27
    Power:    26
    Intrigue: 8

    Trait counts
    Lord:          20
    Knight:        6
    King:          5
    Ironborn:      5
    Small Council: 3
    Lady:          2
    Captain:       2
    Queen:         1
    House Tarly:   1
    Kingsguard:    1
    House Tully:   1
    Ally:          1
    Raider:        1
    Ranger:        1
    Companion:     1
    House Clegane: 1
    House Frey:    1
    House Uller:   1
    Dothraki:      1
    Wildling:      1
    R'Hllor:       1

    Total count: 28

Credits
-------

Thrones CLI was written by Petter Nyström &lt;jimorie@gmail.com&gt;.
