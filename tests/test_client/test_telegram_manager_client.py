import json
import unittest
from unittest.mock import patch, MagicMock, mock_open

import socks
from telethon.network import ConnectionTcpMTProxyRandomizedIntermediate

from telegram_upload.client import TelegramManagerClient
from telegram_upload.client.telegram_manager_client import phone_match, parse_proxy_string, USER_MAX_FILE_SIZE, \
    BOT_USER_MAX_FILE_SIZE, PREMIUM_USER_MAX_FILE_SIZE, USER_MAX_CAPTION_LENGTH, PREMIUM_USER_MAX_CAPTION_LENGTH
from telegram_upload.config import SESSION_FILE
from telegram_upload.exceptions import TelegramProxyError


CONFIG_DATA = {'api_hash': '', 'api_id': ''}


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


class TestTelegramManagerClient(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_manager_client.TelegramUploadClient.__init__')
    def test_init(self, mock_init: MagicMock):
        config_file = "config_file"
        proxy = "mtproxy://secret@proxy.my.site:443"
        TelegramManagerClient(config_file, proxy=proxy)
        mock_init.assert_called_once_with(
            SESSION_FILE, CONFIG_DATA["api_id"], CONFIG_DATA["api_hash"], proxy=("proxy.my.site", 443, "secret"),
            connection=ConnectionTcpMTProxyRandomizedIntermediate
        )

    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_manager_client.TelegramUploadClient.__init__')
    @patch('telegram_upload.client.telegram_manager_client.TelegramUploadClient.start')
    def test_start(self, mock_start: MagicMock, _: MagicMock):
        config_file = "config_file"
        phone = "phone"
        password = "password"
        bot_token = "bot_token"
        force_sms = True
        first_name = "first_name"
        last_name = "last_name"
        max_attempts = 3
        TelegramManagerClient(config_file).start(
            phone, password, bot_token=bot_token, force_sms=force_sms, first_name=first_name, last_name=last_name,
            max_attempts=max_attempts
        )
        mock_start.assert_called_once_with(
            phone=phone, password=password, bot_token=bot_token, force_sms=force_sms, first_name=first_name,
            last_name=last_name, max_attempts=max_attempts,
        )

    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_manager_client.TelegramManagerClient.__init__', return_value=None)
    @patch('telegram_upload.client.telegram_manager_client.TelegramManagerClient.get_me')
    def test_me(self, mock_get_me: MagicMock, _: MagicMock):
        me_result = TelegramManagerClient(MagicMock()).me
        mock_get_me.assert_called_once_with()
        self.assertEqual(mock_get_me.return_value, me_result)

    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_manager_client.TelegramManagerClient.__init__', return_value=None)
    @patch('telegram_upload.client.telegram_manager_client.TelegramManagerClient.me')
    def test_max_file_size(self, mock_me: MagicMock, _: MagicMock):
        with self.subTest("Test user max file size"):
            mock_me.premium = False
            mock_me.bot = False
            self.assertEqual(TelegramManagerClient(MagicMock()).max_file_size, USER_MAX_FILE_SIZE)
        with self.subTest("Test bot max file size"):
            mock_me.premium = False
            mock_me.bot = True
            self.assertEqual(TelegramManagerClient(MagicMock()).max_file_size, BOT_USER_MAX_FILE_SIZE)
        with self.subTest("Test premium user max file size"):
            mock_me.premium = True
            mock_me.bot = False
            self.assertEqual(TelegramManagerClient(MagicMock()).max_file_size, PREMIUM_USER_MAX_FILE_SIZE)

    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_manager_client.TelegramManagerClient.__init__', return_value=None)
    @patch('telegram_upload.client.telegram_manager_client.TelegramManagerClient.me')
    def test_max_caption_length(self, mock_me: MagicMock, _: MagicMock):
        with self.subTest("Test user max caption length"):
            mock_me.premium = False
            self.assertEqual(TelegramManagerClient(MagicMock()).max_caption_length, USER_MAX_CAPTION_LENGTH)
        with self.subTest("Test premium user max caption length"):
            mock_me.premium = True
            self.assertEqual(TelegramManagerClient(MagicMock()).max_caption_length, PREMIUM_USER_MAX_CAPTION_LENGTH)
