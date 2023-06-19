import json
import unittest
from unittest.mock import patch, mock_open, Mock

from telethon.tl.types import DocumentAttributeFilename

from telegram_upload.client.telegram_manager_client import TelegramManagerClient
from telegram_upload.exceptions import TelegramUploadNoSpaceError

CONFIG_DATA = {'api_hash': '', 'api_id': ''}


class TestTelegramManagerClient(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_manager_client.TelegramUploadClient.__init__')
    def setUp(self, m1) -> None:
        self.client = TelegramManagerClient('foo.json')

    def test_download_files(self):
        m = Mock()
        m.document.attributes = [DocumentAttributeFilename('download.png')]
        m.size = 0
        self.client.download_files('foo', [m])

    def test_no_space_error(self):
        m = Mock()
        m.document.attributes = [DocumentAttributeFilename('download.png')]
        m.size = 1000
        with patch('telegram_upload.client.telegram_download_client.free_disk_usage', return_value=0), \
            self.assertRaises(TelegramUploadNoSpaceError):
            self.client.download_files('foo', [m])
