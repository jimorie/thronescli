# -*- coding: utf-8 -*-

from setuptools import setup
from thronescli.thronescli import __version__ as version

setup(
    name='thronescli',
    packages=['thronescli'],  # this must be the same as the name above
    version=version,
    description='A command line interface for the thronesdb.com card database.',
    author='Petter Nyström',
    author_email='jimorie@gmail.com',
    url='https://github.com/jimorie/thronescli',  # use the URL to the github repo
    download_url='https://github.com/jimorie/thronescli/archive/v{}.tar.gz'.format(version),
    keywords=['game of thrones', 'thrones', 'thronesdb.com'],  # arbitrary keywords
    classifiers=[],
    install_requires=[
        'click',
        'titlecase'
    ],
    entry_points={
        'console_scripts': [
            'thronescli=thronescli.thronescli:main'
        ]
    }
)
