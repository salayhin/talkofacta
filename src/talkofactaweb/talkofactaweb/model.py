"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: Visualization webapp
Model.

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
from sqlalchemy import *
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
Base = db.Model

# All tables defined here will share those columns
class SignificantWordTableMixin(object):
    id = Column(Integer, primary_key=True)
    foreground_group_name = Column(String, nullable=False)
    background_group_name = Column(String, nullable=False)
    word = Column(Unicode(200), nullable=False, index=True)
    pval = Column(Numeric, nullable=False)
    odds = Column(Numeric, nullable=False)

class ByHansard(Base, SignificantWordTableMixin):
    __tablename__ = 'words_byhansard'

class ByMonth(Base, SignificantWordTableMixin):
    __tablename__ = 'words_bymonth'

class BySpeaker(Base, SignificantWordTableMixin):
    __tablename__ = 'words_byspeaker'
