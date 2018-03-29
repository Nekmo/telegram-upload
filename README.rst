###############
telegram-upload
###############


.. image:: https://img.shields.io/travis/Nekmo/telegram-upload.svg?style=flat-square&maxAge=2592000
  :target: https://travis-ci.org/Nekmo/telegram-upload
  :alt: Latest Travis CI build status

.. image:: https://img.shields.io/pypi/v/telegram-upload.svg?style=flat-square
  :target: https://pypi.org/project/telegram-upload/
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/telegram-upload.svg?style=flat-square
  :target: https://pypi.org/project/telegram-upload/
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/github/Nekmo/telegram-upload.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/telegram-upload
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/telegram-upload/master.svg?style=flat-square
  :target: https://codecov.io/github/Nekmo/telegram-upload
  :alt: Test coverage

.. image:: https://img.shields.io/requires/github/Nekmo/telegram-upload.svg?style=flat-square
     :target: https://requires.io/github/Nekmo/telegram-upload/requirements/?branch=master
     :alt: Requirements Status


Upload large files to Telegram using your account


To **install telegram-upload**, run this command in your terminal:

.. code-block:: console

    $ sudo pip install telegram-upload

This is the preferred method to install telegram-upload, as it will always install the most recent stable release.

To use this program you need an Telegram account and your *App api_id/api_hash* (get it in
`my.telegram.org <https://my.telegram.org/>`). The first time you use telegram-upload it requests your telephone,
api_id and api_hash. To **send files**:

.. code-block:: console

    $ telegram-upload file1.mp4 /path/to/file2.mkv


Features
========

* Send multiples files (up to 1.5GiB per file)
* Add video thumbs
* Delete local file on success

