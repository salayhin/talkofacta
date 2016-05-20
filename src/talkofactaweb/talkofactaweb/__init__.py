"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: Visualization webapp

Launch the built-in debug webserver

  Usage:
      talkofeurope-web [-h] [--log-config=<file.cfg>] run

  Options:
      -h                        Show this screen
      --log-config=<file.cfg>   Specify the logging configuration file.

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""
import logging.config
from docopt import docopt

def main():
    args = docopt(__doc__)
    if args['--log-config'] is not None:
        logging.config.fileConfig(args['--log-config'])
    else:
        logging.basicConfig(level=logging.DEBUG)
    from .main import app
    app.run(host=app.config['DEBUG_SERVER_HOST'], port=app.config['DEBUG_SERVER_PORT'])
