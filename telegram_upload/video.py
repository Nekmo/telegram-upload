import platform
import re
import struct
import subprocess
import tempfile
import os

import click
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.tl.types import DocumentAttributeVideo

from telegram_upload.exceptions import ThumbVideoError


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


def call_ffmpeg(args):
    try:
        return subprocess.Popen([get_ffmpeg_command()] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise ThumbVideoError('ffmpeg command is not available. Thumbnails for videos are not available!')


def get_ffmpeg_command():
    return os.environ.get('FFMPEG_COMMAND',
                          'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')


def get_video_size(file):
    p = call_ffmpeg([
        '-i', file,
    ])
    stdout, stderr = p.communicate()
    video_lines = re.findall(': Video: ([^\n]+)', stderr.decode('utf-8'))
    if not video_lines:
        return
    matchs = re.findall("(\d{2,6})x(\d{2,6})", video_lines[0])
    if matchs:
        return [int(x) for x in matchs[0]]


def get_video_thumb(file, output=None, size=200):
    output = output or tempfile.NamedTemporaryFile(suffix='.jpg').name
    metadata = video_metadata(file)
    duration = metadata.get('duration').seconds if metadata.has('duration') else 0
    ratio = get_video_size(file)
    if ratio is None:
        raise ThumbVideoError('Video ratio is not available.')
    if ratio[0] / ratio[1] > 1:
        width, height = size, -1
    else:
        width, height = -1, size
    p = call_ffmpeg([
        '-ss', str(int(duration / 2)),
        '-i', file,
        '-filter:v',
        'scale={}:{}'.format(width, height),
        '-vframes:v', '1',
        output,
    ])
    p.communicate()
    if not p.returncode and os.path.lexists(file):
        return output
