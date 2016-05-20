"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: ZODB utilities

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""

import os
import ZODB, ZODB.FileStorage


def open_zodb(config=None, read_only=False):
    "Opens a Zope database and returns a root object. If config not specified get_config() is used."

    if config is None:
        from talkofactadb.config import get_config
        config = get_config()
    storage = ZODB.FileStorage.FileStorage(os.path.join(config.zodb_dir, 'zodb.fs'), read_only=read_only)
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root
    return root
