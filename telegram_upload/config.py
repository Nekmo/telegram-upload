import json
import os

import click

CONFIG_FILE = os.path.expanduser('~/.config/telegram-upload.json')
SESSION_FILE = os.path.expanduser('~/.config/telegram-upload')


def prompt_config(config_file):
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    click.echo('Go to https://my.telegram.org and create a App in API development tools')
    api_id = click.prompt('Please Enter api_id', type=int)
    api_hash = click.prompt('Now enter api_hash')
    with open(config_file, 'w') as f:
        json.dump({'api_id': api_id, 'api_hash': api_hash}, f)
    return config_file


def default_config():
    if os.path.lexists(CONFIG_FILE):
        return CONFIG_FILE
    return prompt_config(CONFIG_FILE)
