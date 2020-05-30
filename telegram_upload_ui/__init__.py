import os
import sys
import glob
from typing import Union

from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import Qt, QSize, QObject, Signal
from PySide2.QtGui import QIcon, QPixmap, QPainterPath, QPainter
from PySide2.QtWidgets import QListWidgetItem
from telethon.tl.custom import Dialog

from telegram_upload.config import CONFIG_FILE
from telegram_upload_ui.file import UploadFile
from telegram_upload_ui.widgets.actions import Action
from telegram_upload_ui.widgets.pixmap import RoundedPixmap
from telegram_upload_ui.widgets.table import TableWidget, TableWidgetReadOnlyItem
from telegram_upload_ui.widgets.window import MainWindow

PHOTOS_DIRECTORY = os.path.expanduser('~/.config/telegram-upload/photos/')


class CircularListWidget(QtWidgets.QListWidget):
    """
    Circular ListWidget.

    https://stackoverflow.com/questions/16239552/pyqt-qlistwidget-with-infinite-scrolling
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            if self.currentRow() == self.count()-1:
                self.setCurrentRow(0)
                return
        elif event.key() == Qt.Key_Up:
            if self.currentRow() == 0:
                self.setCurrentRow(self.count()-1)
                return

        # Otherwise, parent behavior
        super().keyPressEvent(event)


class ConfirmUploadDialog(QtWidgets.QDialog):

    def __init__(self, parent, **kwargs):
        self.parent_window: 'TelegramUploadWindow' = kwargs.pop('parent_window')
        self.files = list(map(UploadFile, kwargs.pop('files', [])))
        self.selected_dialog: Union['Dialog', None] = None
        super().__init__(parent, **kwargs)
        self.create_table()
        self.layout = QtWidgets.QVBoxLayout()

        central_layout = QtWidgets.QHBoxLayout()
        central_layout.addWidget(self.get_dialogs_list(), 1)
        central_layout.addWidget(self.tableWidget, 2)
        self.layout.addLayout(central_layout)

        upload_button = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        upload_button.accepted.connect(self.confirm)
        upload_button.rejected.connect(self.close)
        self.layout.addWidget(upload_button)
        self.setLayout(self.layout)
        self.setGeometry(350, 350, 600, 350)

    def confirm(self):
        for file in self.files:
            file.dialog = self.selected_dialog
        self.parent_window.add_files(self.files)
        self.parent_window.activateWindow()
        self.close()

    def get_dialogs_list(self):
        dialogs_list_widget = CircularListWidget()
        for i, dialog in enumerate(self.parent_window.telegram_client.iter_dialogs()):
            photo = os.path.join(PHOTOS_DIRECTORY, f'{dialog.id}.jpg')
            if not os.path.lexists(photo):
                photo = self.parent_window.telegram_client.download_profile_photo(
                    dialog, file=photo.rsplit('.jpg')[0]
                )
            if photo:
                icon = QIcon()
                icon.addPixmap(RoundedPixmap(photo))
                item = QtWidgets.QListWidgetItem(icon, dialog.name)
                item.setSizeHint(QSize(item.sizeHint().width(), 35))
            else:
                item = QtWidgets.QListWidgetItem(dialog.name)
            item.setData(1000, dialog)
            dialogs_list_widget.addItem(item)
            if i > 10:
                break
        dialogs_list_widget.itemActivated.connect(self.set_selected_dialog)
        return dialogs_list_widget

    def create_table(self):
        # Create table
        self.tableWidget = TableWidget(header_labels=(
            'File Name', 'Size', 'Caption', 'Force file', 'Upload',
        ))
        self.tableWidget.horizontalHeader().setMinimumHeight(25)
        for i, file in enumerate(self.files):
            line_edit = QtWidgets.QLineEdit()
            line_edit.textChanged.connect(lambda x: file.set_caption(x))
            force_file = QtWidgets.QCheckBox()
            force_file.stateChanged.connect(lambda x: file.set_force_file(x))
            upload = QtWidgets.QCheckBox()
            upload.setCheckState(Qt.CheckState.Checked)
            upload.stateChanged.connect(lambda x: file.set_is_active(x))
            self.tableWidget.add_row(
                QtWidgets.QTableWidgetItem(file.name),
                QtWidgets.QTableWidgetItem(file.human_size),
                line_edit,
                force_file,
                upload
            )
        self.tableWidget.update_rows_count()
        self.tableWidget.move(0, 0)

    def set_selected_dialog(self, item: QListWidgetItem):
        self.selected_dialog = item.data(1000)


class TelegramUploadWindow(MainWindow):
    window_title = 'Telegram Upload'
    geometry = (300, 300, 350, 250)

    def __init__(self, parent=None, telegram_client: 'Client' = None):
        super().__init__(parent)
        self.telegram_client = telegram_client
        self.createTable()
        self.setCentralWidget(self.tableWidget)
        self.show()

    def get_actions(self):
        # https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
        return [
            Action("folder", 'Select files', self, shortcut='Ctrl+F',
                   connect=self.get_files),
            Action("application-exit", 'Exit application', self,
                   shortcut='Ctrl+Q', connect=self.close),
        ]

    def get_files(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFiles)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.open_confirm_upload_dialog(filenames)

    def createTable(self):
        # Create table
        self.tableWidget = TableWidget(header_labels=(
            'File name', 'File size', 'Caption', 'Upload to', 'Force file', 'Progress'
        ))

    def create_status_bar(self):
        status_bar = QtWidgets.QStatusBar()
        status_bar.addWidget(QtWidgets.QLabel('Uploading 1/3 files'))
        status_bar.addWidget(QtWidgets.QProgressBar())
        self.setStatusBar(status_bar)

    def open_confirm_upload_dialog(self, files):
        dialog = ConfirmUploadDialog(self, parent_window=self, files=files)
        dialog.exec_()

    def add_files(self, files):
        self.files = files
        for file in files:
            force_file = QtWidgets.QTableWidgetItem()
            force_file.setIcon(QIcon.fromTheme('checkbox' if file.force_file else 'dialog-cancel'))
            self.tableWidget.add_row(
                TableWidgetReadOnlyItem(file.name),
                TableWidgetReadOnlyItem(file.human_size, align=Qt.AlignRight | Qt.AlignVCenter),
                TableWidgetReadOnlyItem(file.caption, align=Qt.AlignRight | Qt.AlignVCenter),
                TableWidgetReadOnlyItem(file.dialog.name, align=Qt.AlignRight | Qt.AlignVCenter),
                force_file,
                QtWidgets.QProgressBar(),
            )


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # client = None
    from telegram_upload.client import Client
    client = Client(CONFIG_FILE)
    client.start()
    # Create and show the form
    form = TelegramUploadWindow(telegram_client=client)
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
