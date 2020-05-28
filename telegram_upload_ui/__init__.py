import os
import sys
import glob

from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QVBoxLayout, QHeaderView


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
        super().__init__(parent, **kwargs)
        self.createTable()
        self.layout = QVBoxLayout()
        label = QtWidgets.QLabel()
        label.setText('Confirm before uploading files')
        self.layout.addWidget(label)
        self.layout.addWidget(self.tableWidget)
        upload_button = QtWidgets.QDialogButtonBox()
        upload_button.addButton("Apply", QtWidgets.QDialogButtonBox.AcceptRole)
        upload_button.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.layout.addWidget(upload_button)
        self.setLayout(self.layout)
        self.setGeometry(350, 350, 600, 350)

    def createTable(self):
        # Create table
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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


class Form(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        # textEdit = QtWidgets.QTextEdit()
        # self.setCentralWidget(textEdit)

        # https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
        exitAct = QtWidgets.QAction(QIcon.fromTheme("application-exit"), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        selectFiles = QtWidgets.QAction(QIcon.fromTheme("folder"), 'Select files', self)
        selectFiles.setShortcut('Ctrl+F')
        selectFiles.setStatusTip('Select files')
        # TODO: selectFiles.triggered.connect(self.getfiles)
        selectFiles.triggered.connect(self.open_confirm_upload_dialog)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(selectFiles)
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(selectFiles)
        toolbar.addAction(exitAct)

        self.createTable()
        self.setCentralWidget(self.tableWidget)
        # self.layout = QtWidgets.QVBoxLayout()
        # self.layout.addWidget(self.tableWidget)
        # self.setLayout(self.layout)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()

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
        dialog = ConfirmUploadDialog(self)
        # dialog.ui = Ui_MyDialog()
        dialog.exec_()


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
