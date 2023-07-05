#!/usr/bin/env python
import asyncio
import os
import time
from tempfile import NamedTemporaryFile
from typing import Callable, Optional

import click
from telethon.tl.patched import Message

from telegram_upload.client import TelegramManagerClient
from telegram_upload.config import default_config
from telegram_upload.upload_files import NoLargeFiles

CHUNK = 1024 * 4
REPEATS = 5
BENCHMARKS = {
    "small": (1024 * 512, 3, 10),
    # "medium": (1024 * 1024 * 20, 10, 10),
    # "large": (1024 * 1024 * 200, 30, 5),
    # "full": (1024 * 1024 * 1024 * 2, 90, 5),
}
PARALLELS = range(1, 11)


def create_file(size: int) -> str:
    """Create a file with the specified size"""
    file = NamedTemporaryFile(delete=False)
    with file:
        for i in range(0, size, CHUNK):
            file.write(b"\x00" * CHUNK)
    return file.name


def upload_file(client: TelegramManagerClient, path) -> Message:
    """Upload a file to Telegram"""
    messages = client.send_files("me", NoLargeFiles(client, [path]))
    if messages:
        return messages[0]


class Benchmark:
    """Benchmark a function."""
    def __init__(self, callback: Callable, repeats: int = REPEATS, wait: int = 0):
        """Initialize the benchmark"""
        self.callback = callback
        self.repeats = repeats
        self.times = []
        self.results = []
        self.wait = wait

    def __call__(self):
        for i in range(self.repeats):
            start = time.time()
            output = self.callback()
            end = time.time()
            self.results.append(output)
            self.times.append(end - start)
            if self.wait:
                time.sleep(self.wait)

    @property
    def average(self) -> float:
        """Return the average time"""
        if not self.times:
            return .0
        return sum(self.times) / len(self.times)

    @property
    def minimum(self) -> float:
        """Return the minimum time"""
        return min(self.times)

    @property
    def maximum(self) -> float:
        """Return the maximum time"""
        return max(self.times)


def benchmark_file_size(client: TelegramManagerClient, size: int, repeats: int = REPEATS, wait: int = 0,
                        parallel: Optional[int] = None):
    """Benchmark the upload of a file of the specified size"""
    # reset parallel upload blocks
    client.parallel_upload_blocks = parallel
    client.reconnecting_lock = asyncio.Lock()
    client.upload_semaphore = asyncio.Semaphore(parallel)
    # create file
    path = create_file(size)
    # benchmark upload
    benchmark = Benchmark(lambda: upload_file(client, path), repeats, wait)
    benchmark()
    click.echo(f"Size: {size} bytes  -  Parallel: {parallel}")
    click.echo(f"Average: {benchmark.average} seconds")
    click.echo(f"Minimum: {benchmark.minimum} seconds")
    click.echo(f"Maximum: {benchmark.maximum} seconds")
    click.echo("=" * 80 + "\n")
    os.remove(path)
    for message in benchmark.results:
        message.delete()


@click.command()
@click.option('--repeats', '-r', default=None, type=int, help='Number of repeats')
@click.option('--benchmark', '-b', default=None, type=click.Choice(list(BENCHMARKS.keys())), help='Benchmark name')
@click.option('--parallel', '-p', default=None, type=int, help='Parallel parts uploaded')
def benchmark(repeats, benchmark, parallel):
    client = TelegramManagerClient(default_config())
    client.start()
    if benchmark:
        benchmarks = [BENCHMARKS[benchmark]]
    else:
        benchmarks = list(BENCHMARKS.values())
    if parallel:
        parallels = [parallel]
    else:
        parallels = PARALLELS
    for size, wait, def_repeats in benchmarks:
        for parallel in parallels:
            benchmark_file_size(client, size, repeats or def_repeats, wait, parallel)


if __name__ == '__main__':
    benchmark()
