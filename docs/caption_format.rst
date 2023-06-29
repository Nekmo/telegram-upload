
.. _caption_format:

Caption format
==============
Telegram-upload has a argument to add a message with every file you send. This is the **caption argument**. The
caption argument (``--caption "<message>"``) can be personalized for every file you send using variables between braces
(``{}``). The variables are replaced with the corresponding value when the file is sent. The following variables are
available:

* ``{file}``: file object. This variable has a lot of attributes available.
* ``{now}``: current datetime.

For example:

.. code-block:: bash

    $ telegram-upload --caption "This is a file with name {file.name}" file.txt

The latest caption message will be *"This is a file with name file.txt"*. In case of using a invalid variable, the
variable will be keep without replacing. The rest of variables will be replaced correctly. In case of a sintax error
the entire caption will be keep without replacing.

The caption variables can be Python attributes of the ``{file}`` & ``{now}`` objects. Some methods without arguments are
available too. In case of accesing to a unsupported method, the variable will be keep without replacing. The private
attributes are prohibited for security reasons.

For testing the caption variables before sending the file, you can use the next command:

.. code-block:: bash

    $ python -m telegram_upload.caption_formatter file.txt "{file.absolute}"

We recommend you to use the latest command to test the caption variables before sending the file.

If you need to use a brace in the caption, you can escape it using two braces. For example: ``{{ {file.name} }}`` will
be replaced with ``{ file.txt }``.

The available attributes are described below.


Path attributes
---------------
The ``{file}`` variable has all the attributes of the ``pathlib.Path`` object. The following attributes are the most
used:

* ``{file.name}``: file name with extension. For example ``file.txt``.
* ``{file.stem}``: file name without extension. For example ``file``.
* ``{file.suffix}``: file extension including the period. For example ``.txt``.
* ``{file.parent}``: parent directory of the file. For example ``/home/user``.

The next methods are available too:

* ``{file.absolute}``: absolute path of the file. For example ``/home/user/file.txt``.
* ``{file.home}``: home directory of the user. For example ``/home/user``.

The next methods are added or modified:

* ``{file.relative}``: relative path of the file. For example ``file.txt``.
* ``{file.mediatype}``: media type of the file. For example ``text/plain``.
* ``{file.preffixes}``: all preffixes of the file. For example ``.tar.gz`` for ``file.tar.gz``.

The entire list of attributes and methods can be found in the
`pathlib.Path documentation <https://docs.python.org/3/library/pathlib.html#>`_


File size
---------
The ``{file}`` variable has the ``{file.size}`` to get the file size. The size is returned in bytes. The size attribute
has other attributes to get the size in other units. The following attributes are available:

* ``{file.size}``: file size in bytes.
* ``{file.size.as_kibibytes}``: file size in kibibytes (KiB).
* ``{file.size.as_mebibytes}``: file size in mebibytes (MiB).
* ``{file.size.as_gibibytes}``: file size in gibibytes (GiB).
* ``{file.size.as_kilobytes}``: file size in kilobytes (KB).
* ``{file.size.as_megabytes}``: file size in megabytes (MB).
* ``{file.size.as_gigabytes}``: file size in gigabytes (GB).
* ``{file.size.for_humans}``: file size in a human readable format. For example ``1.2 MiB``.

If you don't know what is the difference between a kibibyte and a kilobyte, you can read the Wikipedia article about
`binary prefixes <https://en.wikipedia.org/wiki/Byte#Multiple-byte_units>`_. We recommend to use the binary prefixes
(``KiB``, ``MiB``, ``GiB``...) because they are the correct units for binary files.


Media attributes
----------------
The ``{file}`` variable has the ``{file.media}`` to get the media attributes. The media attributes are extracted from
the video and audio files. The following attributes are available:

* ``{file.media.width}``: width of the video in pixels *(only for video files)*.
* ``{file.media.height}``: height of the video in pixels *(only for video files)*.
* ``{file.media.title}``: title of the media. This is extracted from the metadata of the file.
* ``{file.media.artist}``: artist of the media *(only for audio files)*.
* ``{file.media.album}``: album of the media *(only for audio files)*.
* ``{file.media.producer}``: producer of the media.
* ``{file.media.duration}``: duration of the media in seconds.

The duration attribute has other attributes to get the duration in other units. The following attributes are available:

* ``{file.media.duration.as_minutes}``: duration of the media in minutes.
* ``{file.media.duration.as_hours}``: duration of the media in hours.
* ``{file.media.duration.as_days}``: duration of the media in days.
* ``{file.media.duration.for_humans}``: duration of the media in a human readable format. For example ``1 hour and 30 minutes``. The text is in English.

Notice that some of the attributes will not be available if the file doesn't have the metadata. Some video & audio
doesn't have the metadata. The metadata is extracted using the
`hachoir library <https://hachoir.readthedocs.io/en/latest/>`_


Datetime attributes
-------------------
The file object has the following attributes to get the datetimes of the file:

* ``{file.ctime}``: datetime when the file was created.
* ``{file.mtime}``: datetime when the file was modified.
* ``{file.atime}``: datetime when the file was accessed.

By default the datetime is returned like ``YYYY-MM-DD HH:MM:SS.mmmmmm``. The datetime attribute has other attributes to
get the datetime in other formats. All the attributes from the ``datetime.datetime`` object are available. The following
attributes are the most used:

* ``{file.ctime.day}``: day of the month. For example ``1``.
* ``{file.ctime.month}``: month of the year. For example ``11``.
* ``{file.ctime.year}``: year. For example ``2019``.
* ``{file.ctime.hour}``: hour of the day. For example ``14``.
* ``{file.ctime.minute}``: minute of the hour. For example ``30``.
* ``{file.ctime.second}``: second of the minute. For example ``0``.

The next methods are available too:

* ``{file.ctime.astimezone}``: datetime with timezone. For example ``2019-11-01 14:30:00+01:00``.
* ``{file.ctime.ctime}``: datetime in ctime format. For example ``Fri Nov  1 14:30:00 2019``.
* ``{file.ctime.date}``: date in ISO 8601 format. For example ``2019-11-01``.
* ``{file.ctime.dst}``: dst of the tzinfo datetime.
* ``{file.ctime.isoformat}``: datetime in ISO 8601 format. For example ``2019-11-01T14:30:00.123456``.
* ``{file.ctime.isoweekday}``: day of the week. For example ``5``.
* ``{file.ctime.now}``: current datetime. For example ``2023-06-29 02:32:15.123456``.
* ``{file.ctime.time}``: time in ISO 8601 format. For example ``14:30:00.123456``.
* ``{file.ctime.timestamp}``: timestamp of the datetime. For example ``1572622200``.
* ``{file.ctime.today}``: current datetime. For example ``2023-06-29 02:32:15.123456``.
* ``{file.ctime.toordinal}``: ordinal of the datetime. For example ``737373``.
* ``{file.ctime.tzname}``: name of the timezone. For example ``CET``.
* ``{file.ctime.utcnow}``: current datetime in UTC. For example ``2019-11-01 13:30:00.123456``.
* ``{file.ctime.utcoffset}``: offset of the timezone. For example ``3600``.
* ``{file.ctime.weekday}``: day of the week. For example ``4``.

The ``{file.mtime}`` and ``{file.atime}`` attributes have the same methods & attributes. Also the ``{now}`` variable.

For more info about the datetime attributes and methods, you can read the
`datetime.datetime documentation <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_.


Checksum attributes
-------------------
The file object has the following attributes to get the checksums of the file:

* ``{file.md5}``: MD5 checksum of the file. For example ``d41d8cd98f00b204e9800998ecf8427e``.
* ``{file.sha1}``: SHA1 checksum of the file. For example ``da39a3ee5e6b4b0d3255bfef95601890afd80709``.
* ``{file.sha224}``: SHA224 checksum of the file. For example ``d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f``.
* ``{file.sha256}``: SHA256 checksum of the file. For example ``e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855``.
* ``{file.sha384}``: SHA384 checksum of the file.
* ``{file.sha512}``: SHA512 checksum of the file.
* ``{file.sha3_224}``: SHA3 224 checksum of the file.
* ``{file.sha3_256}``: SHA3 256 checksum of the file.
* ``{file.sha3_384}``: SHA3 384 checksum of the file.
* ``{file.sha3_512}``: SHA3 512 checksum of the file.
* ``{file.crc32}``: CRC32 checksum of the file. For example ``00000000``.
* ``{file.adler32}``: Adler32 checksum of the file. For example ``00000001``.

Note that the checksums are calculated after accesing the attribute. If you access the attribute twice, the checksum
will be calculated twice. Calculate the checksums can take a lot of time, so it's recommended to use the checksums only
when you need them.


String methods
--------------
The next methods are available to manipulate the strings availables in the file object. All the examples are using the
string attribute ``{file.stem}`` (with the value ``my file name``), but you can use any string attribute.

* ``{file.stem.title}``: capitalize the string. For example ``My File Name``.
* ``{file.stem.capitalize}``: capitalize the string. For example ``My file name``.
* ``{file.stem.lower}``: convert the string to lowercase. For example ``my file name``.
* ``{file.stem.upper}``: convert the string to uppercase. For example ``MY FILE NAME``.
* ``{file.stem.swapcase}``: swap the case of the string. For example ``MY FILE NAME``.
* ``{file.stem.strip}``: remove the leading and trailing characters. For example ``my file name``. This is useful to
  remove the spaces in the filename. For example if the stem is ``  my file name  `` (with spaces), the value will be
  ``my file name``.
* ``{file.stem.lstrip}``: remove the leading characters. For example ``my file name``. Like strip but only remove the
  characters at the beginning of the string.
* ``{file.stem.rstrip}``: remove the trailing characters. For example ``my file name``. Like strip but only remove the
  characters at the end of the string.
