import getpass
import json
import re
from distutils.version import StrictVersion

import click
import os
from telegram_upload.files import get_file_attributes, get_file_thumb
from telethon.version import __version__ as telethon_version
from telethon import TelegramClient

if StrictVersion(telethon_version) >= StrictVersion('1.0'):
    import telethon.sync


CAPTION_MAX_LENGTH = 200


def phone_match(value):
    match = re.match(r'\+?[0-9.()\[\] \-]+', value)
    if match is None:
        raise ValueError('{} is not a valid phone'.format(value))
    return value


class Client(TelegramClient):
    def __init__(self, config_file, **kwargs):
        config = json.load(open(config_file))
        super().__init__(config.get('session', 'telegram-upload'), config['api_id'], config['api_hash'], **kwargs)

    def start(
            self,
            phone=lambda: click.prompt('Please enter your phone', type=phone_match),
            password=lambda: getpass.getpass('Please enter your password: '),
            *,
            bot_token=None, force_sms=False, code_callback=None,
            first_name='New User', last_name='', max_attempts=3):
        return super().start(phone=phone, password=password, bot_token=bot_token, force_sms=force_sms,
                             first_name=first_name, last_name=last_name, max_attempts=max_attempts)

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

    def find_files(self):
        pass
