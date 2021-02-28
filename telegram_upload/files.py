import math
import os


import mimetypes
from io import FileIO, SEEK_SET
from typing import Union

from hachoir.metadata.video import MP4Metadata
from telethon.tl.types import DocumentAttributeVideo

from telegram_upload.exceptions import TelegramInvalidFile
from telegram_upload.utils import scantree
from telegram_upload.video import get_video_thumb, video_metadata

mimetypes.init()


MAX_FILE_SIZE = 2097152000


def is_valid_file(file, errorLogger=None):
    if not os.path.lexists(file):
        errorLogger('File "{}" does not exist.'.format(file))
        return False
    elif not os.path.getsize(file):
        errorLogger('File "{}" is empty.'.format(file))
        return False
    return True


def get_file_mime(file):
    return (mimetypes.guess_type(file)[0] or ('')).split('/')[0]


def get_file_attributes(file):
    attrs = []
    mime = get_file_mime(file)
    if mime == 'video':
        metadata = video_metadata(file)
        video_meta = metadata
        meta_groups = None
        if hasattr(metadata, '_MultipleMetadata__groups'):
            # Is mkv
            meta_groups = metadata._MultipleMetadata__groups
        if not metadata.has('width') and meta_groups:
            video_meta = meta_groups[next(filter(lambda x: x.startswith('video'), meta_groups._key_list))]
        supports_streaming = isinstance(video_meta, MP4Metadata)
        attrs.append(DocumentAttributeVideo(
            (0, metadata.get('duration').seconds)[metadata.has('duration')],
            (0, video_meta.get('width'))[video_meta.has('width')],
            (0, video_meta.get('height'))[video_meta.has('height')],
            False,
            supports_streaming,
        ))
    return attrs


def get_file_thumb(file):
    if get_file_mime(file) == 'video':
        return get_video_thumb(file)


class FilesBase:
    def __init__(self, files):
        self._iterator = None
        self.files = files

    def get_iterator(self):
        raise NotImplementedError

    def __iter__(self):
        self._iterator = self.get_iterator()
        return self

    def __next__(self):
        if self._iterator is None:
            self._iterator = self.get_iterator()
        return next(self._iterator)


class RecursiveFiles(FilesBase):

    def get_iterator(self):
        for file in self.files:
            if os.path.isdir(file):
                yield from map(lambda file: file.path,
                               filter(lambda x: not x.is_dir(), scantree(file, True)))
            else:
                yield file


class NoDirectoriesFiles(FilesBase):
    def get_iterator(self):
        for file in self.files:
            if os.path.isdir(file):
                raise TelegramInvalidFile('"{}" is a directory.'.format(file))
            else:
                yield file


class LargeFilesBase(FilesBase):
    def get_iterator(self):
        for file in self.files:
            if os.path.getsize(file) > MAX_FILE_SIZE:
                yield from self.process_large_file(file)
            else:
                yield file

    def process_large_file(self, file):
        raise NotImplementedError


class NoLargeFiles(LargeFilesBase):
    def process_large_file(self, file):
        raise TelegramInvalidFile('"{}" file is too large for Telegram.'.format(file))


class File:
    @property
    def file_name(self):
        raise NotImplementedError

    @property
    def file_size(self):
        raise NotImplementedError


class SplitFile(File, FileIO):
    def __init__(self, file: Union[str, bytes, int], max_read_size: int, name: str):
        super().__init__(file)
        self.max_read_size = max_read_size
        self.remaining_size = max_read_size
        self._name = name

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            size = self.remaining_size
        if not self.remaining_size:
            return b''
        size = min(self.remaining_size, size)
        self.remaining_size -= size
        return super().read(size)

    def readall(self) -> bytes:
        return self.read()

    @property
    def file_name(self):
        return self._name

    @property
    def file_size(self):
        return self.max_read_size

    def seek(self, offset: int, whence: int = SEEK_SET, split_seek: bool = False) -> int:
        if not split_seek:
            self.remaining_size += self.tell() - offset
        return super().seek(offset, whence)


class SplitFiles(LargeFilesBase):
    def process_large_file(self, file):
        file_name = os.path.basename(file)
        total_size = os.path.getsize(file)
        parts = math.ceil(total_size / MAX_FILE_SIZE)
        zfill = int(math.log10(10)) + 1
        for part in range(parts):
            size = total_size - (part * MAX_FILE_SIZE) if part >= parts - 1 else MAX_FILE_SIZE
            splitted_file = SplitFile(file, size, '{}.{}'.format(file_name, str(part).zfill(zfill)))
            splitted_file.seek(MAX_FILE_SIZE * part, split_seek=True)
            yield splitted_file
