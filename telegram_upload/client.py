import getpass
import json
import re
import time
from distutils.version import StrictVersion
from typing import Iterable, Union, Optional
from urllib.parse import urlparse

import click
import os

from telethon.errors import ApiIdInvalidError, RPCError, FloodWaitError
from telethon.network import ConnectionTcpMTProxyRandomizedIntermediate
from telethon.tl import types, functions
from telethon.tl.types import DocumentAttributeFilename
from telethon.utils import pack_bot_file_id

from telegram_upload.config import SESSION_FILE
from telegram_upload.download_files import DownloadFile
from telegram_upload.exceptions import TelegramUploadDataLoss, TelegramUploadNoSpaceError, \
    TelegramProxyError, MissingFileError, InvalidApiFileError
from telegram_upload.upload_files import File
from telethon.version import __version__ as telethon_version
from telethon import TelegramClient, utils

from telegram_upload.utils import free_disk_usage, sizeof_fmt, grouper, async_to_sync

if StrictVersion(telethon_version) >= StrictVersion('1.0'):
    import telethon.sync  # noqa


ALBUM_FILES = 10
RETRIES = 3
PROXY_ENVIRONMENT_VARIABLE_NAMES = [
    'TELEGRAM_UPLOAD_PROXY',
    'HTTPS_PROXY',
    'HTTP_PROXY',
]


def get_message_file_attribute(message):
    return next(filter(lambda x: isinstance(x, DocumentAttributeFilename),
                       message.document.attributes), None)


def phone_match(value):
    match = re.match(r'\+?[0-9.()\[\] \-]+', value)
    if match is None:
        raise ValueError('{} is not a valid phone'.format(value))
    return value


def get_progress_bar(action, file, length):
    bar = click.progressbar(label='{} "{}"'.format(action, file), length=length)

    def progress(current, total):
        bar.pos = 0
        bar.update(current)
    return progress, bar


def get_proxy_environment_variable():
    for env_name in PROXY_ENVIRONMENT_VARIABLE_NAMES:
        if env_name in os.environ:
            return os.environ[env_name]


def parse_proxy_string(proxy: Union[str, None]):
    if not proxy:
        return None
    proxy_parsed = urlparse(proxy)
    if not proxy_parsed.scheme or not proxy_parsed.hostname or not proxy_parsed.port:
        raise TelegramProxyError('Malformed proxy address: {}'.format(proxy))
    if proxy_parsed.scheme == 'mtproxy':
        return ('mtproxy', proxy_parsed.hostname, proxy_parsed.port, proxy_parsed.username)
    try:
        import socks
    except ImportError:
        raise TelegramProxyError('pysocks module is required for use HTTP/socks proxies. '
                                 'Install it using: pip install pysocks')
    proxy_type = {
        'http': socks.HTTP,
        'socks4': socks.SOCKS4,
        'socks5': socks.SOCKS5,
    }.get(proxy_parsed.scheme)
    if proxy_type is None:
        raise TelegramProxyError('Unsupported proxy type: {}'.format(proxy_parsed.scheme))
    return (proxy_type, proxy_parsed.hostname, proxy_parsed.port, True,
            proxy_parsed.username, proxy_parsed.password)


class Client(TelegramClient):
    def __init__(self, config_file, proxy=None, **kwargs):
        with open(config_file) as f:
            config = json.load(f)
        self.config_file = config_file
        proxy = proxy if proxy is not None else get_proxy_environment_variable()
        proxy = parse_proxy_string(proxy)
        if proxy and proxy[0] == 'mtproxy':
            proxy = proxy[1:]
            kwargs['connection'] = ConnectionTcpMTProxyRandomizedIntermediate
        super().__init__(config.get('session', SESSION_FILE), config['api_id'], config['api_hash'],
                         proxy=proxy, **kwargs)

    def start(
            self,
            bot_token=None,
            phone=None,
            password=None,
            *,
            force_sms=False, code_callback=None,
            first_name='New User', last_name='', max_attempts=3):
        with open(self.config_file) as f:
            config = json.load(f)
        try:
            return super().start(phone=config.get('phone', None), password=config.get('password', None),
                                 bot_token=config.get('bot_token', None), force_sms=force_sms, first_name=first_name,
                                 last_name=last_name, max_attempts=max_attempts)
        except ApiIdInvalidError:
            raise InvalidApiFileError(self.config_file)

    async def _send_album_media(self, entity, media):
        entity = await self.get_input_entity(entity)
        request = functions.messages.SendMultiMediaRequest(
            entity, reply_to_msg_id=None, multi_media=media,
            silent=None, schedule_date=None, clear_draft=None
        )
        result = await self(request)

        random_ids = [m.random_id for m in media]
        return self._get_response_message(random_ids, result, entity)

    def send_files_as_album(self, entity, files, delete_on_success=False, print_file_id=False,
                            forward=()):
        for files_group in grouper(ALBUM_FILES, files):
            media = self.send_files(entity, files_group, delete_on_success, print_file_id, forward, send_as_media=True)
            async_to_sync(self._send_album_media(entity, media))

    def _send_file_message(self, entity, file, thumb, progress):
        message = self.send_file(entity, file, thumb=thumb,
                                 file_size=file.file_size if isinstance(file, File) else None,
                                 caption=file.file_caption, force_document=file.force_file,
                                 progress_callback=progress, attributes=file.file_attributes)
        if hasattr(message.media, 'document') and file.file_size != message.media.document.size:
            raise TelegramUploadDataLoss(
                'Remote document size: {} bytes (local file size: {} bytes)'.format(
                    message.media.document.size, file.file_size))
        return message

    async def _send_media(self, entity, file: File, progress):
        entity = await self.get_input_entity(entity)
        supports_streaming = False  # TODO
        fh, fm, _ = await self._file_to_media(
            file, supports_streaming=file, progress_callback=progress)
        if isinstance(fm, types.InputMediaUploadedPhoto):
            r = await self(functions.messages.UploadMediaRequest(
                entity, media=fm
            ))

            fm = utils.get_input_media(r.photo)
        elif isinstance(fm, types.InputMediaUploadedDocument):
            r = await self(functions.messages.UploadMediaRequest(
                entity, media=fm
            ))

            fm = utils.get_input_media(
                r.document, supports_streaming=supports_streaming)

        return types.InputSingleMedia(
            fm,
            message=file.short_name,
            entities=None,
            # random_id is autogenerated
        )

    def send_one_file(self, entity, file: File, send_as_media: bool = False, thumb: Optional[str] = None,
                      retries=RETRIES):
        message = None
        progress, bar = get_progress_bar('Uploading', file.file_name, file.file_size)

        try:
            try:
                if send_as_media:
                    message = async_to_sync(self._send_media(entity, file, progress))
                else:
                    message = self._send_file_message(entity, file, thumb, progress)
            finally:
                bar.render_finish()
        except FloodWaitError as e:
            click.echo(f'{e}. Waiting for {e.seconds} seconds.', err=True)
            time.sleep(e.seconds)
            message = self.send_one_file(entity, file, send_as_media, thumb, retries)
        except RPCError as e:
            if retries > 0:
                click.echo(f'The file "{file.file_name}" could not be uploaded: {e}. Retrying...', err=True)
                message = self.send_one_file(entity, file, send_as_media, thumb, retries - 1)
            else:
                click.echo(f'The file "{file.file_name}" could not be uploaded: {e}. It will not be retried.', err=True)
        return message

    def send_files(self, entity, files: Iterable[File], delete_on_success=False, print_file_id=False,
                   forward=(), send_as_media: bool = False):
        has_files = False
        messages = []
        for file in files:
            has_files = True
            thumb = file.get_thumbnail()
            try:
                message = self.send_one_file(entity, file, send_as_media)
            finally:
                if thumb and not file.is_custom_thumbnail and os.path.lexists(thumb):
                    os.remove(thumb)
            if message is None:
                click.echo('Failed to upload file "{}"'.format(file.file_name), err=True)
            if message and print_file_id:
                click.echo('Uploaded successfully "{}" (file_id {})'.format(file.file_name,
                                                                            pack_bot_file_id(message.media)))
            if message and delete_on_success:
                click.echo('Deleting "{}"'.format(file))
                os.remove(file.path)
            if message:
                self.forward_to(message, forward)
        if not has_files:
            raise MissingFileError('Files do not exist.')
        return messages

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
