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
   "...", "session": "/path/to/telegram-upload.json"}``
4. Run using ``--config /path/to/telegram-upload.json``.

If you are sure that Telegram-upload is not running, search for the process that is blocking the file::

    fuser ~/.config/telegram-upload.session

As a last resort, you can restart your machine.
