import json

import click
import os
from telethon import TelegramClient



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

            self.send_file(entity, file, progress_callback=progress)
            click.echo()

    def progress_callback(self, tell, size):
        click.echo('{} -- {}'.format(tell, size))
