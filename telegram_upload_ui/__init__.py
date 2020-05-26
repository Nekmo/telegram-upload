import sys
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon


class Form(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        textEdit = QtWidgets.QTextEdit()
        self.setCentralWidget(textEdit)

        # https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
        exitAct = QtWidgets.QAction(QIcon.fromTheme("application-exit"), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        selectFiles = QtWidgets.QAction(QIcon.fromTheme("folder"), 'Select files', self)
        selectFiles.setShortcut('Ctrl+F')
        selectFiles.setStatusTip('Select files')
        selectFiles.triggered.connect(self.getfiles)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(selectFiles)
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(selectFiles)
        toolbar.addAction(exitAct)

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


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
