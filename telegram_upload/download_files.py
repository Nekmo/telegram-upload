import os
from functools import cached_property
from typing import Iterable, Iterator, Optional, BinaryIO

from telethon.tl.types import Message, DocumentAttributeFilename


CHUNK_FILE_SIZE = 1024 * 1024


def pipe_file(read_file_name: str, write_file: BinaryIO):
    with open(read_file_name, "rb") as read_file:
        while True:
            data = read_file.read(CHUNK_FILE_SIZE)
            if data:
                write_file.write(data)
            else:
                break


class JoinStrategyBase:
    def __init__(self):
        self.download_files = []

    def is_part(self, download_file: 'DownloadFile') -> bool:
        raise NotImplementedError

    def add_download_file(self, download_file: 'DownloadFile') -> None:
        if download_file in self.download_files:
            return
        self.download_files.append(download_file)

    @classmethod
    def is_applicable(cls, download_file: 'DownloadFile') -> bool:
        raise NotImplementedError

    def join_download_files(self):
        raise NotImplementedError


class UnionJoinStrategy(JoinStrategyBase):
    base_name: Optional[str] = None

    @staticmethod
    def get_base_name(download_file: 'DownloadFile'):
        return download_file.file_name.rsplit(".", 1)[0]

    def add_download_file(self, download_file: 'DownloadFile') -> None:
        if self.base_name is None:
            self.base_name = self.get_base_name(download_file)
        super().add_download_file(download_file)

    def is_part(self, download_file: 'DownloadFile') -> bool:
        return self.base_name == self.get_base_name(download_file)

    @classmethod
    def is_applicable(cls, download_file: 'DownloadFile') -> bool:
        return download_file.file_name_extension.isdigit()

    def join_download_files(self):
        download_files = self.download_files
        sorted_files = sorted(download_files, key=lambda x: x.file_name_extension)
        sorted_files = [file for file in sorted_files if os.path.lexists(file.file_name)]
        if not sorted_files or len(sorted_files) - 1 != int(sorted_files[-1].file_name_extension):
            # There are parts of the file missing. Stopping...
            return
        with open(self.base_name, "wb") as new_file:
            for download_file in sorted_files:
                pipe_file(download_file.file_name, new_file)
        for download_file in sorted_files:
            os.remove(download_file.file_name)


JOIN_STRATEGIES = [
    UnionJoinStrategy,
]


def get_join_strategy(download_file: 'DownloadFile') -> Optional[JoinStrategyBase]:
    for strategy_cls in JOIN_STRATEGIES:
        if strategy_cls.is_applicable(download_file):
            strategy = strategy_cls()
            strategy.add_download_file(download_file)
            return strategy


class DownloadFile:
    file_name: Optional[str] = None

    """File to download. This includes the Telethon message with the file."""
    def __init__(self, message: Message):
        self.message = message

    def set_download_file_name(self, file_name):
        self.file_name = file_name

    @cached_property
    def filename_attr(self) -> Optional[DocumentAttributeFilename]:
        return next(filter(lambda x: isinstance(x, DocumentAttributeFilename),
                           self.document.attributes), None)

    @cached_property
    def file_name(self) -> str:
        return self.filename_attr.file_name if self.filename_attr else 'Unknown'

    @property
    def file_name_extension(self) -> str:
        parts = self.file_name.rsplit(".", 1)
        return parts[-1] if len(parts) >= 2 else ""

    @property
    def document(self):
        return self.message.document

    @property
    def size(self) -> int:
        return self.document.size

    def __eq__(self, other: 'DownloadFile'):
        return self.file_name == other.file_name


class DownloadSplitFilesBase:
    """Iterate over complete and split files. Base class to inherit."""
    def __init__(self, messages: Iterable[Message]):
        self.messages = messages

    def get_iterator(self) -> Iterator[DownloadFile]:
        raise NotImplementedError

    def __iter__(self) -> 'DownloadSplitFilesBase':
        self._iterator = self.get_iterator()
        return self

    def __next__(self) -> 'DownloadFile':
        if self._iterator is None:
            self._iterator = self.get_iterator()
        return next(self._iterator)


class KeepDownloadSplitFiles(DownloadSplitFilesBase):
    def get_iterator(self) -> Iterator[DownloadFile]:
        return map(lambda message: DownloadFile(message), self.messages)


class JoinDownloadSplitFiles(DownloadSplitFilesBase):
    def get_iterator(self) -> Iterator[DownloadFile]:
        current_join_strategy: Optional[JoinStrategyBase] = None
        for message in self.messages:
            download_file = DownloadFile(message)
            yield download_file
            if current_join_strategy and current_join_strategy.is_part(download_file):
                current_join_strategy.add_download_file(download_file)
            elif current_join_strategy and not current_join_strategy.is_part(download_file):
                current_join_strategy.join_download_files()
                current_join_strategy = None
            if current_join_strategy is None:
                current_join_strategy = get_join_strategy(download_file)
        else:
            if current_join_strategy:
                current_join_strategy.join_download_files()
