import unittest
from unittest.mock import patch, Mock

from telegram_upload.files import get_file_attributes


class TestGetFileAttributes(unittest.TestCase):
    def test_not_video(self):
        self.assertEqual(get_file_attributes('foo.png'), [])

    @patch('telegram_upload.files.video_metadata')
    def test_video(self, m_video_metadata):
        m_video_metadata.return_value.has.return_value = True
        duration = Mock()
        duration.seconds = 1000
        m_video_metadata.return_value.get.side_effect = [
            duration, 1920, 1080
        ]
        attrs = get_file_attributes('foo.mp4')
        self.assertEqual(attrs[0].w, 1920)
        self.assertEqual(attrs[0].h, 1080)
        self.assertEqual(attrs[0].duration, 1000)
