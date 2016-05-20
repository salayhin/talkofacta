"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: Visualization webapp
Config.

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
import os

class Config(object):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    
    # Deployment option
    APPLICATION_ROOT = '/'  # Untested
    DEBUG_SERVER_HOST = '0.0.0.0'
    DEBUG_SERVER_PORT = 5000

    # Database connection
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'resultsdb.sqlite')
