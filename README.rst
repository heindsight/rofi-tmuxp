==========
Rofi TmuxP
==========

Use Rofi_ to launch tmuxp_ sessions.

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

   rofi.modi: run,ssh,tmuxp:rofi-tmuxp

Then you can run rofi like:

.. code-block:: shell

   rofi -show tmuxp

License
-------

Copyright (c) Heinrich Kruger. Distributed under the `MIT license`_.


.. _Rofi: https://github.com/davatorium/rofi
.. _tmuxp: http://tmuxp.git-pull.com/
.. _tmuxp python API: https://tmuxp.git-pull.com/en/latest/api.html
.. _MIT license: LICENSE
