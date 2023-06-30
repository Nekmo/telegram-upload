#!/usr/bien/env python
import os
import shutil
import tempfile
from typing import Tuple, List

import click
import requests
from telethon.tl.types import Message

from telegram_upload.client import TelegramManagerClient
from telegram_upload.config import default_config
from telegram_upload.upload_files import NoLargeFiles

VIDEO_FILE_EXTENSIONS = [
    "3gp", "asf", "avi", "f4v", "flv", "hevc", "m2ts", "m2v", "m4v", "mjpeg", "mkv", "mov", "mp4", "mpeg", "mpg", "mts",
    "mxf", "ogv", "rm", "ts", "vob", "webm", "wmv", "wtv"
]
AUDIO_FILE_EXTENSIONS = [
    "8svx", "aac", "ac3", "aiff", "amb", "au", "avr", "caf", "cdda", "cvs", "cvsd", "cvu", "dts", "dvms", "fap",
    "flac", "fssd", "gsrt", "hcom", "htk", "ima", "ircam", "m4a", "m4r", "maud", "mp2", "mp3", "nist", "oga", "ogg",
    "opus", "paf", "prc", "pvf", "ra", "sd2", "sln", "smp", "snd", "sndr", "sndt", "sou", "sph", "spx", "tta", "txw",
    "vms", "voc", "vox", "w64", "wav", "wma", "wv", "wve",
]
VIDEO_CAPTION_MESSAGE = "{file.name}\n" \
                        "{file.media.title} ({file.media.producer})\n" \
                        "{file.media.width}x{file.media.height}px {file.media.duration.for_humans}"
AUDIO_CAPTION_MESSAGE = "{file.name}\n" \
                        "{file.media.title} ({file.media.producer})\n" \
                        "{file.media.artist} - {file.media.album}\n" \
                        "{file.media.duration.for_humans}"
VIDEO_URL = "https://filesamples.com/samples/video/{extension}/sample_960x400_ocean_with_audio.{extension}"
AUDIO_URL = "https://filesamples.com/samples/audio/{extension}/sample4.{extension}"
CHUNK_SIZE = 8192


def download_file(url: str, directory: str = "") -> str:
    """Download a file from a URL and save it in the specified directory"""
    local_filename = url.split('/')[-1]
    local_filename = os.path.join(directory, local_filename)
    if os.path.lexists(local_filename):
        return local_filename
    tmp_local_filename = local_filename + '.tmp'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    shutil.move(tmp_local_filename, local_filename)
    return local_filename


def download_video_file(extension: str, directory: str = "") -> str:
    """Download a video file from an URL and save it in the specified directory"""
    url = VIDEO_URL.format(extension=extension)
    return download_file(url, directory)


def download_audio_file(extension: str, directory: str = "") -> str:
    """Download an audio file from an URL and save it in the specified directory"""
    url = AUDIO_URL.format(extension=extension)
    return download_file(url, directory)


def download_extension_file(extension: str, directory: str = "") -> Tuple[str, str]:
    """Download a file from an URL and save it in the specified directory"""
    if extension in VIDEO_FILE_EXTENSIONS:
        return download_video_file(extension, directory), "video"
    elif extension in AUDIO_FILE_EXTENSIONS:
        return download_audio_file(extension, directory), "audio"
    else:
        raise ValueError(f"Unsupported extension {extension}")


def upload_extension_file(client: TelegramManagerClient, extension: str, directory: str = "") -> List[Message]:
    """Upload a file to Telegram by extension"""
    path, media_type = download_extension_file(extension, directory)
    if media_type == "audio":
        caption = AUDIO_CAPTION_MESSAGE
    elif media_type == "video":
        caption = VIDEO_CAPTION_MESSAGE
    else:
        raise ValueError(f"Unsupported media type {media_type}")
    return client.send_files("me", NoLargeFiles(client, [path], caption=caption))


@click.command()
@click.option('--extension', '-e', default="",  help='Extension of the file to upload')
@click.option('--directory', '-d', default="", help='Directory where to save the file')
def upload_file(extension: str = "", directory: str = ""):
    """Upload a file to Telegram by extension"""
    extensions = []
    if not directory:
        directory = tempfile.gettempdir()
    if extension:
        extensions.append(extension)
    else:
        extensions = VIDEO_FILE_EXTENSIONS + AUDIO_FILE_EXTENSIONS
    client = TelegramManagerClient(default_config())
    client.start()
    for extension in extensions:
        click.echo(f"Uploading {extension} file")
        try:
            upload_extension_file(client, extension, directory)
        except Exception as e:
            click.echo(f"Error uploading {extension} file: {e}", err=True)


if __name__ == '__main__':
    upload_file()
