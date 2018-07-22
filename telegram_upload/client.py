import json
from distutils.version import StrictVersion

import click
import os
from telegram_upload.files import get_file_attributes, get_file_thumb
from telethon.version import __version__ as telethon_version
from telethon import TelegramClient

if StrictVersion(telethon_version) >= StrictVersion('1.0'):
    import telethon.sync


CAPTION_MAX_LENGTH = 200


class Client(TelegramClient):
    def __init__(self, config_file, **kwargs):
        config = json.load(open(config_file))
        super().__init__(config.get('session', 'telegram-upload'), config['api_id'], config['api_hash'], **kwargs)

    def send_files(self, entity, files, delete_on_success=False):
        for file in files:
            bar = click.progressbar(label='Uploading {}'.format(os.path.basename(file)),
                                    length=os.path.getsize(file))

            def progress(current, total):
                bar.pos = 0
                bar.update(current)

            name = '.'.join(os.path.basename(file).split('.')[:-1])
            thumb = get_file_thumb(file)
            try:
                self.send_file(entity, file, thumb=thumb,
                               caption=(name[:CAPTION_MAX_LENGTH] + '..') if len(name) > CAPTION_MAX_LENGTH else name,
                               progress_callback=progress, attributes=get_file_attributes(file))
            except Exception:
                raise
            finally:
                if thumb:
                    os.remove(thumb)
            click.echo()
            if delete_on_success:
                click.echo('Deleting {}'.format(file))
                os.remove(file)
