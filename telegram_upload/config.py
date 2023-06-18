import getpass
import json
import os
import re

import click

CONFIG_DIRECTORY = os.environ.get('TELEGRAM_UPLOAD_CONFIG_DIRECTORY', '~/.config')
CONFIG_FILE = os.path.expanduser('{}/telegram-upload.json'.format(CONFIG_DIRECTORY))
SESSION_FILE = os.path.expanduser('{}/telegram-upload'.format(CONFIG_DIRECTORY))


def phone_match(value):
    match = re.match(r'\+?[0-9.()\[\] \-]+', value)
    if match is None:
        raise ValueError('{} is not a valid phone'.format(value))
    return value


def prompt_config(config_file):
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    config_data = {}
    click.echo('Go to https://my.telegram.org and create a App in API development tools')
    api_id = click.prompt('Please Enter api_id', type=int)
    config_data['api_id'] = api_id
    api_hash = click.prompt('Now enter api_hash')
    config_data['api_hash'] = api_hash
    mode = click.prompt('Choose mode: User [u] or Bot [b]')
    if mode == 'u':
        phone = click.prompt('Please enter your phone', type=phone_match)
        config_data['phone'] = phone
        password = getpass.getpass('Please enter your password: ')
        config_data['password'] = password
    elif mode == 'b':
        bot_token = click.prompt('Please enter your bot token: ')
        config_data['bot_token'] = bot_token
    else:
        raise KeyError('Unknown mode')
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    return config_file


def default_config():
    if os.path.lexists(CONFIG_FILE):
        return CONFIG_FILE
    return prompt_config(CONFIG_FILE)
