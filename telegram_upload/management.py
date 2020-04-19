# -*- coding: utf-8 -*-

"""Console script for telegram-upload."""
import click

from telegram_upload.client import Client
from telegram_upload.config import default_config, CONFIG_FILE


@click.command()
@click.argument('files', nargs=-1)
@click.option('--to', default='me', help='Phone number, username, chat id or "me" (saved messages). By default "me".')
@click.option('--config', default=None, help='Configuration file to use. By default "{}".'.format(CONFIG_FILE))
@click.option('-d', '--delete-on-success', is_flag=True, help='Delete local file after successful upload.')
@click.option('--print-file-id', is_flag=True, help='Print the id of the uploaded file after the upload.')
def upload(files, to, config, delete_on_success, print_file_id):
    """Upload one or more files to Telegram using your personal account.
    The maximum file size is 1.5 GiB and by default they will be saved in
    your saved messages.
    """
    client = Client(config or default_config())
    client.start()
    client.send_files(to, files, delete_on_success, print_file_id)


@click.command()
@click.option('--from', '-f', 'from_', default='me')
@click.option('--config', default=None)
@click.option('-d', '--delete-on-success', is_flag=True)
def download(from_, config, delete_on_success):
    client = Client(config or default_config())
    client.start()
    messages = client.find_files(from_)
    client.download_files(from_, messages, delete_on_success)
