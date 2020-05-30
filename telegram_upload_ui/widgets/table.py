# https://stackoverflow.com/questions/51893313/adjust-the-size-width-height-of-a-custom-qtablewidget
from PySide2 import QtWidgets
from PySide2.QtCore import Qt


class TableWidgetReadOnlyItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        align = kwargs.pop('align', None)
        super().__init__(*args, **kwargs)
        color = self.textColor()
        self.setFlags(Qt.ItemIsEditable)
        self.setTextColor(color)
        self.current_row = 0
        if align:
            self.setTextAlignment(align)


class TableWidget(QtWidgets.QTableWidget):
    header_labels = None
    vertical_header_visible = False
    sorting_enabled = True
    section_resize_mode = QtWidgets.QHeaderView.Stretch

    def __init__(self, *args, **kwargs):
        header_labels = kwargs.pop('header_labels', self.header_labels)
        super().__init__(*args, **kwargs)
        if header_labels:
            self.setColumnCount(len(header_labels))
            self.setHorizontalHeaderLabels(header_labels)
        self.verticalHeader().setVisible(self.vertical_header_visible)
        self.setSortingEnabled(self.sorting_enabled)
        self.horizontalHeader().setSectionResizeMode(self.section_resize_mode)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setStretchLastSection(True)

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.current_row = 0

    def add_row(self, *fields):
        self.setRowCount(self.current_row + 1)
        for i, field in enumerate(fields):
            self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            if isinstance(field, QtWidgets.QTableWidgetItem):
                self.setItem(self.current_row, i, field)
            else:
                self.setCellWidget(self.current_row, i, field)
        self.current_row += 1

    def update_rows_count(self):
        self.setRowCount(self.current_row)
