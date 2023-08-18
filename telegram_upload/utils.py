import asyncio
import itertools
import os
import shutil
from telegram_upload._compat import scandir
from telegram_upload.exceptions import TelegramEnvironmentError


def free_disk_usage(directory='.'):
    return shutil.disk_usage(directory)[2]


def truncate(text, max_length):
    return (text[:max_length - 3] + '...') if len(text) > max_length else text


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def scantree(path, follow_symlinks=False):
    """Recursively yield DirEntry objects for given directory."""
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=follow_symlinks):
            yield from scantree(entry.path, follow_symlinks)  # see below for Python 2.x
        else:
            yield entry


def async_to_sync(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return coro
    else:
        return loop.run_until_complete(coro)


async def aislice(iterator, limit):
    items = []
    i = 0
    async for value in iterator:
        items.append(value)
        i += 1
        if i >= limit:
            break
    return items


async def amap(fn, iterator):
    async for value in iterator:
        yield fn(value)


async def sync_to_async_iterator(iterator):
    for value in iterator:
        yield value


def get_environment_integer(environment_name: str, default_value: int):
    """Get an integer from an environment variable."""
    value = os.environ.get(environment_name, default_value)
    if isinstance(value, int) or value.isdigit():
        return int(value)
    raise TelegramEnvironmentError(f"Environment variable {environment_name} must be an integer")
