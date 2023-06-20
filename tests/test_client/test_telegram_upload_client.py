import json
import os
import sys
import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock, call, AsyncMock

from telethon import types

from telegram_upload.client.telegram_upload_client import TelegramUploadClient
from telegram_upload.exceptions import TelegramUploadDataLoss, MissingFileError
from telegram_upload.upload_files import File

CONFIG_DATA = {'api_hash': '', 'api_id': ''}

directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../')


class AnyArg(object):
    """https://stackoverflow.com/questions/20428750/pythons-assert-called-with-is-there-a-wildcard-character"""
    def __eq__(a, b):
        return True


class TestTelegramUploadClient(unittest.IsolatedAsyncioTestCase):
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

    async def test_send_album_media(self):
        self.client.get_input_entity = AsyncMock()
        self.client._call = AsyncMock()
        self.client._sender = MagicMock()
        self.client._get_response_message = MagicMock()
        entity = "entity"
        mock_media = [MagicMock(), MagicMock()]
        response_message = await self.client._send_album_media(entity, mock_media)
        self.assertEqual(self.client._get_response_message.return_value, response_message)
        self.client._get_response_message.assert_called_once_with(
            [m.random_id for m in mock_media], self.client._call.return_value,
            self.client.get_input_entity.return_value,
        )

    @patch('telegram_upload.client.telegram_upload_client.TelegramUploadClient.send_files')
    @patch('telegram_upload.client.telegram_upload_client.TelegramUploadClient._send_album_media')
    @unittest.skipIf(sys.version_info < (3, 8), "TypeError: An asyncio.Future, a coroutine or an awaitable is required")
    def test_send_files_as_album(self, mock_send_album_media: MagicMock, mock_send_files: MagicMock):
        entity = "entity"
        mock_files = [MagicMock(), MagicMock()]
        self.client.send_files_as_album(entity, mock_files)
        mock_send_files.assert_called_once_with(
            entity, tuple(mock_files), False, False, (), send_as_media=True
        )
        mock_send_album_media.assert_called_once_with(entity, mock_send_files.return_value)

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

    @patch('telegram_upload.client.telegram_upload_client.utils')
    async def test_send_media(self, mock_utils: MagicMock):
        mock_utils.get_appropriated_part_size.return_value = 512
        self.client.get_input_entity = AsyncMock()
        self.client._log = AsyncMock()
        self.client._call = AsyncMock()
        self.client._sender = MagicMock()
        entity = 'entity'
        mock_progress = MagicMock()
        file = File(self.upload_file_path)
        with patch('telegram_upload.client.telegram_upload_client.isinstance', return_value=True), \
                self.subTest("Test photo"):
            await self.client._send_media(entity, file, mock_progress)
        isinstance_result = {types.InputMediaUploadedPhoto: False, types.InputMediaUploadedDocument: True}
        with patch('telegram_upload.client.telegram_upload_client.isinstance',
                   side_effect=lambda obj, target: isinstance_result.get(target, isinstance(obj, target))), \
                self.subTest("Test Document"):
            await self.client._send_media(entity, file, mock_progress)
        # self.client.send_file.assert_called_once_with(
        #     entity, file, thumb=None, file_size=file.file_size,
        #     caption=os.path.basename(self.upload_file_path).split('.')[0], force_document=False,
        #     progress_callback=AnyArg(), attributes=[],
        # )
