import json
import mimetypes

import click
import os
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


CAPTION_MAX_LENGTH = 200

mimetypes.init()


def get_file_attributes(file):
    attrs = []
    mime = (mimetypes.guess_type(file)[0] or ('')).split('/')[0]
    if mime == 'video':
        metadata = extractMetadata(createParser(file))
        attrs.append(DocumentAttributeVideo(
            (0, metadata.get('duration').seconds)[metadata.has('duration')],
            (0, metadata.get('width'))[metadata.has('width')],
            (0, metadata.get('height'))[metadata.has('height')]
        ))
    return attrs


class Client(TelegramClient):
    def __init__(self, config_file, **kwargs):
        config = json.load(open(config_file))
        super().__init__(config.get('session', 'telegram-upload'), config['api_id'], config['api_hash'], **kwargs)

    def send_files(self, entity, files):
        for file in files:
            bar = click.progressbar(label='Uploading {}'.format(os.path.basename(file)),
                                    length=os.path.getsize(file))
            def progress(current, total):
                bar.pos = 0
                bar.update(current)

            name = '.'.join(os.path.basename(file).split('.')[:-1])
            self.send_file(entity, file,
                           caption=(name[:CAPTION_MAX_LENGTH] + '..') if len(name) > CAPTION_MAX_LENGTH else name,
                           progress_callback=progress, attributes=get_file_attributes(file))
            click.echo()
