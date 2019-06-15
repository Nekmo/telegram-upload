# -*- coding: utf-8 -*-

"""Console script for telegram-upload."""
import click

from telegram_upload.client import Client
from telegram_upload.config import default_config


@click.command()
@click.argument('files', nargs=-1)
@click.option('--to', default='me')
@click.option('--config', default=None)
@click.option('-d', '--delete-on-success', is_flag=True)
def upload(files, to, config, delete_on_success):
    client = Client(config or default_config())
    client.start()
    client.send_files(to, files, delete_on_success)


@click.command()
@click.option('--from', '-f', 'from_', default='me')
@click.option('--config', default=None)
@click.option('-d', '--delete-on-success', is_flag=True)
def download(from_, config, delete_on_success):
    client = Client(config or default_config())
    client.start()
    messages = client.find_files(from_)
    client.download_files(from_, messages, delete_on_success)

