import json
import os

import click

CONFIG_FILE = os.path.expanduser('~/.config/telegram-upload.json')


def default_config():
    if os.path.lexists(CONFIG_FILE):
        return CONFIG_FILE
    click.echo('Go to https://my.telegram.org and create a App in API development tools')
    api_id = click.prompt('Please Enter api_id', type=int)
    api_hash = click.prompt('Now enter api_hash')
    json.dump({'api_id': api_id, 'api_hash': api_hash}, open(CONFIG_FILE, 'w'))
    return CONFIG_FILE
