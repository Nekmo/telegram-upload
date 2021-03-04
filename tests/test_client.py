import json
import os
import unittest
from unittest.mock import patch, mock_open, sentinel, Mock

import socks
from telethon.tl.types import DocumentAttributeFilename

from telegram_upload.client import Client, parse_proxy_string, phone_match
from telegram_upload.exceptions import TelegramUploadDataLoss, TelegramUploadNoSpaceError, TelegramProxyError, \
    MissingFileError
from telegram_upload.files import File

CONFIG_DATA = {'api_hash': '', 'api_id': ''}

directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')


class AnyArg(object):
    """https://stackoverflow.com/questions/20428750/pythons-assert-called-with-is-there-a-wildcard-character"""
    def __eq__(a, b):
        return True


class TestPhoneMatch(unittest.TestCase):
    def test_not_valid_phone(self):
        with self.assertRaises(ValueError):
            phone_match('foo')

    def test_number(self):
        number = '+34612345678'
        self.assertEqual(phone_match(number), number)


class TestParseProxyString(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(parse_proxy_string(None))

    def test_malformed_url(self):
        with self.assertRaises(TelegramProxyError):
            parse_proxy_string('foo')

    def test_mtproxy(self):
        s = parse_proxy_string('mtproxy://secret@foo:123')
        self.assertEqual(s, ('mtproxy', 'foo', 123, 'secret'))

    @patch('builtins.__import__', side_effect=ImportError)
    def test_socks_import_error(self, m):
        with self.assertRaises(TelegramProxyError):
            parse_proxy_string('socks4://user:pass@foo:123')

    def test_unsupported_proxy_type(self):
        with self.assertRaises(TelegramProxyError):
            parse_proxy_string('foo://user:pass@foo:123')

    def test_proxy(self):
        self.assertEqual(
            parse_proxy_string('http://user:pass@foo:123'),
            (socks.HTTP, 'foo', 123, True, 'user', 'pass')
        )


class TestClient(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.TelegramClient.__init__')
    def setUp(self, m1) -> None:
        self.upload_file_path = os.path.abspath(os.path.join(directory, 'logo.png'))
        self.client = Client('foo.json')
        self.client.send_file = Mock()
        self.client.send_file.return_value.media.document.size = os.path.getsize(self.upload_file_path)

    @patch('telegram_upload.management.default_config')
    def test_missing_file(self, m1):
        with self.assertRaises(MissingFileError):
            self.client.send_files('foo', [])

    def test_send_files(self):
        entity = 'foo'
        file = File(self.upload_file_path)
        self.client.send_files(entity, [file])
        self.client.send_file.assert_called_once_with(
            entity, file, thumb=None, file_size=file.file_size,
            caption=os.path.basename(self.upload_file_path).split('.')[0], force_document=False,
            progress_callback=AnyArg(), attributes=[],
        )

    def test_send_files_data_loss(self):
        file = File(self.upload_file_path)
        self.client.send_file.return_value.media.document.size = 200
        with self.assertRaises(TelegramUploadDataLoss):
            self.client.send_files('foo', [file])

    def test_download_files(self):
        m = Mock()
        m.document.attributes = [DocumentAttributeFilename('download.png')]
        m.document.size = 0
        self.client.download_files('foo', [m])

    def test_no_space_error(self):
        m = Mock()
        m.document.attributes = [DocumentAttributeFilename('download.png')]
        m.document.size = 1000
        with patch('telegram_upload.client.free_disk_usage', return_value=0), \
            self.assertRaises(TelegramUploadNoSpaceError):
            self.client.download_files('foo', [m])
