import unittest

from telegram_upload.exceptions import TelegramUploadError


class TestTelegramUploadError(unittest.TestCase):
    def test_exception(self):
        self.assertEqual(str(TelegramUploadError()), 'TelegramUploadError')

    def test_body(self):
        error = TelegramUploadError()
        error.body = 'body'
        self.assertEqual(str(error), 'TelegramUploadError: body')

    def test_extra_body(self):
        self.assertEqual(str(TelegramUploadError('extra_body')), 'TelegramUploadError: extra_body')

    def test_all(self):
        error = TelegramUploadError('extra_body')
        error.body = 'body'
        self.assertEqual(str(error), 'TelegramUploadError: body. extra_body')
