"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: SQLAlchemy model

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def _saobject_repr(self):
    s = [self.__class__.__name__, '\n']
    for c in self.__class__.__table__.columns:
        s.extend(['\t', c.name, ': ', unicode(getattr(self, c.name)).encode('utf-8'), '\n'])
    return ''.join(s)


def _saobject_as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def _saobject_as_tuple(self):
    return tuple([getattr(self, n.name) for n in self.__table__.columns])


Base.__repr__ = _saobject_repr
Base._as_dict = _saobject_as_dict
Base._as_tuple = _saobject_as_tuple


class Speech(Base):
    __tablename__ = 'speech'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    speaker_uri = Column(Unicode(200), nullable=False, index=True)
    hansard = Column(String(3), nullable=False, index=True)
    speech = Column(Unicode, nullable=False)


def open_db(db_url = None):
    "Returns an initialized Session object. If db_url is not specified, uses get_config().db_url"
    if db_url is None:
        from talkofactadb.config import get_config
        db_url = get_config().db_url
    e = create_engine(db_url)
    Session = sessionmaker(e)
    return Session()

