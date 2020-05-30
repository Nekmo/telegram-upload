import os
import sys
import glob

from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon, QPixmap, QPainterPath, QPainter

from telegram_upload.client import Client
from telegram_upload.config import CONFIG_FILE
from telegram_upload_ui.widgets.actions import Action
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
        super().__init__(parent, **kwargs)
        self.createTable()
        self.layout = QtWidgets.QVBoxLayout()

        # label = QtWidgets.QLabel()
        # label.setText('Confirm before uploading files')
        # self.layout.addWidget(label)
        central_layout = QtWidgets.QHBoxLayout()

        dialogs_list_widget = CircularListWidget()
        for i, dialog in enumerate(self.parent_window.telegram_client.iter_dialogs()):
            photo = os.path.join(PHOTOS_DIRECTORY, f'{dialog.id}.jpg')
            if not os.path.lexists(photo):
                photo = self.parent_window.telegram_client.download_profile_photo(
                    dialog, file=photo.rsplit('.jpg')[0]
                )
            if photo:
                # https://stackoverflow.com/questions/36597124/rounded-icon-on-qpushbutton
                original_pixmap = QPixmap(photo)
                size = max(original_pixmap.width(), original_pixmap.height())
                rounded_pixmap = QPixmap(size, size)
                rounded_pixmap.fill(Qt.transparent)
                painter_path = QPainterPath()
                painter_path.addEllipse(rounded_pixmap.rect())
                painter = QPainter(rounded_pixmap)
                painter.setClipPath(painter_path)
                painter.fillRect(rounded_pixmap.rect(), Qt.black)

                painter.drawPixmap(abs(original_pixmap.width() - size) / 2,
                                   abs(original_pixmap.height() - size) / 2,
                                   original_pixmap.width(), original_pixmap.height(),
                                   original_pixmap)
                painter.end()

                # TODO: rounded_pixmap.fill(Transparent)
                icon = QIcon()
                icon.addPixmap(rounded_pixmap)
                # icon.addFile(photo)
                item = QtWidgets.QListWidgetItem(icon, dialog.name)
                item.setSizeHint(QSize(item.sizeHint().width(), 35))
            else:
                item = QtWidgets.QListWidgetItem(dialog.name)
            dialogs_list_widget.addItem(item)
            if i > 10:
                break
        central_layout.addWidget(dialogs_list_widget, 1)

        central_layout.addWidget(self.tableWidget, 2)
        self.layout.addLayout(central_layout)
        upload_button = QtWidgets.QDialogButtonBox()
        upload_button.addButton("Apply", QtWidgets.QDialogButtonBox.AcceptRole)
        upload_button.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.layout.addWidget(upload_button)
        self.setLayout(self.layout)
        self.setGeometry(350, 350, 600, 350)

    def createTable(self):
        # Create table
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        directory = os.path.expanduser('~')
        files = glob.glob1(directory, '*.mkv')
        self.tableWidget.setRowCount(len(files))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('File Name', 'Size'))
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setMinimumHeight(25)
        for i, file in enumerate(files):
            path = os.path.join(directory, file)
            # file
            item = QtWidgets.QTableWidgetItem(file)
            color = item.textColor()
            item.setFlags(Qt.ItemIsEditable)
            item.setTextColor(color)
            self.tableWidget.setItem(i, 0, item)
            # size
            item = QtWidgets.QTableWidgetItem(f'{os.path.getsize(path)}')
            item.setFlags(Qt.ItemIsEditable)
            item.setTextColor(color)
            self.tableWidget.setItem(i, 1, item)
        self.tableWidget.move(0, 0)
        # comboBox = QtWidgets.QComboBox()
        # progressBar = QtWidgets.QProgressBar()
        # progressBar.setValue(50)
        # self.tableWidget.setCellWidget(0, 1, comboBox)
        # self.tableWidget.setCellWidget(0, 2, progressBar)


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
                   connect=self.open_confirm_upload_dialog),
            Action("application-exit", 'Exit application', self,
                   shortcut='Ctrl+Q', connect=self.close),
        ]

    def getfiles(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        # dlg.setFilter("Text files (*.txt)")

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            print(filenames)

    def createTable(self):
        # Create table
        self.tableWidget = QtWidgets.QTableWidget(1, 3)
        item1 = QtWidgets.QTableWidgetItem("foo")
        comboBox = QtWidgets.QComboBox()
        progressBar = QtWidgets.QProgressBar()
        progressBar.setValue(50)
        self.tableWidget.setItem(0, 0, item1)
        self.tableWidget.setCellWidget(0, 1, comboBox)
        self.tableWidget.setCellWidget(0, 2, progressBar)

    def open_confirm_upload_dialog(self):
        dialog = ConfirmUploadDialog(self, parent_window=self)
        # dialog.ui = Ui_MyDialog()
        dialog.exec_()


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    client = Client(CONFIG_FILE)
    client.start()
    # Create and show the form
    form = TelegramUploadWindow(telegram_client=client)
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
