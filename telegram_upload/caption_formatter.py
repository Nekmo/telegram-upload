import _string
import datetime
import hashlib
import mimetypes
import os
import sys
import zlib
from pathlib import Path, PosixPath, WindowsPath
from string import Formatter
from typing import Any, Sequence, Mapping, Tuple

from telegram_upload.video import video_metadata

try:
    from typing import LiteralString
except ImportError:
    LiteralString = str


if sys.version_info < (3, 8):
    cached_property = property
else:
    from functools import cached_property


CHUNK_SIZE = 4096
VALID_TYPES: Tuple[Any, ...] = (str, int, float, complex, bool, datetime.datetime, datetime.date, datetime.time)
AUTHORIZED_METHODS = (Path.absolute, Path.home)
AUTHORIZED_STRING_METHODS = ("title", "capitalize", "lower", "upper", "swapcase", "strip", "lstrip", "rstrip")
AUTHORIZED_DT_METHODS = (
    "astimezone", "ctime", "date", "dst", "isoformat", "isocalendar", "isoformat", "isoweekday", "now", "time",
    "timestamp", "timetuple", "timetz", "today", "toordinal", "tzname", "utcnow", "utcoffset", "utctimetuple", "weekday"
)


class Duration:
    def __init__(self, seconds: int):
        self.seconds = seconds

    @property
    def as_minutes(self):
        return self.seconds // 60

    @property
    def as_hours(self):
        return self.as_minutes // 60

    @property
    def as_days(self):
        return self.as_hours // 24

    @property
    def for_humans(self):
        words = ["year", "day", "hour", "minute", "second"]

        if not self.seconds:
            return "now"
        else:
            m, s = divmod(self.seconds, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            y, d = divmod(d, 365)

            time = [y, d, h, m, s]

            duration = []

            for x, i in enumerate(time):
                if i == 1:
                    duration.append(f"{i} {words[x]}")
                elif i > 1:
                    duration.append(f"{i} {words[x]}s")

            if len(duration) == 1:
                return duration[0]
            elif len(duration) == 2:
                return f"{duration[0]} and {duration[1]}"
            else:
                return ", ".join(duration[:-1]) + " and " + duration[-1]

    def __int__(self):
        return self.seconds

    def __str__(self):
        return str(self.seconds)


class FileSize:
    def __init__(self, size: int):
        self.size = size

    @property
    def as_kilobytes(self):
        return self.size // 1000

    @property
    def as_megabytes(self):
        return self.as_kilobytes // 1000

    @property
    def as_gigabytes(self):
        return self.as_megabytes // 1000

    @property
    def as_kibibytes(self):
        return self.size // 1024

    @property
    def as_mebibytes(self):
        return self.as_kibibytes // 1024

    @property
    def as_gibibytes(self):
        return self.as_mebibytes // 1024

    @property
    def for_humans(self, suffix="B"):
        num = self.size
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return f"{num:3.1f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f} Yi{suffix}"

    def __int__(self):
        return self.size

    def __str__(self):
        return str(self.size)


class FileMedia:
    def __init__(self, path: str):
        self.path = path
        self.metadata = video_metadata(path)

    @cached_property
    def video_metadata(self):
        metadata = self.metadata
        meta_groups = None
        if hasattr(metadata, '_MultipleMetadata__groups'):
            # Is mkv
            meta_groups = metadata._MultipleMetadata__groups
        if metadata is not None and not metadata.has('width') and meta_groups:
            return meta_groups[next(filter(lambda x: x.startswith('video'), meta_groups._key_list))]
        return metadata

    @property
    def duration(self):
        if self.metadata and self.metadata.has('duration'):
            return Duration(self.metadata.get('duration').seconds)

    @property
    def width(self):
        return self.video_metadata.get('width') if self.video_metadata and self.video_metadata.has('width') else None

    @property
    def height(self):
        return self.video_metadata.get('height') if self.video_metadata and self.video_metadata.has('height') else None

    @property
    def title(self):
        return self.metadata.get('title') if self.metadata and self.metadata.has('title') else None

    @property
    def artist(self):
        return self.metadata.get('artist') if self.metadata and self.metadata.has('artist') else None

    @property
    def album(self):
        return self.metadata.get('album') if self.metadata and self.metadata.has('album') else None

    @property
    def producer(self):
        return self.metadata.get('producer') if self.metadata and self.metadata.has('producer') else None


class FileMixin:

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

    @cached_property
    def _file_stat(self):
        return os.stat(str(self))

    @cached_property
    def ctime(self):
        return datetime.datetime.fromtimestamp(self._file_stat.st_ctime)

    @cached_property
    def mtime(self):
        return datetime.datetime.fromtimestamp(self._file_stat.st_mtime)

    @cached_property
    def atime(self):
        return datetime.datetime.fromtimestamp(self._file_stat.st_atime)

    @cached_property
    def size(self):
        return FileSize(self._file_stat.st_size)

    @cached_property
    def media(self):
        return FileMedia(str(self))

    @cached_property
    def mimetype(self):
        mimetypes.init()
        return mimetypes.guess_type(str(self))[0]


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
            has_func = hasattr(obj, "__func__")
            has_self = hasattr(obj, "__self__")
            if (has_func and obj.__func__ in AUTHORIZED_METHODS) or \
                    (has_self and isinstance(obj.__self__, str) and obj.__name__ in AUTHORIZED_STRING_METHODS) or \
                    (has_self and isinstance(obj.__self__, datetime.datetime)
                     and obj.__name__ in AUTHORIZED_DT_METHODS):
                obj = obj()
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
