import unittest
from unittest.mock import patch, MagicMock

from telegram_upload.caption_formatter import Duration, FileSize, FileMedia


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
