import unittest
from ._compat import patch

from telegram_upload.exceptions import TelegramUploadError, catch


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


class TestCatch(unittest.TestCase):
    def test_call(self):
        self.assertEqual(catch(lambda: 'foo')(), 'foo')

    @patch('telegram_upload.exceptions.sys.stderr.write')
    def test_raise(self, m):
        def raise_error():
            raise TelegramUploadError('Error')
        with self.assertRaises(SystemExit):
            catch(raise_error)()
        m.assert_called_once()
