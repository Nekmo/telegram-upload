import struct
import subprocess
import tempfile
import os

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


def get_video_thumb(file, output=None, width=90):
    output = output or tempfile.NamedTemporaryFile(suffix='.jpg').name
    metadata = video_metadata(file)
    p = subprocess.Popen([
        'ffmpeg', '-i', file,
        '-ss', str(int((0, metadata.get('duration').seconds)[metadata.has('duration')] / 2)),
        '-filter:v', 'scale={}:-1'.format(width),
        '-vframes', '1',
        output,
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p.communicate()
    if not p.returncode and os.path.lexists(file):
        return output
