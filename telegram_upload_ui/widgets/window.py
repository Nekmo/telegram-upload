from PySide2 import QtWidgets



class MainWindow(QtWidgets.QMainWindow):
    window_title = ''
    geometry = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_actions()
        if self.geometry:
            self.setGeometry(*self.geometry)
        if self.window_title:
            self.setWindowTitle(self.window_title)

    def get_actions(self):
        raise NotImplementedError

    def create_actions(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        toolbar = self.addToolBar('Exit')
        self.statusBar()
        for action in self.get_actions():
            fileMenu.addAction(action)
            toolbar.addAction(action)
