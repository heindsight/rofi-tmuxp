==========
Rofi TmuxP
==========

.. pull-quote::

   Use Rofi_ to launch tmuxp_ sessions.

.. image:: https://img.shields.io/pypi/v/rofi-tmuxp.svg
    :target: https://pypi.org/project/rofi-tmuxp/

.. image:: https://img.shields.io/pypi/pyversions/rofi-tmuxp.svg
    :target: https://pypi.org/project/rofi-tmuxp/

.. image:: https://img.shields.io/pypi/format/rofi-tmuxp.svg
    :target: https://pypi.org/project/rofi-tmuxp/

.. image:: https://github.com/heindsight/rofi-tmuxp/actions/workflows/test.yaml/badge.svg?branch=develop
    :target: https://github.com/heindsight/rofi-tmuxp/actions/workflows/test.yaml?query=branch%3Adevelop

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

Installation
------------

.. code-block:: shell

   $ pip install rofi-tmuxp

Note
````

The ``rofi-tmuxp`` script uses the `tmuxp python API`_ to find your tmuxp
session config files. This means that you should install it in the same Python
environment as tmuxp.

Usage
-----

Without any command-line arguments, ``rofi-tmuxp`` will print out a list of
tmuxp session names to standard output. If a session name is passed as an
argument, it will attempt to launch that session in a new terminal.

To use with ``rofi``, you will need to add ``rofi-tmuxp`` as a "script" mode to
you rofi config file.  E.g.

.. code-block::

   configuration {
       /* Enable run and tmuxp modes */
       modi: "run,tmuxp:rofi-tmuxp";
   }

Then you can run rofi like:

.. code-block:: shell

   rofi -show tmuxp

License
-------

Copyright (c) Heinrich Kruger. Distributed under the `MIT license`_.


.. _Rofi: https://github.com/davatorium/rofi
.. _tmuxp: http://tmuxp.git-pull.com/
.. _tmuxp python API: https://tmuxp.git-pull.com/en/latest/api.html
.. _MIT license: https://github.com/heindsight/rofi-tmuxp/blob/master/LICENSE
