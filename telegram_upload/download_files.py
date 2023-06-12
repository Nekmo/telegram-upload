from functools import cached_property
from typing import Iterable, Iterator

from telethon.tl.types import Message, DocumentAttributeFilename


class JoinStrategyBase:
    def __init__(self):
        pass

    @classmethod
    def is_applicable(cls, extension: str, filename: str):
        raise NotImplementedError


class UnionJoinStrategy(JoinStrategyBase):
    @classmethod
    def is_applicable(cls, extension: str, filename: str):
        return extension.isdigit()


JOIN_STRATEGIES = [
    UnionJoinStrategy,
]


class DownloadFile:
    """File to download. This includes the Telethon message with the file."""
    def __init__(self, message: Message):
        self.message = message

    @cached_property
    def filename_attr(self):
        return next(filter(lambda x: isinstance(x, DocumentAttributeFilename),
                           self.message.document.attributes), None)

    @cached_property
    def file_name(self):
        return self.filename_attr.file_name

    @property
    def document(self):
        return self.message.document

    @property
    def size(self):
        return self.document.size


class DownloadSplitFilesBase:
    """Iterate over complete and split files. Base class to inherit."""
    def __init__(self, messages: Iterable[Message]):
        self.messages = messages

    def get_iterator(self) -> Iterator[DownloadFile]:
        raise NotImplementedError

    def __iter__(self):
        self._iterator = self.get_iterator()
        return self

    def __next__(self):
        if self._iterator is None:
            self._iterator = self.get_iterator()
        return next(self._iterator)


class KeepDownloadSplitFiles(DownloadSplitFilesBase):
    def get_iterator(self) -> Iterator[DownloadFile]:
        return map(lambda message: DownloadFile(message), self.messages)


class JoinDownloadSplitFiles(DownloadSplitFilesBase):

    def get_iterator(self):
        return map(lambda x: (x, None), self.messages)
