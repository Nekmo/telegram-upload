import asyncio
import json
import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock, call

from telethon.tl.types import DocumentAttributeFilename

from telegram_upload.client.telegram_download_client import TelegramDownloadClient
from telegram_upload.exceptions import TelegramUploadNoSpaceError

CONFIG_DATA = {'api_hash': '', 'api_id': ''}


class TestTelegramDownloadClient(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data=json.dumps(CONFIG_DATA)))
    @patch('telegram_upload.client.telegram_download_client.TelegramClient.__init__', return_value=None)
    def setUp(self, m1) -> None:
        self.client = TelegramDownloadClient(Mock(), Mock(), Mock())

    def test_find_files(self):
        entity = "entity"
        mock_iter_messages = MagicMock()
        mock_iter_messages.return_value = [
            MagicMock(**{"document": MagicMock()}),
            MagicMock(**{"document": MagicMock()}),
            MagicMock(**{"document": None}),
        ]
        self.client.iter_messages = mock_iter_messages
        files = list(self.client.find_files(entity))
        self.assertEqual(mock_iter_messages.return_value[0:2], files)

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

    @patch("telegram_upload.client.telegram_download_client.TelegramDownloadClient._iter_download_chunk_tasks")
    @patch("telegram_upload.client.telegram_download_client.asyncio.wait")
    def test_download_file(self, mock_wait: MagicMock, mock_iter_download_chunk_tasks: MagicMock):
        mock_iter_download_chunk_tasks.return_value = [
            MagicMock(**{"result.return_value": f"foo{i}".encode("utf-8")}) for i in range(2)
        ]
        mock_input_location = MagicMock()
        mock_file = MagicMock()
        mock_progress_callback = MagicMock()
        file_size = 2048
        part_size = 4
        self.client.download_file(
            mock_input_location, mock_file, file_size=file_size, part_size_kb=part_size,
            progress_callback=mock_progress_callback,
        )
        mock_file.write.assert_called_once_with(b"foo0foo1")
        mock_iter_download_chunk_tasks.assert_called_once_with(
            mock_input_location, part_size * 1024, None, None, file_size,
        )
        mock_wait.assert_called_once_with(mock_iter_download_chunk_tasks.return_value)

    @patch("telegram_upload.client.telegram_download_client.TelegramDownloadClient.loop")
    @patch("telegram_upload.client.telegram_download_client.TelegramDownloadClient._iter_download")
    def test_iter_download_chunk_tasks(self, mock_iter_download: MagicMock, mock_loop: MagicMock):
        mock_input_location = MagicMock()
        part_size = 1024
        dc_id = 1
        msg_data = "msg_data"
        file_size = 2048
        tasks = list(self.client._iter_download_chunk_tasks(
            mock_input_location, part_size, dc_id, msg_data, file_size
        ))
        self.assertEqual([mock_loop.create_task.return_value] * 2, tasks)
        mock_iter_download.assert_has_calls([
            call(mock_input_location, offset=0, request_size=part_size, dc_id=dc_id, msg_data=msg_data),
            call(mock_input_location, offset=1024, request_size=part_size, dc_id=dc_id, msg_data=msg_data),
        ], any_order=True)
