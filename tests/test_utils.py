import unittest
from unittest.mock import patch, Mock

from telegram_upload.utils import sizeof_fmt, scantree, aislice

import asyncio # for TestAISlice's test_general


class TestSizeOfFmt(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(sizeof_fmt(1023), '1023.0B')

    def test_kibibytes(self):
        self.assertEqual(sizeof_fmt(2400), '2.3KiB')

    def test_exact_mebibytes(self):
        self.assertEqual(sizeof_fmt((1024 ** 2) * 3), '3.0MiB')


class TestScanTree(unittest.TestCase):
    @patch('telegram_upload.utils.scandir', return_value=[])
    def test_empty_directory(self, m):
        self.assertEqual(list(scantree('foo')), [])

    @patch('telegram_upload.utils.scandir')
    def test_files(self, m):
        file = Mock()
        file.is_dir.return_value = False
        m.return_value = [file] * 3
        self.assertEqual(list(scantree('foo')), m.return_value)

    @patch('telegram_upload.utils.scandir')
    def test_directory(self, m):
        directory = Mock()
        directory.is_dir.side_effect = [True, False]
        file = Mock()
        file.is_dir.return_value = False
        side_effect = [[directory], [file] * 3]
        m.side_effect = side_effect
        self.assertEqual(list(scantree('foo')), side_effect[-1])

class TestAISlice(unittest.TestCase):
    def test_general(self):
        class asyncFromList:
            def __init__(self, rawlist):
                self.rawidx = -1
                self.rawlist = rawlist.copy()
            def __aiter__(self):
                return self
            async def __anext__(self):
                await asyncio.sleep(0)
                self.rawidx += 1
                if self.rawidx >= len(self.rawlist):
                    raise StopAsyncIteration
                return self.rawlist[self.rawidx]
        async def async_collect_all_files(it, pagesize):
            ret = []
            while True:
                aislice_res = await aislice(it, pagesize)
                if len(aislice_res) == 0: break
                self.assertLessEqual(len(aislice_res), pagesize, "limit returns more than asked")
                ret.extend(aislice_res)
            return ret
        pagesize = 10
        files = [ str(i) for i in range(51) ]
        gotfiles = asyncio.get_event_loop().run_until_complete(async_collect_all_files(asyncFromList(files), pagesize))
        self.assertEqual(gotfiles, files, "got different set of values")
