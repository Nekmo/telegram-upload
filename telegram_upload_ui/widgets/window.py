from PySide2 import QtWidgets
from PySide2.QtWidgets import QStatusBar


class MainWindow(QtWidgets.QMainWindow):
    window_title = ''
    geometry = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_actions()
        self.create_status_bar()
        if self.geometry:
            self.setGeometry(*self.geometry)
        if self.window_title:
            self.setWindowTitle(self.window_title)

    def get_actions(self):
        raise NotImplementedError

    def create_actions(self):
        toolbar = self.addToolBar('Exit')
        for action in self.get_actions():
            toolbar.addAction(action)

    def create_status_bar(self):
        pass
