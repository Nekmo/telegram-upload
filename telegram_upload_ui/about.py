import os

from docutils.core import publish_string

from telegram_upload import __version__
from PySide2 import QtWidgets


ABOUT_TABS = [
    ('About', 'SUMMARY.rst'),
    ('Contributors', 'AUTHORS.rst'),
    ('Changelog', 'HISTORY.rst'),
    ('License', 'LICENSE'),
]


project_directory = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..'))


def rst_to_html(data):
    html = publish_string(
        source=data,
        writer_name="html")
    return html.decode('utf-8')


def rst_file_to_html(path):
    with open(path, 'r') as f:
        data = f.read()
    return rst_to_html(data)


class AboutTabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for label, filename in ABOUT_TABS:
            text_widget = QtWidgets.QTextBrowser()
            text_widget.setHtml(rst_file_to_html(os.path.join(project_directory, filename)))
            self.addTab(text_widget, label)


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        name = QtWidgets.QLabel(f'Telegram upload {__version__}')
        font = name.font()
        font.setBold(True)
        font.setPointSize(30)
        name.setFont(font)
        self.layout.addWidget(name)
        self.layout.addWidget(AboutTabWidget())
        self.setLayout(self.layout)
