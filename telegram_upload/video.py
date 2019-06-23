import platform
import struct
import subprocess
import tempfile
import os

import click
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.tl.types import DocumentAttributeVideo


class DocumentAttributeStreamVideo(DocumentAttributeVideo):
    def __bytes__(self):
        return b''.join((
            b'\xe6,\xf0\x0e',
            struct.pack('<I', 10),
            struct.pack('<i', self.duration),
            struct.pack('<i', self.w),
            struct.pack('<i', self.h),
        ))


def video_metadata(file):
    return extractMetadata(createParser(file))


def get_ffmpeg_command():
    return os.environ.get('FFMPEG_COMMAND',
                          'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')


def get_video_thumb(file, output=None, width=90):
    output = output or tempfile.NamedTemporaryFile(suffix='.jpg').name
    metadata = video_metadata(file)
    duration = metadata.get('duration').seconds if metadata.has('duration') else 0
    try:
        p = subprocess.Popen([
            get_ffmpeg_command(),
            '-ss', str(int(duration / 2)),
            '-i', file,
            '-filter:v',
            'scale={}:-1'.format(width),
            '-vframes:v', '1',
            output,
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        click.echo('ffmpeg command is not available. Thumbnails for videos are not available!', err=True)
        return None
    p.communicate()
    if not p.returncode and os.path.lexists(file):
        return output
