import unittest
from unittest.mock import patch

from telegram_upload.config import default_config, CONFIG_FILE


class TestDefaultConfig(unittest.TestCase):
    @patch('telegram_upload.config.os.path.lexists', return_value=True)
    def test_exists(self, m):
        self.assertEqual(default_config(), CONFIG_FILE)
        m.assert_called_once()
