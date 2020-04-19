.. highlight:: console

============
Installation
============


Stable release
--------------

To install telegram-upload, run these commands in your terminal:

.. code-block:: console

    $ sudo pip3 install -U telegram-upload

This is the preferred method to install telegram-upload, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Other releases
--------------
You can install other versions from Pypi using::

    $ pip install telegram-upload==<version>

For versions that are not in Pypi (it is a development version)::

    $ pip install git+https://github.com/Nekmo/telegram-upload.git@<branch>#egg=telegram_upload


If you do not have git installed::

    $ pip install https://github.com/Nekmo/telegram-upload/archive/<branch>.zip
