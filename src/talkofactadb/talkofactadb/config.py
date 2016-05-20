"""
Talk of Europe Creative Camp #2 :: Wordcloud project :: config

The configuration for ToE scripts is specified by setting an environment
variable $CONFIG to point to a .py file specifying values for config variables.

The get_config function reads this files and returns all values as attributes
of a Config object.

The test_config script writes out the values for the known parameter values.

  Usage: test-config [-h]

Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Alexander Tkachenko.
License: MIT
"""

import os
from docopt import docopt


class Config:
    """
    Config object. Set the environment variable CONFIG to point to a
    python file with configuration options. Use get_config to load them and populate as
    attributes of a Config object.
    """
    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        else:
            raise Exception("Parameter %s not specified in your $CONFIG!" % name)


def get_config():
    config_name = os.getenv('CONFIG', None)
    if config_name is None:
        raise Exception("Please, specify the CONFIG variable")
    c = Config()
    variables = {}
    execfile(config_name, {}, variables)
    for k in variables:
        if type(variables[k]) != type(os):     # Don't add modules
            setattr(c, k, variables[k])
    return c


def test_config():
    args = docopt(__doc__)
    c = get_config()
    print "Configuration file: "
    print "   " + os.getenv('CONFIG')
    print "-"*(3 + len(os.getenv('CONFIG')))
    for k, v in c.__dict__.iteritems():
        print k, "\t=\t", v
