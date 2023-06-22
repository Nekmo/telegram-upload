import asyncio
import inspect
import io
import pathlib
import sys
from typing import Iterable

import typing

from more_itertools import grouper
from telethon import TelegramClient, utils, helpers
from telethon.client.downloads import MIN_CHUNK_SIZE
from telethon.crypto import AES

from telegram_upload.client.progress_bar import get_progress_bar
from telegram_upload.download_files import DownloadFile
from telegram_upload.exceptions import TelegramUploadNoSpaceError
from telegram_upload.utils import free_disk_usage, sizeof_fmt, get_environment_integer


if sys.version_info < (3, 10):
    from telegram_upload._compat import anext


PARALLEL_DOWNLOAD_BLOCKS = get_environment_integer('TELEGRAM_UPLOAD_PARALLEL_DOWNLOAD_BLOCKS', 10)


class TelegramDownloadClient(TelegramClient):
    def find_files(self, entity):
        for message in self.iter_messages(entity):
            if message.document:
                yield message
            else:
                break

    async def iter_files(self, entity):
        async for message in self.iter_messages(entity=entity):
            if message.document:
                yield message

    def download_files(self, entity, download_files: Iterable[DownloadFile], delete_on_success: bool = False):
        for download_file in download_files:
            if download_file.size > free_disk_usage():
                raise TelegramUploadNoSpaceError(
                    'There is no disk space to download "{}". Space required: {}'.format(
                        download_file.file_name, sizeof_fmt(download_file.size - free_disk_usage())
                    )
                )
            progress, bar = get_progress_bar('Downloading', download_file.file_name, download_file.size)
            file_name = download_file.file_name
            try:
                file_name = self.download_media(download_file.message, progress_callback=progress)
                download_file.set_download_file_name(file_name)
            finally:
                bar.label = f'Downloaded  "{file_name}"'
                bar.update(1, 1)
                bar.render_finish()
            if delete_on_success:
                self.delete_messages(entity, [download_file.message])

    async def _download_file(
            self: 'TelegramClient',
            input_location: 'hints.FileLike',
            file: 'hints.OutFileLike' = None,
            *,
            part_size_kb: float = None,
            file_size: int = None,
            progress_callback: 'hints.ProgressCallback' = None,
            dc_id: int = None,
            key: bytes = None,
            iv: bytes = None,
            msg_data: tuple = None) -> typing.Optional[bytes]:
        if not part_size_kb:
            if not file_size:
                part_size_kb = 64  # Reasonable default
            else:
                part_size_kb = utils.get_appropriated_part_size(file_size)

        part_size = int(part_size_kb * 1024)
        if part_size % MIN_CHUNK_SIZE != 0:
            raise ValueError(
                'The part size must be evenly divisible by 4096.')

        if isinstance(file, pathlib.Path):
            file = str(file.absolute())

        in_memory = file is None or file is bytes
        if in_memory:
            f = io.BytesIO()
        elif isinstance(file, str):
            # Ensure that we'll be able to download the media
            helpers.ensure_parent_dir_exists(file)
            f = open(file, 'wb')
        else:
            f = file

        try:
            # The speed of this code can be improved. 10 requests are made in parallel, but it waits for all 10 to
            # finish before launching another 10.
            for tasks in grouper(self._iter_download_chunk_tasks(input_location, part_size, dc_id, msg_data, file_size),
                                 PARALLEL_DOWNLOAD_BLOCKS):
                tasks = list(filter(bool, tasks))
                await asyncio.wait(tasks)
                chunk = b''.join(filter(bool, [task.result() for task in tasks]))
                if not chunk:
                    break
                if iv and key:
                    chunk = AES.decrypt_ige(chunk, key, iv)
                r = f.write(chunk)
                if inspect.isawaitable(r):
                    await r

                if progress_callback:
                    r = progress_callback(f.tell(), file_size)
                    if inspect.isawaitable(r):
                        await r

            # Not all IO objects have flush (see #1227)
            if callable(getattr(f, 'flush', None)):
                f.flush()

            if in_memory:
                return f.getvalue()
        finally:
            if isinstance(file, str) or in_memory:
                f.close()

    def _iter_download_chunk_tasks(self, input_location, part_size, dc_id, msg_data, file_size):
        for i in range(0, file_size, part_size):
            yield self.loop.create_task(
                anext(self._iter_download(input_location, offset=i, request_size=part_size, dc_id=dc_id,
                                          msg_data=msg_data))
            )
