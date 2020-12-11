import unittest

from telegram_upload.utils import sizeof_fmt


class TestSizeOfFmt(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(sizeof_fmt(1023), '1023B')

    def test_kibibytes(self):
        self.assertEqual(sizeof_fmt(2400), '2.3KiB')

    def test_exact_mebibytes(self):
        self.assertEqual(sizeof_fmt((1024 ** 2) * 3), '3.0MiB')
