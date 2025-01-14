from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Slot


class Indicator(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.state = None
        self.setFixedSize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.state == "red":
            color = QColor(255, 0, 0)
        elif self.state == "yellow":
            color = QColor(255, 255, 0)
        elif self.state == "green":
            color = QColor(0, 255, 0)
        else:
            color = QColor(255, 255, 255)

        painter.setBrush(color)
        painter.drawEllipse(10, 10, 10, 10)

    @Slot()
    def setState(self, state):
        self.state = state
        self.update()
