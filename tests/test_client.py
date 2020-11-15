import json
import os
import unittest
from unittest.mock import patch, mock_open, sentinel, Mock

from telegram_upload.client import Client
from telegram_upload.exceptions import TelegramUploadDataLoss

CONFIG_DATA = {'api_hash': '', 'api_id': ''}

directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')


class AnyArg(object):
    """https://stackoverflow.com/questions/20428750/pythons-assert-called-with-is-there-a-wildcard-character"""
    def __eq__(a, b):
        return True


class TestClient(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.TelegramClient.__init__')
    def setUp(self, m1) -> None:
        self.upload_file_path = os.path.abspath(os.path.join(directory, 'logo.png'))
        self.client = Client('foo.json')
        self.client.send_file = Mock()
        self.client.send_file.return_value.media.document.size = os.path.getsize(self.upload_file_path)

    def test_send_files(self):
        entity = 'foo'
        self.client.send_files(entity, [self.upload_file_path])
        self.client.send_file.assert_called_once_with(
            entity, self.upload_file_path, thumb=None, file_size=None,
            caption=os.path.basename(self.upload_file_path).split('.')[0], force_document=False,
            progress_callback=AnyArg(), attributes=[],
        )

    def test_send_files_data_loss(self):
        self.client.send_file.return_value.media.document.size = 200
        with self.assertRaises(TelegramUploadDataLoss):
            self.client.send_files('foo', [self.upload_file_path])
