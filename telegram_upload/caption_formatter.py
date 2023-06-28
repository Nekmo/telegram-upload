import _string
import datetime
import hashlib
import os
import zlib
from pathlib import Path, PosixPath, WindowsPath
from string import Formatter
from typing import Any, Sequence, Mapping, Tuple


try:
    from typing import LiteralString
except ImportError:
    LiteralString = str


CHUNK_SIZE = 4096
VALID_TYPES: Tuple[Any, ...] = (str, int, float, complex, bool, datetime.datetime, datetime.date, datetime.time)


class FileMixin:
    _private = 4

    def _calculate_hash(self, hash_calculator: Any):
        with open(str(self), "rb") as f:
            # Read and update hash string value in blocks
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                hash_calculator.update(byte_block)
            return hash_calculator.hexdigest()

    @property
    def md5(self):
        return self._calculate_hash(hashlib.md5())

    @property
    def sha1(self):
        return self._calculate_hash(hashlib.sha1())

    @property
    def sha224(self):
        return self._calculate_hash(hashlib.sha224())

    @property
    def sha256(self):
        return self._calculate_hash(hashlib.sha256())

    @property
    def sha384(self):
        return self._calculate_hash(hashlib.sha384())

    @property
    def sha512(self):
        return self._calculate_hash(hashlib.sha512())

    @property
    def sha3_224(self):
        return self._calculate_hash(hashlib.sha3_224())

    @property
    def sha3_256(self):
        return self._calculate_hash(hashlib.sha3_256())

    @property
    def sha3_384(self):
        return self._calculate_hash(hashlib.sha3_384())

    @property
    def sha3_512(self):
        return self._calculate_hash(hashlib.sha3_512())

    @property
    def crc32(self):
        with open(str(self), "rb") as f:
            calculated_hash = 0
            # Read and update hash string value in blocks
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                calculated_hash = zlib.crc32(byte_block, calculated_hash)
            return "%08X" % (calculated_hash & 0xFFFFFFFF)

    @property
    def adler32(self):
        with open(str(self), "rb") as f:
            calculated_hash = 1
            # Read and update hash string value in blocks
            for byte_block in iter(lambda: f.read(CHUNK_SIZE), b""):
                calculated_hash = zlib.adler32(byte_block, calculated_hash)
                if calculated_hash < 0:
                    calculated_hash += 2 ** 32
            return hex(calculated_hash)[2:10].zfill(8)


class FilePath(FileMixin, Path):
    def __new__(cls, *args, **kwargs):
        if cls is FilePath:
            cls = WindowsFilePath if os.name == 'nt' else PosixFilePath
        self = cls._from_parts(args)
        if not self._flavour.is_supported:
            raise NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        return self


class WindowsFilePath(FileMixin, WindowsPath):
    pass


class PosixFilePath(FileMixin, PosixPath):
    pass


class CaptionFormatter(Formatter):

    def get_field(self, field_name: str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
        try:
            if "._" in field_name:
                raise TypeError(f'Access to private property in {field_name}')
            obj, first = super().get_field(field_name, args, kwargs)
            if not isinstance(obj, VALID_TYPES + (WindowsFilePath, PosixFilePath, FilePath)):
                raise TypeError(f'Invalid type for {field_name}: {type(obj)}')
            return obj, first
        except Exception:
            first, rest = _string.formatter_field_name_split(field_name)
            return '{' + field_name + '}', first

    def format(self, __format_string: LiteralString, *args: LiteralString, **kwargs: LiteralString) -> LiteralString:
        try:
            return super().format(__format_string, *args, **kwargs)
        except ValueError:
            return __format_string
