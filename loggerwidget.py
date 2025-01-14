from PySide6.QtCore import Qt, Slot, QThread
from PySide6.QtWidgets import (
    QGroupBox,
    QFormLayout,
    QLineEdit,
)

from loggerworker import LoggerWorker


class LoggerWidget(QGroupBox):
    def __init__(self, title):
        super().__init__()

        self.configuration = {}

        self.worker = LoggerWorker()

        self.create_ui(title)

    def create_ui(self, title):
        self.setTitle("Logger: " + title)

        self.setCheckable(True)
        self.setChecked(False)

        self.filename = ""
        self.filename_input = QLineEdit(self.filename)
        self.filename_input.textEdited.connect(self.worker.set_filename)

        main_layout = QFormLayout()
        main_layout.addRow("Filename:", self.filename_input)

        self.setLayout(main_layout)

    def start(self):
        self.worker.initialize(self.configuration)
        self.worker.start()

    def stop(self):
        self.worker.stop()

    @Slot()
    def update_configuration(self, configuration):
        self.configuration.update(configuration)
