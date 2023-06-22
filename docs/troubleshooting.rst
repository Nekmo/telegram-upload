Troubleshooting
===============

Videos are not streameable in Telegram app
-------------------------------------------
**Only mp4 videos can be played on Telegram without downloading them first**. To stream your video in Telegram you must
convert it before uploading it. For example you can use ffmpeg to convert your video::

    $ ffmpeg -i input.mov -preset slow -codec:a libfdk_aac -b:a 128k \
             -codec:v libx264 -pix_fmt yuv420p -b:v 2500k -minrate 1500k \
             -maxrate 4000k -bufsize 5000k -vf scale=-1:720 output.mp4


Database is locked
------------------
Telegram-upload is already running, or an old process **has locked the session** (``telegram-upload.session``). Only one
Telegram-upload session can be run at a time.

**If you need to run Telegram-upload multiple times anyway**, you need to duplicate the session and config files:

1. Copy the session file (``~/.config/telegram-upload.session``) to another path.
2. Copy the configuration file (``~/.config/telegram-upload.json``) to another path.
3. Edit this file and add the path to session file like this: ``{"api_id": 0, "api_hash":
   "...", "session": "/path/to/telegram-upload.json"}``.
4. Run using ``--config /path/to/telegram-upload.json``.

If you are sure that Telegram-upload is not running, search for the process that is blocking the file::

    fuser ~/.config/telegram-upload.session

As a last resort, you can restart your machine.


I am getting 429 errors during upload
-------------------------------------
Since version v0.7.0 Telegram-upload uploads several parts of the file in parallel. Become of this, the Telegram API
can become overloaded and return 429 errors. This is normal and you don't have to worry. If you are getting too many of
these errors, you can try to reduce the number of parallel uploads using the ``PARALLEL_UPLOAD_BLOCKS`` environment
variable. For example::

    $ PARALLEL_UPLOAD_BLOCKS=2 telegram-upload video.mkv

Or exporting the variable::

    $ export PARALLEL_UPLOAD_BLOCKS=2
    $ telegram-upload video.mkv

The **default value is 4**. Values above this value can increase the number of 429 errors. Telegram-upload in case of
an error will try to reconnect to the API before ``TELEGRAM_UPLOAD_MIN_RECONNECT_WAIT`` seconds. The default value is 2.
This value will be increased with each retry. Each retry will decrease the number of ``PARALLEL_UPLOAD_BLOCKS``. The
minimum of ``PARALLEL_UPLOAD_BLOCKS`` is one. Telegram-upload will retry connecting up to
``TELEGRAM_UPLOAD_MAX_RECONNECT_RETRIES`` times. The default value is 5. Each retry has a maximum wait time of
``TELEGRAM_UPLOAD_RECONNECT_TIMEOUT`` seconds before failing. All of these variables can be defined using environment
variables.

Telegram-upload does not work! An error occurs when executing it
-----------------------------------------------------------------
Telegram-upload is not tested with all versions of all dependencies it uses. If you have installed Telegram-upload
on your system (using root) maybe some existing dependency is on an incompatible version. You can try updating the
dependencies carefully::

    $ pip install -U telegram-upload Telethon hachoir cryptg click

To avoid errors it is recommended to use `virtualenvs <https://docs.python-guide.org/dev/virtualenvs/>`_.

Before asking for help, remember to find out if `the issue already exists <https://github
.com/Nekmo/telegram-upload/issues>`_. If you open a ticket remember to paste your system dependencies on the issue::

    $ pip freeze

Some problems may not be related to Telegram-upload. If possible, `Google before asking <https://google.com/>`_.
