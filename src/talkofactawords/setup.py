#!/usr/bin/env python
"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: Words package

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""

from setuptools import setup, find_packages

setup(
    name = 'talkofactawords',
    description = 'Talk of ACTA - Fork of https://github.com/konstantint/talkofeurope-wordclouds adapted to an ACTA dataset',
    version = '0.1',
    install_requires = ['talkofactadb', 'python-dateutil', 'requests', 'textblob', 'ZODB', 'docopt', 'clint', 'unidecode'],
    author = 'Konstantin Tretyakov, Ilya Kuzovkin, Aleksandr Tkachenko',
    license = 'MIT',
    author_email = 'kt@ut.ee',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
          'compute_features = talkofactawords.scripts.compute_features:main',
          'collect_words = talkofactawords.scripts.collect_words:main',
          'extract_significant_features = talkofactawords.scripts.extract_significant_features:main',
         ]
    }
)
