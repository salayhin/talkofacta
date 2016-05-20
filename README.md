Talk of Europe: Significant words
=================================

This repository contains the source code of the [project](http://europe.all.my) developed during the
[Talk of Europe (ToE) Creative Camp #2](http://www.talkofeurope.eu/creativecamp2/call-for-participation/) (23-27 March 2015, Amsterdam)
by Konstantin Tretyakov, Ilya Kuzovkin & Alexander Tkachenko.

The aim of the project was to extract words, *significantly overrepresented* in the speeches of representatives of particular countries,
or at particular timepoints. [Fisher exact test](http://en.wikipedia.org/wiki/Fisher%27s_exact_test) was used to measure overrepresentation.
Results were visualized as wordclouds, served via an interactive web application.

The application is hosted live (as of April 2015) on [http://europe.all.my](http://europe.all.my). This repository contains the source code
of the scripts used to compute the results and of the visualization web application.

Project structure
-----------------

The project's code consists of three parts, each contained in a separate python package.

  * ``talkofeuropedb`` -- scripts for exporting the necessary ToE data (i.e. English texts) from [LinkedPolitics RDF files](http://linkedpolitics.ops.few.vu.nl/browse/list_graphs) into tabular (relational) format.
  * ``talkofeuropewords`` -- scripts for performing the core analysis, i.e. extracting significant words for various groupings. Final results are stored in a relational database.
  * ``talkofeuropeweb`` -- Flask-based application for visualizing results. Uses data produced by scripts from ``talkofeuropewords``.

The source code of the packages is available under ``src/`` subdirectory.


Preparation
-----------
We use [Buildout](https://pypi.python.org/pypi/zc.buildout/2.3.1) for build management. If ``zc.buildout`` is already installed in your
Python system, you can prepare the project by running:

    $ buildout

Otherwise, do:

    $ python bootstrap.py
    $ bin/buildout

If all goes well, all the necessary scripts will be installed into the ``bin/`` subdirectory.


Recomputing the results
-----------------------
In order to recompute the results (which is not really necessary, in fact, as those are provided in the repository),
you will need to run through a sequence of steps. This sequence of steps is listed in the ``compute_results.sh``
bash script. Before those are run, you need to specify appropriate configuration settings. Edit (or copy) the
``sample_config.py`` file, and set up the ``CONFIG`` environment variable to point to the resulting configuration file.

    $ cp sample_config.py my_config.py
    ... edit my_config.py ...
    $ export CONFIG=$PWD/my_config.py
    $ ./compute_results.sh

If all goes well (which is not guaranteed as the ``compute_results.sh`` script is more of a "action transcript"
rather than a script that is really meant to be run without supervision), the results will appear in the SQLite
file ``data/resultsdb.sqlite`` (unless you changed the corresponding setting in ``my_config.py``, of course).


Running the web application
---------------------------
The package ``talkofeuropeweb`` is a self-contained Flask web application. It contains all the computed data necessary for
visualization (in a SQLite file stored in its data directory) and does not depend on the two "computation" packages. The application can be launched in debug mode by running

    $ bin/talkofeurope-web run

Alternatively, you may use any WSGI container to serve the application, such as GUnicorn:

    $ bin/gunicorn -b 0.0.0.0:33333 talkofeuropeweb.main:app

or PasteDeploy:

    $ bin/paster serve sample_pasteconfig.ini

or

    $ bin/gunicorn --paste sample_pasteconfig.ini

etc.

Copyright & License
-------------------

  * Copyright 2015, [Konstantin Tretyakov](http://kt.era.ee/), [Ilya Kuzovkin](http://ikuz.eu), Alexander Tkachenko
  * License: MIT

  * The project relies on a multitude of other Python and Javascript packages.
     * For a list of Python packages used see ``buildout.cfg``
     * The ``talkofeuropeweb`` application includes the following packages as part of its source code:
       [D3.js](https://github.com/jasondavies/d3-cloud), [C3.js](http://c3js.org/), [ColorBrewer](http://colorbrewer2.org/),
       [D3-cloud](https://github.com/jasondavies/d3-cloud) (with some modifications), [JQuery](https://jquery.com/),
       [JQuery UI](https://jqueryui.com/), [JQuery UI Slider Pips](http://simeydotme.github.io/jQuery-ui-Slider-Pips/),
       [Modernizr](http://modernizr.com/), [Bootstrap](http://getbootstrap.com/),
       [Flag-icon-css](https://github.com/lipis/flag-icon-css).
  * All those packages are subject to their own licenses (all are openly licensed, though).
