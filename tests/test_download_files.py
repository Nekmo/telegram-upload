import sys
import unittest
from io import BytesIO
from unittest.mock import patch, MagicMock, call

from telethon.tl.types import DocumentAttributeFilename

from telegram_upload.download_files import pipe_file, CHUNK_FILE_SIZE, JoinStrategyBase, UnionJoinStrategy, \
    get_join_strategy, DownloadFile, KeepDownloadSplitFiles, JoinDownloadSplitFiles


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


class TestGetJoinStrategy(unittest.TestCase):
    def test_get_join_strategy(self):
        mock_download_file = MagicMock()
        strategies = [MagicMock()]
        with patch("telegram_upload.download_files.JOIN_STRATEGIES", strategies):
            strategy = get_join_strategy(mock_download_file)
            self.assertEqual(strategies[0].return_value, strategy)
            strategies[0].is_applicable.assert_called_once_with(mock_download_file)
            strategies[0].return_value.add_download_file.assert_called_once_with(mock_download_file)


class TestDownloadFile(unittest.TestCase):
    def test_set_download_file_name(self):
        download_file = DownloadFile(MagicMock())
        download_file_name = "download_file_name"
        download_file.set_download_file_name(download_file_name)
        self.assertEqual(download_file_name, download_file.downloaded_file_name)

    def test_filename_attr(self):
        with self.subTest("Found attribute"):
            attribute = DocumentAttributeFilename("file_name")
            mock_download_file = MagicMock(**{'document.attributes': [attribute]})
            download_file = DownloadFile(mock_download_file)
            self.assertEqual(attribute, download_file.filename_attr)
        with self.subTest("Missing attribute"):
            mock_download_file = MagicMock(**{'document.attributes': []})
            download_file = DownloadFile(mock_download_file)
            self.assertIsNone(download_file.filename_attr)

    @unittest.skipIf(sys.version_info < (3, 8), "Unsupported in Python 3.7")
    def test_file_name(self):
        file_name = "file_name"
        download_file = DownloadFile(MagicMock())
        with patch.object(download_file, 'filename_attr', file_name=file_name), self.subTest("Return file name"):
            self.assertEqual(file_name, download_file.file_name)
        download_file = DownloadFile(MagicMock(**{'document.attributes': []}))
        with self.subTest("Return unknown"):
            self.assertEqual("Unknown", download_file.file_name)

    @unittest.skipIf(sys.version_info < (3, 8), "Unsupported in Python 3.7")
    def test_file_name_extension(self):
        file_name = "file_name.tar"
        download_file = DownloadFile(MagicMock())
        with patch.object(download_file, 'filename_attr', file_name=file_name), \
                self.subTest("Return extension file name"):
            self.assertEqual("tar", download_file.file_name_extension)
        download_file = DownloadFile(MagicMock(**{'document.attributes': []}))
        with self.subTest("Empty extension"):
            self.assertEqual("", download_file.file_name_extension)

    def test_document(self):
        mock_mesage = MagicMock()
        download_file = DownloadFile(mock_mesage)
        self.assertEqual(mock_mesage.document, download_file.document)

    def test_size(self):
        mock_mesage = MagicMock()
        download_file = DownloadFile(mock_mesage)
        self.assertEqual(mock_mesage.document.size, download_file.document.size)

    def test_eq(self):
        mock_mesage = MagicMock()
        download_file = DownloadFile(mock_mesage)
        download_file2 = DownloadFile(mock_mesage)
        self.assertEqual(download_file, download_file2)


class TestKeepDownloadSplitFiles(unittest.TestCase):
    def test_get_iterator(self):
        mock_messages = [MagicMock()]
        keep_download_split_files = KeepDownloadSplitFiles(mock_messages)
        download_files = list(keep_download_split_files)
        self.assertIsInstance(download_files[0], DownloadFile)
        self.assertEqual(mock_messages[0], download_files[0].message)


class TestJoinDownloadSplitFiles(unittest.TestCase):
    @patch("telegram_upload.download_files.get_join_strategy")
    def test_get_iterator_without_strategy(self, mock_get_join_strategy: MagicMock):
        """Test a download file without a valid strategy. The file is outside the supported
        files to unzip.
        """
        mock_messages = [MagicMock()]
        mock_get_join_strategy.return_value = False
        join_download_split_files = JoinDownloadSplitFiles(mock_messages)
        download_files = list(join_download_split_files)
        self.assertIsInstance(download_files[0], DownloadFile)
        self.assertEqual(mock_messages[0], download_files[0].message)

    @patch("telegram_upload.download_files.get_join_strategy")
    def test_get_iterator_with_strategy(self, mock_get_join_strategy: MagicMock):
        """Test two related download files with a valid strategy. The files are unzipped."""
        mock_messages = [MagicMock(), MagicMock()]
        mock_strategy = MagicMock()
        mock_get_join_strategy.return_value = mock_strategy
        join_download_split_files = JoinDownloadSplitFiles(mock_messages)
        download_files = list(join_download_split_files)
        self.assertIsInstance(download_files[0], DownloadFile)
        self.assertEqual(mock_messages[0], download_files[0].message)
        mock_strategy.add_download_file.assert_called_once_with(download_files[1])
        mock_strategy.join_download_files.assert_called_once()

    @patch("telegram_upload.download_files.get_join_strategy")
    def test_get_iterator_with_strategy_and_other_file(self, mock_get_join_strategy: MagicMock):
        """Test two related download files with a valid strategy, and other unsupported file.
        Unzip the latest download file after detect an unsupported file.
        """
        mock_messages = [MagicMock(), MagicMock(), MagicMock()]
        mock_strategy = MagicMock()
        mock_strategy.is_part.side_effect = [True, False, False]
        mock_get_join_strategy.side_effect = [mock_strategy, False]
        join_download_split_files = JoinDownloadSplitFiles(mock_messages)
        download_files = list(join_download_split_files)
        self.assertIsInstance(download_files[0], DownloadFile)
        self.assertEqual(mock_messages[0], download_files[0].message)
        mock_strategy.add_download_file.assert_called_once_with(download_files[1])
        mock_strategy.join_download_files.assert_called_once()
