Troubleshooting
===============

Videos are not streameable in Telegram app
-------------------------------------------
Only mp4 videos can be played on Telegram without downloading them first. To stream your video in Telegram you must
convert it before uploading it. For example you can use ffmpeg to convert your video::

    $ ffmpeg -i input.mov -preset slow -codec:a libfdk_aac -b:a 128k \
             -codec:v libx264 -pix_fmt yuv420p -b:v 2500k -minrate 1500k \
             -maxrate 4000k -bufsize 5000k -vf scale=-1:720 output.mp4

