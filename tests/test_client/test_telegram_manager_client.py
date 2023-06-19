import unittest
from unittest.mock import patch

import socks

from telegram_upload.client.telegram_manager_client import phone_match, parse_proxy_string
from telegram_upload.exceptions import TelegramProxyError


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
    pass
