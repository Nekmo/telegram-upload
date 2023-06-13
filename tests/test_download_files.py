import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock, call

from telegram_upload.download_files import pipe_file, CHUNK_FILE_SIZE, JoinStrategyBase, UnionJoinStrategy


class TestPipeFile(unittest.TestCase):
    @patch('builtins.open')
    def test_pipe(self, mock_open: MagicMock):
        mock_open.return_value.__enter__.return_value.read.side_effect = [b"foo", b"bar", b""]
        read_file_name = "read_file_name"
        write_file = BytesIO()
        pipe_file(read_file_name, write_file)
        write_file.seek(0)
        self.assertEqual(b"foobar", write_file.read())
        mock_open.assert_called_once_with(read_file_name, "rb")
        mock_open.return_value.__enter__.return_value.read.assert_has_calls([call(CHUNK_FILE_SIZE)] * 3)


class TestJoinStrategyBase(unittest.TestCase):
    def test_add_download_file(self):
        strategy = JoinStrategyBase()
        mock_download_file = MagicMock()
        with self.subTest("Test to add new download_file"):
            strategy.add_download_file(mock_download_file)
            self.assertEqual([mock_download_file], strategy.download_files)
        with self.subTest("Test to add existing download_file"):
            strategy.add_download_file(mock_download_file)
            self.assertEqual([mock_download_file], strategy.download_files)


class TestUnionJoinStrategy(unittest.TestCase):
    def test_get_base_name(self):
        with self.subTest("Test file with extension."):
            mock_download_file = MagicMock(file_name="file.tar.gz")
            base_name = UnionJoinStrategy.get_base_name(mock_download_file)
            self.assertEqual("file.tar", base_name)
        with self.subTest("Test file without extension."):
            mock_download_file = MagicMock(file_name="file")
            base_name = UnionJoinStrategy.get_base_name(mock_download_file)
            self.assertEqual("file", base_name)

    @patch("telegram_upload.download_files.JoinStrategyBase.add_download_file")
    def test_add_download_file(self, mock_add_download_file: MagicMock):
        mock_download_file = MagicMock(file_name="file.tar.gz")
        strategy = UnionJoinStrategy()
        strategy.add_download_file(mock_download_file)
        self.assertEqual("file.tar", strategy.base_name)
        mock_add_download_file.assert_called_once_with(mock_download_file)

    def test_is_part(self):
        mock_download_file = MagicMock(file_name="file.tar.gz")
        strategy = UnionJoinStrategy()
        strategy.base_name = "file.tar"
        self.assertTrue(strategy.is_part(mock_download_file))

    def test_is_applicable(self):
        strategy = UnionJoinStrategy()
        with self.subTest("Test applicable"):
            mock_download_file = MagicMock(file_name_extension="00")
            self.assertTrue(strategy.is_applicable(mock_download_file))
        with self.subTest("Test not applicable"):
            mock_download_file = MagicMock(file_name_extension="tar")
            self.assertFalse(strategy.is_applicable(mock_download_file))

    @patch('builtins.open')
    @patch('telegram_upload.download_files.os')
    @patch('telegram_upload.download_files.pipe_file')
    def test_join_download_files(self, mock_pipe_file: MagicMock, mock_os: MagicMock, mock_open: MagicMock):
        strategy = UnionJoinStrategy()
        download_files = [
            MagicMock(file_name="file.01", downloaded_file_name="file.01", file_name_extension="01"),
            MagicMock(file_name="file.00", downloaded_file_name="file.00", file_name_extension="00"),
        ]
        strategy.download_files = list(download_files)
        with self.subTest("Test successful join"):
            strategy.join_download_files()
            mock_pipe_file.assert_has_calls([
                call("file.00", mock_open.return_value.__enter__.return_value),
                call("file.01", mock_open.return_value.__enter__.return_value),
            ])
            mock_os.remove.assert_has_calls([call("file.00"), call("file.01")])
            mock_os.path.lexists.assert_has_calls([call("file.00"), call("file.01")], any_order=True)
            mock_open.assert_called_once_with("file", "wb")
        with self.subTest("Test join with missing files"):
            strategy.download_files = [download_files[0]]
            mock_open.reset_mock()
            strategy.join_download_files()
            mock_open.assert_not_called()
