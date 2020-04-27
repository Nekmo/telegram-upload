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
@click.option('--force-file', is_flag=True, help='Force send as a file. The filename will be preserved '
                                                 'but the preview will not be available.')
def upload(files, to, config, delete_on_success, print_file_id, force_file):
    """Upload one or more files to Telegram using your personal account.
    The maximum file size is 1.5 GiB and by default they will be saved in
    your saved messages.
    """
    client = Client(config or default_config())
    client.start()
    client.send_files(to, files, delete_on_success, print_file_id, force_file)


@click.command()
@click.option('--from', '-f', 'from_', default='me',
              help='Phone number, username, chat id or "me" (saved messages). By default "me".')
@click.option('--config', default=None, help='Configuration file to use. By default "{}".'.format(CONFIG_FILE))
@click.option('-d', '--delete-on-success', is_flag=True,
              help='Delete telegram message after successful download. Useful for creating a download queue.')
def download(from_, config, delete_on_success):
    """Download all the latest messages that are files in a chatt, by default download
    from "saved messages". It is recommended to forward the files to download to
    "saved messages" and use parameter ``--delete-on-success``. Forwarded messages will
    be removed from the chat after downloading, such as a download queue.
    """
    client = Client(config or default_config())
    client.start()
    messages = client.find_files(from_)
    client.download_files(from_, messages, delete_on_success)
