import unittest
from unittest.mock import patch, Mock

from telegram_upload.exceptions import TelegramInvalidFile
from telegram_upload.files import get_file_attributes, RecursiveFiles, NoDirectoriesFiles, MAX_FILE_SIZE, \
    NoLargeFiles


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


class TestRecursiveFiles(unittest.TestCase):
    @patch('telegram_upload.files.scantree', return_value=[])
    @patch('telegram_upload.files.os.path.isdir', return_value=False)
    def test_one_file(self, m1, m2):
        self.assertEqual(list(RecursiveFiles(['foo'])), ['foo'])

    @patch('telegram_upload.files.scantree')
    @patch('telegram_upload.files.os.path.isdir', return_value=True)
    def test_directory(self, m1, m2):
        directory = Mock()
        directory.is_dir.side_effect = [True, False]
        file = Mock()
        file.is_dir.return_value = False
        side_effect = [file] * 3
        m2.return_value = side_effect
        self.assertEqual(list(RecursiveFiles(['foo'])), [x.path for x in side_effect])


class TestNoDirectoriesFiles(unittest.TestCase):
    @patch('telegram_upload.files.scantree', return_value=[])
    @patch('telegram_upload.files.os.path.isdir', return_value=False)
    def test_one_file(self, m1, m2):
        self.assertEqual(list(NoDirectoriesFiles(['foo'])), ['foo'])

    @patch('telegram_upload.files.os.path.isdir', return_value=True)
    def test_directory(self, m):
        with self.assertRaises(TelegramInvalidFile):
            next(NoDirectoriesFiles(['foo']))


class TestNoLargeFiles(unittest.TestCase):
    @patch('telegram_upload.files.os.path.getsize', return_value=MAX_FILE_SIZE - 1)
    def test_small_file(self, m):
        self.assertEqual(list(NoLargeFiles(['foo'])), ['foo'])

    @patch('telegram_upload.files.os.path.getsize', return_value=MAX_FILE_SIZE + 1)
    def test_big_file(self, m):
        with self.assertRaises(TelegramInvalidFile):
            next(NoLargeFiles(['foo']))
