import os
from typing import TYPE_CHECKING

from PySide2 import QtWidgets

from telegram_upload.utils import sizeof_fmt


if TYPE_CHECKING:
    from telegram_upload_ui import TelegramUploadWindow


class UploadFile:
    parent: 'TelegramUploadWindow'
    progress: QtWidgets.QProgressBar

    def __init__(self, path):
        self.path = path
        self.caption = ''
        self.force_file = False
        self.is_active = True
        self.upload_to = None

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def size(self):
        return os.path.getsize(self.path)

    @property
    def human_size(self):
        return sizeof_fmt(self.size)

    def set_caption(self, text):
        self.caption = text

    def set_force_file(self, boolean):
        self.force_file = bool(boolean)

    def set_is_active(self, boolean):
        self.is_active = bool(boolean)

    def update_progress(self, current, total):
        # self.progress.setValue((current / total) * 100)
        self.parent.c.progress.emit(self.path, (current / total) * 100)
