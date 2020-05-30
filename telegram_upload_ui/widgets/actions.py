from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction


class Action(QAction):
    def __init__(self, icon, text, *args, **kwargs):
        shortcut = kwargs.pop('shortcut', None)
        connect = kwargs.pop('connect', None)
        if isinstance(icon, str) and isinstance(text, str):
            icon = QIcon.fromTheme(icon)
        super().__init__(icon, text, *args, **kwargs)
        if text:
            self.setStatusTip(text)
        if shortcut:
            self.setShortcut(shortcut)
        if connect:
            self.triggered.connect(connect)
