import os


import mimetypes

from hachoir.metadata.video import MP4Metadata
from telethon.tl.types import DocumentAttributeVideo

from telegram_upload.exceptions import TelegramInvalidFile
from telegram_upload.utils import scantree
from telegram_upload.video import get_video_thumb, video_metadata

mimetypes.init()


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


