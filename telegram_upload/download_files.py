import os
import sys
from typing import Iterable, Iterator, Optional, BinaryIO

from telethon.tl.types import Message, DocumentAttributeFilename


if sys.version_info < (3, 8):
    cached_property = property
else:
    from functools import cached_property


CHUNK_FILE_SIZE = 1024 * 1024


def pipe_file(read_file_name: str, write_file: BinaryIO):
    """Read a file by its file name and write in another file already open."""
    with open(read_file_name, "rb") as read_file:
        while True:
            data = read_file.read(CHUNK_FILE_SIZE)
            if data:
                write_file.write(data)
            else:
                break


class JoinStrategyBase:
    """Base class to inherit join strategies. The strategies depend on the file type.
    For example, zip files and rar files do not merge in the same way.
    """
    def __init__(self):
        self.download_files = []

    def is_part(self, download_file: 'DownloadFile') -> bool:
        """Returns if the download file is part of this bundle."""
        raise NotImplementedError

    def add_download_file(self, download_file: 'DownloadFile') -> None:
        """Add a download file to this bundle."""
        if download_file in self.download_files:
            return
        self.download_files.append(download_file)

    @classmethod
    def is_applicable(cls, download_file: 'DownloadFile') -> bool:
        """Returns if this strategy is applicable to the download file."""
        raise NotImplementedError

    def join_download_files(self):
        """Join the downloaded files in the bundle."""
        raise NotImplementedError


class UnionJoinStrategy(JoinStrategyBase):
    """Join separate files without any application. These files have extension
    01, 02, 03...
    """
    base_name: Optional[str] = None

    @staticmethod
    def get_base_name(download_file: 'DownloadFile'):
        """Returns the file name without extension."""
        return download_file.file_name.rsplit(".", 1)[0]

    def add_download_file(self, download_file: 'DownloadFile') -> None:
        """Add a download file to this bundle."""
        if self.base_name is None:
            self.base_name = self.get_base_name(download_file)
        super().add_download_file(download_file)

    def is_part(self, download_file: 'DownloadFile') -> bool:
        """Returns if the download file is part of this bundle."""
        return self.base_name == self.get_base_name(download_file)

    @classmethod
    def is_applicable(cls, download_file: 'DownloadFile') -> bool:
        """Returns if this strategy is applicable to the download file."""
        return download_file.file_name_extension.isdigit()

    def join_download_files(self):
        """Join the downloaded files in the bundle."""
        download_files = self.download_files
        sorted_files = sorted(download_files, key=lambda x: x.file_name_extension)
        sorted_files = [file for file in sorted_files if os.path.lexists(file.downloaded_file_name or "")]
        if not sorted_files or len(sorted_files) - 1 != int(sorted_files[-1].file_name_extension):
            # There are parts of the file missing. Stopping...
            return
        with open(self.get_base_name(sorted_files[0]), "wb") as new_file:
            for download_file in sorted_files:
                pipe_file(download_file.downloaded_file_name, new_file)
        for download_file in sorted_files:
            os.remove(download_file.downloaded_file_name)


JOIN_STRATEGIES = [
    UnionJoinStrategy,
]


def get_join_strategy(download_file: 'DownloadFile') -> Optional[JoinStrategyBase]:
    """Get join strategy for the download file. An instance is returned if a strategy
    is available. Otherwise, None is returned.
    """
    for strategy_cls in JOIN_STRATEGIES:
        if strategy_cls.is_applicable(download_file):
            strategy = strategy_cls()
            strategy.add_download_file(download_file)
            return strategy


class DownloadFile:
    """File to download. This includes the Telethon message with the file."""
    downloaded_file_name: Optional[str] = None

    def __init__(self, message: Message):
        """Creates the download file instance from the message."""
        self.message = message

    def set_download_file_name(self, file_name):
        """After download the file, set the final download file name."""
        self.downloaded_file_name = file_name

    @cached_property
    def filename_attr(self) -> Optional[DocumentAttributeFilename]:
        """Get the document attribute file name attribute in the document."""
        return next(filter(lambda x: isinstance(x, DocumentAttributeFilename),
                           self.document.attributes), None)

    @cached_property
    def file_name(self) -> str:
        """Get the file name."""
        return self.filename_attr.file_name if self.filename_attr else 'Unknown'

    @property
    def file_name_extension(self) -> str:
        """Get the file name extension."""
        parts = self.file_name.rsplit(".", 1)
        return parts[-1] if len(parts) >= 2 else ""

    @property
    def document(self):
        """Get the message document."""
        return self.message.document

    @property
    def size(self) -> int:
        """Get the file size."""
        return self.document.size

    def __eq__(self, other: 'DownloadFile'):
        """Compare download files by their file name."""
        return self.file_name == other.file_name


class DownloadSplitFilesBase:
    """Iterate over complete and split files. Base class to inherit."""
    def __init__(self, messages: Iterable[Message]):
        self.messages = messages

    def get_iterator(self) -> Iterator[DownloadFile]:
        """Get an iterator with the download files."""
        raise NotImplementedError

    def __iter__(self) -> 'DownloadSplitFilesBase':
        """Set the iterator from the get_iterator method."""
        self._iterator = self.get_iterator()
        return self

    def __next__(self) -> 'DownloadFile':
        """Get the next download file in the iterator."""
        if self._iterator is None:
            self._iterator = self.get_iterator()
        return next(self._iterator)


class KeepDownloadSplitFiles(DownloadSplitFilesBase):
    """Download split files without join it."""
    def get_iterator(self) -> Iterator[DownloadFile]:
        """Get an iterator with the download files."""
        return map(lambda message: DownloadFile(message), self.messages)


class JoinDownloadSplitFiles(DownloadSplitFilesBase):
    """Download split files and join it."""
    def get_iterator(self) -> Iterator[DownloadFile]:
        """Get an iterator with the download files. This method applies the join strategy and
        joins the files after download it.
        """
        current_join_strategy: Optional[JoinStrategyBase] = None
        for message in self.messages:
            download_file = DownloadFile(message)
            yield download_file
            if current_join_strategy and current_join_strategy.is_part(download_file):
                # There is a bundle in process and the download file is part of it. Add the download
                # file to the bundle.
                current_join_strategy.add_download_file(download_file)
            elif current_join_strategy and not current_join_strategy.is_part(download_file):
                # There is a bundle in process and the download file is not part of it. Join the files
                # in the bundle and finish it.
                current_join_strategy.join_download_files()
                current_join_strategy = None
            if current_join_strategy is None:
                # There is no bundle in process. Get the current bundle if the file has a strategy
                # available.
                current_join_strategy = get_join_strategy(download_file)
        else:
            # After finish all the files, join the latest bundle.
            if current_join_strategy:
                current_join_strategy.join_download_files()
