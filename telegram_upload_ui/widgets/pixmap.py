from PySide2.QtGui import QPixmap, Qt, QPainterPath, QPainter


class RoundedPixmap(QPixmap):
    def __init__(self, photo):
        # https://stackoverflow.com/questions/36597124/rounded-icon-on-qpushbutton
        original_pixmap = QPixmap(photo)
        size = max(original_pixmap.width(), original_pixmap.height())

        super().__init__(size, size)

        self.fill(Qt.transparent)
        painter_path = QPainterPath()
        painter_path.addEllipse(self.rect())
        painter = QPainter(self)
        painter.setClipPath(painter_path)
        painter.fillRect(self.rect(), Qt.black)
        painter.drawPixmap(abs(original_pixmap.width() - size) / 2,
                           abs(original_pixmap.height() - size) / 2,
                           original_pixmap.width(), original_pixmap.height(),
                           original_pixmap)
        painter.end()
