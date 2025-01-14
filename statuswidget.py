from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QGridLayout, QSizePolicy
from PySide6.QtCore import Slot

from indicator import Indicator


class StatusWidget(QGroupBox):
    def __init__(self, title):
        super().__init__()

        self.create_ui(title)

    def create_ui(self, title):
        self.setTitle("Status: " + title)

        layout = QGridLayout(self)

        label = QLabel("Probability:")
        self.probability_input = QLineEdit()
        self.probability_input.setEnabled(False)

        self.indicator = Indicator(25, 25)
        self.indicator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(label, 0, 0)
        layout.addWidget(self.probability_input, 0, 1)
        layout.addWidget(self.indicator, 0, 2)

        self.setLayout(layout)

    @Slot()
    def updateState(self, prediction, probability):
        self.indicator.setState(prediction)
        self.probability_input.setText(probability)
