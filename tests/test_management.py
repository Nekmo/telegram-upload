import os
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from telegram_upload.management import upload, download

directory = os.path.dirname(os.path.abspath(__file__))


class TestUpload(unittest.TestCase):
    @patch('telegram_upload.management.Client')
    def test_upload(self, m):
        test_file = os.path.join(directory, 'test_management.py')
        runner = CliRunner()
        result = runner.invoke(upload, [test_file])
        self.assertEqual(result.exit_code, 0)
        m.assert_called_once()
        m.return_value.send_files.assert_called_once()

    @patch('telegram_upload.management.Client')
    def test_failed(self, m):
        runner = CliRunner()
        result = runner.invoke(upload, ['missing_file.txt'])
        self.assertEqual(result.exit_code, 1)
        m.return_value.send_files.assert_not_called()


class TestDownload(unittest.TestCase):
    @patch('telegram_upload.management.Client')
    def test_download(self, m):
        runner = CliRunner()
        result = runner.invoke(download, [])
        self.assertEqual(result.exit_code, 0)
        m.assert_called_once()
        m.return_value.download_files.assert_called_once()
