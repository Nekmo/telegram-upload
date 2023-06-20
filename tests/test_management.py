import os
import unittest
from unittest.mock import MagicMock

from telethon.tl.types import DocumentAttributeFilename, User

from ._compat import patch

from click.testing import CliRunner

from telegram_upload.management import upload, download, get_file_display_name

directory = os.path.dirname(os.path.abspath(__file__))


class TestGetFileDisplayName(unittest.TestCase):
    def test_get_file_display_name(self):
        mock_message = MagicMock()
        mock_message.document.mime_type = "text/plain"
        mock_message.document.attributes = [DocumentAttributeFilename("test.txt")]
        mock_message.text = "text"
        mock_message.sender = User(
            1000, first_name="first_name", last_name="last_name", username="username",
        )
        mock_message.date = "date"
        display_name = get_file_display_name(mock_message)
        self.assertEqual('text test.txt [text] by first_name last_name @username date', display_name)


class TestUpload(unittest.TestCase):

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload(self, m1, m2):
        test_file = os.path.join(directory, 'test_management.py')
        runner = CliRunner()
        result = runner.invoke(upload, [test_file])
        self.assertEqual(result.exit_code, 0)
        m1.assert_called_once()
        m1.return_value.send_files.assert_called_once()

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_exclusive(self, m1, m2):
        runner = CliRunner()
        result = runner.invoke(upload, ['missing_file.txt', '--thumbnail-file', 'cara128.png', '--no-thumbnail'])
        self.assertEqual(result.exit_code, 2)
        m1.return_value.send_files.assert_not_called()


class TestDownload(unittest.TestCase):
    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_download(self, m1, m2):
        runner = CliRunner()
        result = runner.invoke(download, [])
        self.assertEqual(result.exit_code, 0)
        m1.assert_called_once()
        m1.return_value.download_files.assert_called_once()
