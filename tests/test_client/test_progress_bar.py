import unittest
from unittest.mock import patch, MagicMock

from telegram_upload.client.progress_bar import get_progress_bar


class TestGetProgressBar(unittest.TestCase):
    @patch("telegram_upload.client.progress_bar.click")
    def test_get_progress_bar(self, mock_click: MagicMock):
        action = "action"
        file = "file"
        length = 100
        current = 10
        progress, bar = get_progress_bar(action, file, length)
        progress(current, None)
        progress(5, None)  # The bar should not go back
        mock_click.progressbar.assert_called_once_with(label=f"{action} \"{file}\"", length=length)
        self.assertEqual(0, mock_click.progressbar.return_value.pos)
        mock_click.progressbar.return_value.update.assert_called_once_with(current)
        self.assertEqual(mock_click.progressbar.return_value, bar)
