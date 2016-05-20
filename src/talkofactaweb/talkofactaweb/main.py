"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: Visualization webapp
Main module.

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""

from flask import Flask
import logging, os
log = logging.getLogger('talkofactaweb')

# ------------ Configuration ------------- #
app = Flask(__name__)
app.config.from_object('talkofactaweb.config.Config')
# Load optional config from $CONFIG
if os.getenv('CONFIG', None) is not None:
    variables = {}
    execfile(os.getenv('CONFIG', None), {}, variables)
    for k in variables:
        if type(variables[k]) != type(os):     # Don't add modules
            app.config[k] = variables[k]

# ------------ DB ------------- #
from .model import db
db.init_app(app)

# ------------ Web ------------- #
from . import views


# ----------- Interface with PasteDeploy ----- #
def app_factory(global_config, **local_conf):
    return app.wsgi_app
