import os
import unittest
from unittest.mock import patch, Mock, MagicMock

from telegram_upload.client.telegram_manager_client import USER_MAX_FILE_SIZE
from telegram_upload.exceptions import TelegramInvalidFile
from telegram_upload.upload_files import get_file_attributes, RecursiveFiles, NoDirectoriesFiles, NoLargeFiles, \
    SplitFiles, SplitFile


class TestGetFileAttributes(unittest.TestCase):
    def test_not_video(self):
        self.assertEqual(get_file_attributes('foo.png'), [])

    @patch('telegram_upload.upload_files.video_metadata')
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
    @patch('telegram_upload.upload_files.scantree', return_value=[])
    @patch('telegram_upload.upload_files.os.path.isdir', return_value=False)
    def test_one_file(self, m1, m2):
        self.assertEqual(list(RecursiveFiles(MagicMock(), ['foo'])), ['foo'])

    @patch('telegram_upload.upload_files.scantree')
    @patch('telegram_upload.upload_files.os.path.isdir', return_value=True)
    def test_directory(self, m1, m2):
        directory = Mock()
        directory.is_dir.side_effect = [True, False]
        file = Mock()
        file.is_dir.return_value = False
        side_effect = [file] * 3
        m2.return_value = side_effect
        self.assertEqual(list(RecursiveFiles(MagicMock(), ['foo'])), [x.path for x in side_effect])


class TestNoDirectoriesFiles(unittest.TestCase):
    @patch('telegram_upload.upload_files.scantree', return_value=[])
    @patch('telegram_upload.upload_files.os.path.isdir', return_value=False)
    def test_one_file(self, m1, m2):
        self.assertEqual(list(NoDirectoriesFiles(MagicMock(), ['foo'])), ['foo'])

    @patch('telegram_upload.upload_files.os.path.isdir', return_value=True)
    def test_directory(self, m):
        with self.assertRaises(TelegramInvalidFile):
            next(NoDirectoriesFiles(MagicMock(), ['foo']))


class TestNoLargeFiles(unittest.TestCase):
    @patch('telegram_upload.upload_files.os.path.getsize', return_value=USER_MAX_FILE_SIZE - 1)
    @patch('telegram_upload.upload_files.File')
    def test_small_file(self, m1, m2):
        self.assertEqual(len(list(NoLargeFiles(MagicMock(max_file_size=USER_MAX_FILE_SIZE), ['foo']))), 1)

    @patch('telegram_upload.upload_files.os.path.getsize', return_value=USER_MAX_FILE_SIZE + 1)
    def test_big_file(self, m):
        with self.assertRaises(TelegramInvalidFile):
            next(NoLargeFiles(MagicMock(max_file_size=1024 ** 3), ['foo']))


class TestSplitFile(unittest.TestCase):
    def test_file(self):
        this_file = os.path.abspath(__file__)
        size = os.path.getsize(this_file)
        file0 = SplitFile(MagicMock(), this_file, size - 100, 'test.py.00')
        file1 = SplitFile(MagicMock(), this_file, 100, 'test.py.01')
        file1.seek(size - 100, split_seek=True)
        with open(this_file, 'rb') as f:
            content = f.read()
        self.assertEqual(file0.readall() + file1.readall(), content)
        self.assertEqual(file0.file_name, 'test.py.00')
        self.assertEqual(file1.file_size, 100)
        file0.close()
        file1.close()


class TestSplitFiles(unittest.TestCase):
    @patch('telegram_upload.upload_files.os.path.getsize', return_value=USER_MAX_FILE_SIZE - 1)
    @patch('telegram_upload.upload_files.File')
    def test_small_file(self, m1, m2):
        self.assertEqual(len(list(SplitFiles(MagicMock(max_file_size=USER_MAX_FILE_SIZE), ['foo']))), 1)

    @patch('telegram_upload.upload_files.os.path.getsize', return_value=USER_MAX_FILE_SIZE + 1000)
    @patch('telegram_upload.upload_files.SplitFile.__init__', return_value=None)
    @patch('telegram_upload.upload_files.SplitFile.seek')
    def test_big_file(self, m_getsize, m_init, m_seek):
        mock_client = MagicMock(max_file_size=USER_MAX_FILE_SIZE)
        files = list(SplitFiles(mock_client, ['foo']))
        self.assertEqual(len(files), 2)
        self.assertEqual(m_init.call_args_list[0][0], (mock_client, 'foo', USER_MAX_FILE_SIZE, 'foo.00'))
        self.assertEqual(m_init.call_args_list[1][0], (mock_client, 'foo', 1000, 'foo.01'))
