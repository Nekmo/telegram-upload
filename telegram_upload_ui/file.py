import os

from telegram_upload.utils import sizeof_fmt


class UploadFile:
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
