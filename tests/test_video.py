import unittest
from unittest.mock import patch

from telegram_upload.exceptions import ThumbVideoError
from telegram_upload.video import call_ffmpeg, get_video_size, get_video_thumb


class TestcallFfmpeg(unittest.TestCase):
    @patch('telegram_upload.video.subprocess.Popen', side_effect=FileNotFoundError)
    def test_ffmpeg(self, m):
        with self.assertRaises(ThumbVideoError):
            call_ffmpeg([])


class TestGetVideoSize(unittest.TestCase):
    @patch('telegram_upload.video.call_ffmpeg')
    def test_size(self, m):
        m.return_value.communicate.return_value = (b'', b': Video: 1920x1080')
        self.assertEqual(get_video_size('foo'), [1920, 1080])

    @patch('telegram_upload.video.call_ffmpeg')
    def test_invalid_output(self, m):
        m.return_value.communicate.return_value = (b'', b'foo')
        self.assertIsNone(get_video_size('foo'))


class TestGetVideoThumb(unittest.TestCase):
    @patch('telegram_upload.video.video_metadata')
    @patch('telegram_upload.video.get_video_size', return_value=[1920, 1080])
    @patch('telegram_upload.video.call_ffmpeg')
    def test_video_thumb(self, m1, m2, m3):
        get_video_thumb('foo')

    @patch('telegram_upload.video.video_metadata')
    def test_no_ratio(self, m):
        with self.assertRaises(ThumbVideoError):
            get_video_thumb('foo')
