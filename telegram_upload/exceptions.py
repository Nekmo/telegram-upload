# -*- coding: utf-8 -*-

"""Exceptions for telegram-upload."""
import sys

import click

from telegram_upload.config import prompt_config


class ThumbError(Exception):
    pass


class ThumbVideoError(ThumbError):
    pass


class TelegramUploadError(Exception):
    body = ''
    error_code = 1

    def __init__(self, extra_body=''):
        self.extra_body = extra_body

    def __str__(self):
        msg = self.__class__.__name__
        if self.body:
            msg += ': {}'.format(self.body)
        if self.extra_body:
            msg += ('. {}' if self.body else ': {}').format(self.extra_body)
        return msg


class MissingFileError(TelegramUploadError):
    pass


class InvalidApiFileError(TelegramUploadError):
    def __init__(self, config_file, extra_body=''):
        self.config_file = config_file
        super().__init__(extra_body)


class TelegramInvalidFile(TelegramUploadError):
    error_code = 3


class TelegramUploadNoSpaceError(TelegramUploadError):
    error_code = 28


class TelegramUploadDataLoss(TelegramUploadError):
    error_code = 29


class TelegramProxyError(TelegramUploadError):
    error_code = 30


class TelegramEnvironmentError(TelegramUploadError):
    error_code = 31


def catch(fn):
    def wrap(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except InvalidApiFileError as e:
            click.echo('The api_id/api_hash combination is invalid. Re-enter both values.')
            prompt_config(e.config_file)
            return catch(fn)(*args, **kwargs)
        except TelegramUploadError as e:
            sys.stderr.write('[Error] telegram-upload Exception:\n{}\n'.format(e))
            exit(e.error_code)
    return wrap
