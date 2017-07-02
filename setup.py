# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = 'thronescli',
    packages = ['thronescli'], # this must be the same as the name above
    version = '0.1',
    description = 'A command line interface for looking up cards for A Game of Thrones LCG 2n Ed.',
    author = 'Petter Nyström',
    author_email = 'jimorie@gmail.com',
    url = 'https://github.com/jimorie/thronescli', # use the URL to the github repo
    download_url = 'https://github.com/jimorie/thronescli/archive/0.1.tar.gz', # I'll explain this in a second
    keywords = ['game of thrones', 'thrones', 'thronesdb.com'], # arbitrary keywords
    classifiers = [],
    install_requires = [
        'click'
    ]
)
