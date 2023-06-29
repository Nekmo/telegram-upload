import unittest
from unittest.mock import MagicMock, patch

from telegram_upload.upload_files import File


class TestFile(unittest.TestCase):
    """Test File class."""

    @patch("telegram_upload.upload_files.File.__init__", return_value=None)
    def setUp(self, mock_file_init: MagicMock) -> None:
        """Set up test."""
        self.max_caption_length = 256
        self.mock_client = MagicMock(max_caption_length=self.max_caption_length)
        self.file = File()
        self.file.client = self.mock_client
        self.file.path = "path/to/file.txt"

    def test_file_caption(self):
        """Test file_caption method."""
        with self.subTest("Test file_caption with caption"):
            self.file._caption = "test {file.stem}"
            self.assertEqual("test file", self.file.file_caption)
        with self.subTest("Test file_caption without caption"):
            self.file._caption = None
            self.assertEqual("path/to/file.txt", self.file.path)
        with self.subTest("Test file_caption with long caption"):
            self.file._caption = "a" * (self.max_caption_length + 1)
            self.assertEqual(self.max_caption_length, len(self.file.file_caption))
            self.assertTrue(self.file.file_caption.endswith("..."))
