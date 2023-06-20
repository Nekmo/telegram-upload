import json
import os
import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock, call

from telegram_upload.client.telegram_upload_client import TelegramUploadClient
from telegram_upload.exceptions import TelegramUploadDataLoss, MissingFileError
from telegram_upload.upload_files import File

CONFIG_DATA = {'api_hash': '', 'api_id': ''}

directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../')


class AnyArg(object):
    """https://stackoverflow.com/questions/20428750/pythons-assert-called-with-is-there-a-wildcard-character"""
    def __eq__(a, b):
        return True


class TestTelegramUploadClient(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_upload_client.TelegramClient.__init__', return_value=None)
    def setUp(self, m1) -> None:
        self.upload_file_path = os.path.abspath(os.path.join(directory, 'logo.png'))
        self.client = TelegramUploadClient(Mock(), Mock(), Mock())
        self.client.send_file = Mock()
        self.client.send_file.return_value.media.document.size = os.path.getsize(self.upload_file_path)

    @patch("telegram_upload.client.telegram_upload_client.TelegramUploadClient.forward_messages")
    def test_forward_to(self, mock_forward_messages: MagicMock):
        mock_message = MagicMock()
        mock_destinations = [MagicMock(), MagicMock()]
        self.client.forward_to(mock_message, mock_destinations)
        mock_forward_messages.assert_has_calls([
            call(mock_destinations[0], [mock_message]),
            call(mock_destinations[1], [mock_message]),
        ])

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
