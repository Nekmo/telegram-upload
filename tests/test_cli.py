import sys
import unittest
from unittest.mock import patch

from telegram_upload.cli import show_checkboxlist, show_radiolist
from telegram_upload.utils import async_to_sync


class TestShowCheckboxList(unittest.TestCase):
    @unittest.skipIf(sys.version_info < (3, 8), "Python 3.8 is required")
    @patch('prompt_toolkit.application.application.Application.run_async')
    def test_show_checkbox_list(self, m):
        async def aiterator():
            iterator = iter([(x, x) for x in map(str, range(10))])
            for item in iterator:
                yield item

        async_to_sync(show_checkboxlist(aiterator()))

    @patch('click.echo')
    def test_empty(self, m):
        async def aiterator():
            for item in []:
                yield item

        async_to_sync(show_checkboxlist(aiterator()))
        m.assert_called_once()


class TestShowRadioList(unittest.TestCase):
    @unittest.skipIf(sys.version_info < (3, 8), "Python 3.8 is required")
    @patch('prompt_toolkit.application.application.Application.run_async')
    def test_show_radio_list(self, m):
        async def aiterator():
            iterator = iter([(x, x) for x in map(str, range(10))])
            for item in iterator:
                yield item

        async_to_sync(show_radiolist(aiterator()))

    @patch('click.echo')
    def test_empty(self, m):
        async def aiterator():
            for item in []:
                yield item

        async_to_sync(show_radiolist(aiterator()))
        m.assert_called_once()
