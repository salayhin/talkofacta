"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: results database model
The results of the analysis (i.e. overrepresented words) are written out into a
relational database according to this model.

Note that we use some SQLAlchemy tricks to support several tables with different names
but the same schema.
See http://docs.sqlalchemy.org/en/rel_0_8/orm/extensions/declarative.html#augmenting-the-base
and

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class DynamicTableNameBase(object):
    @declared_attr
    def __tablename__(cls):
        return 'words_' + cls.__name__.lower()

Base = declarative_base(cls=DynamicTableNameBase)


def create_db(db_url, drop_tables=False):
    e = create_engine(db_url)
    if drop_tables:
        Base.metadata.drop_all(e)
    Base.metadata.create_all(e)


# All tables defined here will share those columns
class SignificantWordTableMixin(object):
    id = Column(Integer, primary_key=True)
    foreground_group_name = Column(String, nullable=False)
    background_group_name = Column(String, nullable=False)
    word = Column(Unicode(200), nullable=False, index=True)
    pval = Column(Numeric, nullable=False)
    odds = Column(Numeric, nullable=False)

    @declared_attr
    def __table_args__(cls):
        return (Index('ix_%s' % cls.__tablename__, 'foreground_group_name', 'background_group_name'),)


# The classes below define actual tables. They differ only in the table names
# The table name is determined automatically from class name by a method in DynamicTableNameBase
class ByHansard(Base, SignificantWordTableMixin):
    pass

class ByMonth(Base, SignificantWordTableMixin):
    pass

class BySpeaker(Base, SignificantWordTableMixin):
    pass
