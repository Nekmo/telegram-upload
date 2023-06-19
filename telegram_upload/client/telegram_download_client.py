from typing import Iterable

from telethon import TelegramClient

from telegram_upload.client.progress_bar import get_progress_bar
from telegram_upload.download_files import DownloadFile
from telegram_upload.exceptions import TelegramUploadNoSpaceError
from telegram_upload.utils import free_disk_usage, sizeof_fmt


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

    def forward_to(self, message, destinations):
        for destination in destinations:
            self.forward_messages(destination, [message])
