from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QFormLayout,
    QPushButton,
    QFileDialog,
)

from utils import parse_array_configuration, parse_model_configuration


class ConfigurationWidget(QGroupBox):
    configurationUpdated = Signal(dict)

    def __init__(self, title):
        super().__init__()

        self.configuration = {}

        self.create_ui(title)

    def create_ui(self, title):
        self.setTitle("Configuration: " + title)

        main_layout = QFormLayout()

        self.select_array_button = QPushButton("Select")
        self.select_array_button.clicked.connect(self.select_array)

        self.select_nn_button = QPushButton("Select")
        self.select_nn_button.clicked.connect(self.select_nn)

        main_layout.addRow("Microphone array:", self.select_array_button)
        main_layout.addRow("NN Model:", self.select_nn_button)

        self.setLayout(main_layout)

    @Slot()
    def select_array(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select microphone array",
            "",
            "json (*.json)",
            options=options,
        )
        if file_name:
            self.configuration.update(parse_array_configuration(file_name))
            self.configurationUpdated.emit(self.configuration)

    @Slot()
    def select_nn(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select NN model", "", "h5 (*.h5)", options=options)
        if file_name:
            self.configuration.update(parse_model_configuration(file_name))
            self.configurationUpdated.emit(self.configuration)
