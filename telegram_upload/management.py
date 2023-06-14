# -*- coding: utf-8 -*-

"""Console script for telegram-upload."""
import os

import click
from telethon.tl.types import User

from telegram_upload.cli import show_checkboxlist, show_radiolist
from telegram_upload.client import Client, get_message_file_attribute
from telegram_upload.config import default_config, CONFIG_FILE
from telegram_upload.download_files import KeepDownloadSplitFiles, JoinDownloadSplitFiles
from telegram_upload.exceptions import catch
from telegram_upload.upload_files import NoDirectoriesFiles, RecursiveFiles, NoLargeFiles, SplitFiles, is_valid_file
from telegram_upload.utils import async_to_sync, amap, sync_to_async_iterator


try:
    from natsort import natsorted
except ImportError:
    natsorted = None


DIRECTORY_MODES = {
    'fail': NoDirectoriesFiles,
    'recursive': RecursiveFiles,
}
LARGE_FILE_MODES = {
    'fail': NoLargeFiles,
    'split': SplitFiles,
}
DOWNLOAD_SPLIT_FILE_MODES = {
    'keep': KeepDownloadSplitFiles,
    'join': JoinDownloadSplitFiles,
}


def get_file_display_name(message):
    display_name_parts = []
    is_document = message.document
    if is_document and message.document.mime_type:
        display_name_parts.append(message.document.mime_type.split('/')[0])
    if is_document and get_message_file_attribute(message):
        display_name_parts.append(get_message_file_attribute(message).file_name)
    if message.text:
        display_name_parts.append(f'[{message.text}]' if display_name_parts else message.text)
    from_user = message.sender and isinstance(message.sender, User)
    if from_user:
        display_name_parts.append('by')
    if from_user and message.sender.first_name:
        display_name_parts.append(message.sender.first_name)
    if from_user and message.sender.last_name:
        display_name_parts.append(message.sender.last_name)
    if from_user and message.sender.username:
        display_name_parts.append(f'@{message.sender.username}')
    display_name_parts.append(f'{message.date}')
    return ' '.join(display_name_parts)


async def interactive_select_files(client, entity: str):
    iterator = client.iter_files(entity)
    iterator = amap(lambda x: (x, get_file_display_name(x)), iterator,)
    return await show_checkboxlist(iterator)


async def interactive_select_local_files():
    iterator = filter(lambda x: os.path.isfile(x) and os.path.lexists(x), os.listdir('.'))
    iterator = sync_to_async_iterator(map(lambda x: (x, x), iterator))
    return await show_checkboxlist(iterator, 'Not files were found in the current directory '
                                             '(subdirectories are not supported). Exiting...')


async def interactive_select_dialog(client):
    iterator = client.iter_dialogs()
    iterator = amap(lambda x: (x, x.name), iterator,)
    value = await show_radiolist(iterator, 'Not dialogs were found in your Telegram session. '
                                           'Have you started any conversations?')
    return value.id if value else None


class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help = kwargs.get('help', '')
        if self.mutually_exclusive:
            kwargs['help'] = help + (
                ' NOTE: This argument is mutually exclusive with'
                ' arguments: [{}].'.format(self.mutually_exclusive_text)
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    self.mutually_exclusive_text
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )

    @property
    def mutually_exclusive_text(self):
        return ', '.join([x.replace('_', '-') for x in self.mutually_exclusive])


@click.command()
@click.argument('files', nargs=-1)
@click.option('--to', default=None, help='Phone number, username, invite link or "me" (saved messages). '
                                         'By default "me".')
@click.option('--config', default=None, help='Configuration file to use. By default "{}".'.format(CONFIG_FILE))
@click.option('-d', '--delete-on-success', is_flag=True, help='Delete local file after successful upload.')
@click.option('--print-file-id', is_flag=True, help='Print the id of the uploaded file after the upload.')
@click.option('--force-file', is_flag=True, help='Force send as a file. The filename will be preserved '
                                                 'but the preview will not be available.')
@click.option('-f', '--forward', multiple=True, help='Forward the file to a chat (alias or id) or user (username, '
                                                     'mobile or id). This option can be used multiple times.')
@click.option('--directories', default='fail', type=click.Choice(list(DIRECTORY_MODES.keys())),
              help='Defines how to process directories. By default directories are not accepted and will raise an '
                   'error.')
@click.option('--large-files', default='fail', type=click.Choice(list(LARGE_FILE_MODES.keys())),
              help='Defines how to process large files unsupported for Telegram. By default large files are not '
                   'accepted and will raise an error.')
@click.option('--caption', type=str, help='Change file description. By default the file name.')
@click.option('--no-thumbnail', is_flag=True, cls=MutuallyExclusiveOption, mutually_exclusive=["thumbnail_file"],
              help='Disable thumbnail generation. For some known file formats, Telegram may still generate a '
                   'thumbnail or show a preview.')
@click.option('--thumbnail-file', default=None, cls=MutuallyExclusiveOption, mutually_exclusive=["no_thumbnail"],
              help='Path to the preview file to use for the uploaded file.')
@click.option('-p', '--proxy', default=None,
              help='Use an http proxy, socks4, socks5 or mtproxy. For example socks5://user:pass@1.2.3.4:8080 '
                   'for socks5 and mtproxy://secret@1.2.3.4:443 for mtproxy.')
@click.option('-a', '--album', is_flag=True,
              help='Send video or photos as an album.')
@click.option('-i', '--interactive', is_flag=True,
              help='Use interactive mode.')
@click.option('--sort', is_flag=True,
              help='Sort files by name before upload it. Install the natsort Python package for natural sorting.')
def upload(files, to, config, delete_on_success, print_file_id, force_file, forward, directories, large_files, caption,
           no_thumbnail, thumbnail_file, proxy, album, interactive, sort):
    """Upload one or more files to Telegram using your personal account.
    The maximum file size is 2 GiB and by default they will be saved in
    your saved messages.
    """
    client = Client(config or default_config(), proxy=proxy)
    client.start()
    if interactive and not files:
        click.echo('Select the local files to upload:')
        click.echo('[SPACE] Select file [ENTER] Next step')
        files = async_to_sync(interactive_select_local_files())
    if interactive and not files:
        # No files selected. Exiting.
        return
    if interactive and to is None:
        click.echo('Select the recipient dialog of the files:')
        click.echo('[SPACE] Select dialog [ENTER] Next step')
        to = async_to_sync(interactive_select_dialog(client))
    elif to is None:
        to = 'me'
    files = filter(lambda file: is_valid_file(file, lambda message: click.echo(message, err=True)), files)
    files = DIRECTORY_MODES[directories](files)
    if directories == 'fail':
        # Validate now
        files = list(files)
    if no_thumbnail:
        thumbnail = False
    elif thumbnail_file:
        thumbnail = thumbnail_file
    else:
        thumbnail = None
    files_cls = LARGE_FILE_MODES[large_files]
    files = files_cls(files, caption=caption, thumbnail=thumbnail, force_file=force_file)
    if large_files == 'fail':
        # Validate now
        files = list(files)
    if to.lstrip("-+").isdigit():
        to = int(to)
    if sort and natsorted:
        files = natsorted(files, key=lambda x: x.name)
    elif sort:
        files = sorted(files, key=lambda x: x.name)
    if album:
        client.send_files_as_album(to, files, delete_on_success, print_file_id, forward)
    else:
        client.send_files(to, files, delete_on_success, print_file_id, forward)


@click.command()
@click.option('--from', '-f', 'from_', default='',
              help='Phone number, username, chat id or "me" (saved messages). By default "me".')
@click.option('--config', default=None, help='Configuration file to use. By default "{}".'.format(CONFIG_FILE))
@click.option('-d', '--delete-on-success', is_flag=True,
              help='Delete telegram message after successful download. Useful for creating a download queue.')
@click.option('-p', '--proxy', default=None,
              help='Use an http proxy, socks4, socks5 or mtproxy. For example socks5://user:pass@1.2.3.4:8080 '
                   'for socks5 and mtproxy://secret@1.2.3.4:443 for mtproxy.')
@click.option('-m', '--split-files', default='keep', type=click.Choice(list(DOWNLOAD_SPLIT_FILE_MODES.keys())),
              help='Defines how to download large files split in Telegram. By default the files are not merged.')
@click.option('-i', '--interactive', is_flag=True,
              help='Use interactive mode.')
def download(from_, config, delete_on_success, proxy, split_files, interactive):
    """Download all the latest messages that are files in a chat, by default download
    from "saved messages". It is recommended to forward the files to download to
    "saved messages" and use parameter ``--delete-on-success``. Forwarded messages will
    be removed from the chat after downloading, such as a download queue.
    """
    client = Client(config or default_config(), proxy=proxy)
    client.start()
    if not interactive and not from_:
        from_ = 'me'
    elif not interactive and from_.lstrip("-+").isdigit():
        from_ = int(from_)
    elif interactive and not from_:
        click.echo('Select the dialog of the files to download:')
        click.echo('[SPACE] Select dialog [ENTER] Next step')
        from_ = async_to_sync(interactive_select_dialog(client))
    if interactive:
        click.echo('Select all files to download:')
        click.echo('[SPACE] Select files [ENTER] Download selected files')
        messages = async_to_sync(interactive_select_files(client, from_))
    else:
        messages = client.find_files(from_)
    messages_cls = DOWNLOAD_SPLIT_FILE_MODES[split_files]
    download_files = messages_cls(reversed(list(messages)))
    client.download_files(from_, download_files, delete_on_success)


upload_cli = catch(upload)
download_cli = catch(download)


if __name__ == '__main__':
    import sys
    import re
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    commands = {'upload': upload_cli, 'download': download_cli}
    if len(sys.argv) < 2:
        sys.stderr.write('A command is required. Available commands: {}\n'.format(
            ', '.join(commands)
        ))
        sys.exit(1)
    if sys.argv[1] not in commands:
        sys.stderr.write('{} is an invalid command. Valid commands: {}\n'.format(
            sys.argv[1], ', '.join(commands)
        ))
        sys.exit(1)
    fn = commands[sys.argv[1]]
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    sys.exit(fn())
