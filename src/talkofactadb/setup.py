#! /usr/bin/env python
"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: DB package

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
from setuptools import setup, find_packages

setup(
    name='talkofactadb',
    description='Talk of ACTA - Fork of https://github.com/konstantint/talkofeurope-wordclouds adapted to an ACTA dataset',
    version='0.1',
    author='Konstantin Tretyakov, Ilya Kuzovkin, Aleksandr Tkachenko',
    license='MIT',
    author_email='kt@ut.ee',
    packages=find_packages(),
    install_requires=['docopt', 'SQLAlchemy', 'rdflib', 'requests', 'clint'],
    entry_points={
        'console_scripts': [
          'test_config = talkofactadb.config:test_config',
          'csv2db = talkofactadb.scripts.csv2db:main',
         ]
    }
)
