import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call

from click.testing import CliRunner

from telegram_upload.caption_formatter import Duration, FileSize, FileMedia, FilePath, CHUNK_SIZE, CaptionFormatter, \
    test_caption_format


class TestDuration(unittest.TestCase):
    """Test the duration class."""

    def test_as_minutes(self):
        """Test the as_minutes attribute."""
        self.assertEqual(1, Duration(65).as_minutes)

    def test_as_hours(self):
        """Test the as_hours attribute."""
        self.assertEqual(1, Duration(65 * 60).as_hours)

    def test_as_days(self):
        """Test the as_days attribute."""
        self.assertEqual(1, Duration(65 * 60 * 24).as_days)

    def test_for_humans(self):
        """Test the for_humans attribute."""
        with self.subTest("Test zero seconds"):
            self.assertEqual("now", Duration(0).for_humans)
        with self.subTest("Test seconds"):
            self.assertEqual("1 second", Duration(1).for_humans)
        with self.subTest("Test two units"):
            self.assertEqual("1 minute and 1 second", Duration(61).for_humans)
        with self.subTest("Test all units"):
            self.assertEqual("3 years, 333 days, 21 hours, 33 minutes and 9 seconds", Duration(123456789).for_humans)

    def test_int(self):
        """Test the int cast."""
        self.assertEqual(123, int(Duration(123)))

    def test_str(self):
        """Test the str cast."""
        self.assertEqual("123", str(Duration(123)))


class TestFileSize(unittest.TestCase):
    """Test the FileSize class."""

    def test_as_kilobytes(self):
        """Test the as_kilobytes attribute."""
        self.assertEqual(1, FileSize(1000).as_kilobytes)

    def test_as_megabytes(self):
        """Test the as_megabytes attribute."""
        self.assertEqual(1, FileSize(1000 * 1000).as_megabytes)

    def test_as_gigabytes(self):
        """Test the as_gigabytes attribute."""
        self.assertEqual(1, FileSize(1000 * 1000 * 1000).as_gigabytes)

    def test_as_kibibytes(self):
        """Test the as_kibibytes attribute."""
        self.assertEqual(1, FileSize(1024).as_kibibytes)

    def test_as_mebibytes(self):
        """Test the as_mebibytes attribute."""
        self.assertEqual(1, FileSize(1024 * 1024).as_mebibytes)

    def test_as_gibibytes(self):
        """Test the as_gibibytes attribute."""
        self.assertEqual(1, FileSize(1024 * 1024 * 1024).as_gibibytes)

    def test_for_humans(self):
        """Test the for_humans attribute."""
        with self.subTest("Test zero bytes"):
            self.assertEqual("0.0 B", FileSize(0).for_humans)
        with self.subTest("Test bytes"):
            self.assertEqual("1.0 B", FileSize(1).for_humans)
        with self.subTest("Test all units"):
            self.assertEqual("1.1 GiB", FileSize(1234567890).for_humans)

    def test_int(self):
        """Test the int cast."""
        self.assertEqual(123, int(FileSize(123)))

    def test_str(self):
        """Test the str cast."""
        self.assertEqual("123", str(FileSize(123)))


class TestFileMedia(unittest.TestCase):
    """Test the FileMedia class."""

    @patch("telegram_upload.caption_formatter.video_metadata")
    def setUp(self, mock_video_metadata: MagicMock) -> None:
        """Set up the test case."""
        self.file_media = FileMedia("video.mkv")
        self.mock_metadata = self.file_media.metadata

    @unittest.skipIf(sys.version_info < (3, 8), "Unsupported in Python 3.7")
    def test_video_metadata(self):
        """Test the video_metadata attribute."""
        with self.subTest("Test mkv video"):
            self.mock_metadata.has.return_value = False
            self.mock_metadata._MultipleMetadata__groups._key_list = ["video meta", "audio meta"]
            video_metadata = self.file_media.video_metadata
            self.assertEqual(self.mock_metadata._MultipleMetadata__groups.__getitem__.return_value, video_metadata)
            self.mock_metadata._MultipleMetadata__groups.__getitem__.assert_called_once_with("video meta")
        with self.subTest("Test other formats"):
            del self.mock_metadata._MultipleMetadata__groups
            del self.file_media.__dict__["video_metadata"]  # clear cache
            self.assertEqual(self.mock_metadata, self.file_media.video_metadata)

    def test_duration(self):
        """Test the duration attribute."""
        self.mock_metadata.has.return_value = True
        self.mock_metadata.get.return_value.seconds = 123
        self.assertEqual(Duration(123).seconds, self.file_media.duration.seconds)
        self.mock_metadata.has.assert_called_once_with("duration")
        self.mock_metadata.get.assert_called_once_with("duration")

    @patch.object(FileMedia, "video_metadata")
    def test_get_video_metadata(self, mock_video_metadata: MagicMock):
        """Test the _get_video_metadata method."""
        with self.subTest("Test with video metadata"):
            self.assertEqual(mock_video_metadata.get.return_value, self.file_media._get_video_metadata("width"))
            mock_video_metadata.get.assert_called_once_with("width")
            mock_video_metadata.has.assert_called_once_with("width")
        mock_video_metadata.reset_mock()
        with self.subTest("Test without video metadata field"):
            mock_video_metadata.has.return_value = False
            self.assertIsNone(self.file_media._get_video_metadata("width"))
            mock_video_metadata.get.assert_not_called()
            mock_video_metadata.has.assert_called_once_with("width")
        mock_video_metadata.reset_mock()
        with self.subTest("Test without video metadata"):
            mock_video_metadata.__bool__.return_value = False
            mock_video_metadata.get.assert_not_called()
            mock_video_metadata.has.assert_not_called()

    def test_metadata(self):
        """Test the _get_metadata method."""
        with self.subTest("Test with metadata"):
            self.assertEqual(self.mock_metadata.get.return_value, self.file_media._get_metadata("title"))
            self.mock_metadata.get.assert_called_once_with("title")
            self.mock_metadata.has.assert_called_once_with("title")
        self.mock_metadata.reset_mock()
        with self.subTest("Test without metadata field"):
            self.mock_metadata.has.return_value = False
            self.assertIsNone(self.file_media._get_metadata("title"))
            self.mock_metadata.get.assert_not_called()
            self.mock_metadata.has.assert_called_once_with("title")
        self.mock_metadata.reset_mock()
        with self.subTest("Test without metadata"):
            self.mock_metadata.__bool__.return_value = False
            self.mock_metadata.get.assert_not_called()
            self.mock_metadata.has.assert_not_called()

    @patch.object(FileMedia, "_get_video_metadata")
    def test_width(self, mock_get_video_metadata: MagicMock):
        """Test the width attribute."""
        self.assertEqual(mock_get_video_metadata.return_value, self.file_media.width)
        mock_get_video_metadata.assert_called_once_with("width")

    @patch.object(FileMedia, "_get_video_metadata")
    def test_height(self, mock_get_video_metadata: MagicMock):
        """Test the height attribute."""
        self.assertEqual(mock_get_video_metadata.return_value, self.file_media.height)
        mock_get_video_metadata.assert_called_once_with("height")

    @patch.object(FileMedia, "_get_metadata")
    def test_title(self, mock_get_metadata: MagicMock):
        """Test the title attribute."""
        self.assertEqual(mock_get_metadata.return_value, self.file_media.title)
        mock_get_metadata.assert_called_once_with("title")

    @patch.object(FileMedia, "_get_metadata")
    def test_artist(self, mock_get_metadata: MagicMock):
        """Test the artist attribute."""
        self.assertEqual(mock_get_metadata.return_value, self.file_media.artist)
        mock_get_metadata.assert_called_once_with("artist")

    @patch.object(FileMedia, "_get_metadata")
    def test_album(self, mock_get_metadata: MagicMock):
        """Test the album attribute."""
        self.assertEqual(mock_get_metadata.return_value, self.file_media.album)
        mock_get_metadata.assert_called_once_with("album")

    @patch.object(FileMedia, "_get_metadata")
    def test_producer(self, mock_get_metadata: MagicMock):
        """Test the producer attribute."""
        self.assertEqual(mock_get_metadata.return_value, self.file_media.producer)
        mock_get_metadata.assert_called_once_with("producer")


class TestFilePath(unittest.TestCase):
    """Test the FilePath class."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.file_path = FilePath("file.txt")

    @patch("builtins.open")
    def test_calculate_hash(self, mock_open: MagicMock):
        """Test the calculate_hash method."""
        mock_open.return_value.__enter__.return_value.read.side_effect = [b"abc", b"def"]
        mock_hash_calculator = MagicMock()
        self.assertEqual(
            mock_hash_calculator.hexdigest.return_value, self.file_path._calculate_hash(mock_hash_calculator)
        )
        mock_open.assert_called_once_with("file.txt", "rb")
        mock_open.return_value.__enter__.return_value.read.assert_has_calls([call(CHUNK_SIZE)] * 3)
        mock_hash_calculator.update.assert_has_calls([call(b"abc"), call(b"def")])

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_md5(self, mock_hashlib: MagicMock):
        """Test the md5 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.md5)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.md5.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha1(self, mock_hashlib: MagicMock):
        """Test the sha1 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha1)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha1.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha224(self, mock_hashlib: MagicMock):
        """Test the sha224 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha224)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha224.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha256(self, mock_hashlib: MagicMock):
        """Test the sha256 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha256)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha256.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha384(self, mock_hashlib: MagicMock):
        """Test the sha384 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha384)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha384.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha512(self, mock_hashlib: MagicMock):
        """Test the sha512 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha512)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha512.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha3_224(self, mock_hashlib: MagicMock):
        """Test the sha3_224 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha3_224)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha3_224.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha3_256(self, mock_hashlib: MagicMock):
        """Test the sha3_256 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha3_256)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha3_256.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha3_384(self, mock_hashlib: MagicMock):
        """Test the sha3_384 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha3_384)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha3_384.return_value)

    @patch("telegram_upload.caption_formatter.hashlib")
    def test_sha3_512(self, mock_hashlib: MagicMock):
        """Test the sha3_512 attribute."""
        mock_calculate_hash = MagicMock()
        self.file_path._calculate_hash = mock_calculate_hash
        self.assertEqual(mock_calculate_hash.return_value, self.file_path.sha3_512)
        mock_calculate_hash.assert_called_once_with(mock_hashlib.sha3_512.return_value)

    @patch("builtins.open", mock_open(read_data=b"abcdef"))
    def test_crc32(self):
        """Test the crc32 attribute."""
        self.assertEqual("4B8E39EF", self.file_path.crc32)

    @patch("builtins.open", mock_open(read_data=b"abcdef"))
    def test_adler32(self):
        """Test the adler32 attribute."""
        self.assertEqual("081e0256", self.file_path.adler32)

    @patch("telegram_upload.caption_formatter.os.stat")
    def test_file_stat(self, mock_os_stat: MagicMock):
        """Test the file_stat attribute."""
        self.assertEqual(mock_os_stat.return_value, self.file_path._file_stat)
        mock_os_stat.assert_called_once_with("file.txt")

    @patch("telegram_upload.caption_formatter.datetime")
    def test_ctime(self, mock_datetime: MagicMock):
        """Test the ctime attribute."""
        mock_file_stat = MagicMock()
        self.file_path._file_stat = mock_file_stat
        self.assertEqual(mock_datetime.datetime.fromtimestamp.return_value, self.file_path.ctime)
        mock_datetime.datetime.fromtimestamp.assert_called_once_with(mock_file_stat.st_ctime)

    @patch("telegram_upload.caption_formatter.datetime")
    def test_mtime(self, mock_datetime: MagicMock):
        """Test the mtime attribute."""
        mock_file_stat = MagicMock()
        self.file_path._file_stat = mock_file_stat
        self.assertEqual(mock_datetime.datetime.fromtimestamp.return_value, self.file_path.mtime)
        mock_datetime.datetime.fromtimestamp.assert_called_once_with(mock_file_stat.st_mtime)

    @patch("telegram_upload.caption_formatter.datetime")
    def test_atime(self, mock_datetime: MagicMock):
        """Test the atime attribute."""
        mock_file_stat = MagicMock()
        self.file_path._file_stat = mock_file_stat
        self.assertEqual(mock_datetime.datetime.fromtimestamp.return_value, self.file_path.atime)
        mock_datetime.datetime.fromtimestamp.assert_called_once_with(mock_file_stat.st_atime)

    @patch("telegram_upload.caption_formatter.FileSize")
    def test_size(self, mock_file_size: MagicMock):
        """Test the size attribute."""
        mock_file_stat = MagicMock()
        self.file_path._file_stat = mock_file_stat
        self.assertEqual(mock_file_size.return_value, self.file_path.size)
        mock_file_size.assert_called_once_with(mock_file_stat.st_size)

    @patch("telegram_upload.caption_formatter.FileMedia")
    def test_media(self, mock_file_media: MagicMock):
        """Test the media attribute."""
        self.assertEqual(mock_file_media.return_value, self.file_path.media)
        mock_file_media.assert_called_once_with(str(self.file_path))

    @patch("telegram_upload.caption_formatter.mimetypes")
    def test_mimetype(self, mock_mimetypes: MagicMock):
        """Test the mimetype attribute."""
        self.assertEqual(mock_mimetypes.guess_type.return_value.__getitem__.return_value, self.file_path.mimetype)
        mock_mimetypes.guess_type.assert_called_once_with(str(self.file_path))
        mock_mimetypes.guess_type.return_value.__getitem__.assert_called_once_with(0)
        mock_mimetypes.init.assert_called_once_with()

    def test_suffixes(self):
        """Test the suffixes attribute."""
        file_path = FilePath("file.tar.gz")
        self.assertEqual(".tar.gz", file_path.suffixes)

    def test_absolute(self):
        """Test the absolute attribute."""
        file_path = FilePath("/home/user/file.tar.gz")
        self.assertEqual("/home/user/file.tar.gz", str(file_path.absolute))

    @patch("telegram_upload.caption_formatter.Path.cwd")
    def test_relative(self, mock_cwd: MagicMock):
        """Test the relative attribute."""
        mock_cwd.return_value = Path("/home/user")
        file_path = FilePath("/home/user/file.tar.gz")
        self.assertEqual("file.tar.gz", str(file_path.relative))


class TestCaptionFormatter(unittest.TestCase):
    """Test the CaptionFormatter class."""

    def test_get_field(self):
        """Test the get_field method."""
        with self.subTest("Test with a valid key"):
            self.assertEqual(("value", "key"), CaptionFormatter().get_field("key", (), {"key": "value"}))
        with self.subTest("Test with an undefined key"):
            self.assertEqual(("{key}", "key"), CaptionFormatter().get_field("key", (), {}))
        with self.subTest("Test with a private key"):
            obj = MagicMock()
            obj._private = 123
            self.assertEqual(("{obj._private}", "obj"), CaptionFormatter().get_field("obj._private", (), obj))
        with self.subTest("Test with a method"):
            self.assertEqual(("Value", "key"), CaptionFormatter().get_field("key.title", (), {"key": "value"}))
        with self.subTest("Test with a unsupported key"):
            self.assertEqual(("{key}", "key"), CaptionFormatter().get_field("key", (), {"key": []}))

    def test_format(self):
        """Test the format method."""
        with self.subTest("Test with a valid key"):
            self.assertEqual("Value", CaptionFormatter().format("{key}", key="Value"))
        with self.subTest("Test with a malformed key"):
            self.assertEqual("{key", CaptionFormatter().format("{key", key="Value"))


class TestTestCaptionFormat(unittest.TestCase):
    """Test the test_caption_format function."""

    @patch("telegram_upload.caption_formatter.print")
    def test_test_caption_format(self, mock_print: MagicMock):
        """Test the test_caption_format function."""
        runner = CliRunner()
        result = runner.invoke(test_caption_format, [__file__, "{file.stem}"])
        self.assertEqual(0, result.exit_code)
        mock_print.assert_called_once_with(__file__.split("/")[-1].split(".")[0])
