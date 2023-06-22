import getpass
import json
import os
import re
from distutils.version import StrictVersion
from functools import cached_property
from typing import Union
from urllib.parse import urlparse

import click
from telethon.errors import ApiIdInvalidError
from telethon.network import ConnectionTcpMTProxyRandomizedIntermediate
from telethon.tl.types import DocumentAttributeFilename, User, InputPeerUser
from telethon.version import __version__ as telethon_version

from telegram_upload.client.telegram_download_client import TelegramDownloadClient
from telegram_upload.client.telegram_upload_client import TelegramUploadClient
from telegram_upload.config import SESSION_FILE
from telegram_upload.exceptions import TelegramProxyError, InvalidApiFileError

if StrictVersion(telethon_version) >= StrictVersion('1.0'):
    import telethon.sync  # noqa


BOT_USER_MAX_FILE_SIZE = 52428800  # 50MB
USER_MAX_FILE_SIZE = 2097152000  # 2GB
PREMIUM_USER_MAX_FILE_SIZE = 4194304000  # 4GB
USER_MAX_CAPTION_LENGTH = 1024
PREMIUM_USER_MAX_CAPTION_LENGTH = 2048
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


class TelegramManagerClient(TelegramUploadClient, TelegramDownloadClient):
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
            phone=lambda: click.prompt('Please enter your phone', type=phone_match),
            password=lambda: getpass.getpass('Please enter your password: '),
            *,
            bot_token=None, force_sms=False, code_callback=None,
            first_name='New User', last_name='', max_attempts=3):
        try:
            return super().start(phone=phone, password=password, bot_token=bot_token, force_sms=force_sms,
                                 first_name=first_name, last_name=last_name, max_attempts=max_attempts)
        except ApiIdInvalidError:
            raise InvalidApiFileError(self.config_file)

    @cached_property
    def me(self) -> Union[User, InputPeerUser]:
        return self.get_me()

    @property
    def max_file_size(self):
        if hasattr(self.me, 'premium') and self.me.premium:
            return PREMIUM_USER_MAX_FILE_SIZE
        elif self.me.bot:
            return BOT_USER_MAX_FILE_SIZE
        else:
            return USER_MAX_FILE_SIZE

    @property
    def max_caption_length(self):
        if hasattr(self.me, 'premium') and self.me.premium:
            return PREMIUM_USER_MAX_CAPTION_LENGTH
        else:
            return USER_MAX_CAPTION_LENGTH
