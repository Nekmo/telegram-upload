# -*- coding: utf-8 -*-

"""Exceptions for telegram-upload."""
import sys


class ThumbError(Exception):
    pass


class ThumbVideoError(ThumbError):
    pass


class TelegramUploadError(Exception):
    body = ''

    def __init__(self, extra_body=''):
        self.extra_body = extra_body

    def __str__(self):
        msg = self.__class__.__name__
        if self.body:
            msg += ': {}'.format(self.body)
        if self.extra_body:
            msg += ('. {}' if self.body else ': {}').format(self.extra_body)
        return msg


def catch(fn):
    def wrap(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except TelegramUploadError as e:
            sys.stderr.write('[Error] telegram-upload Exception:\n{}\n'.format(e))
    return wrap
