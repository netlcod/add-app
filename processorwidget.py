from PySide6.QtCore import Qt, Slot, Signal, QThread
from PySide6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
)

from processorworker import ProcessorWorker


class ProcessorWidget(QGroupBox):
    def __init__(self, title):
        super().__init__()

        self.configuration = {}
        self.is_processing = False

        self.worker_thread = QThread()
        self.worker = ProcessorWorker()
        self.worker.moveToThread(self.worker_thread)

        self.create_ui(title)

    def create_ui(self, title):
        self.setTitle("Processor: " + title)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setRange(0.001, 1)
        self.threshold_input.setDecimals(3)
        self.threshold_input.setSingleStep(0.001)
        self.threshold_input.setValue(0.5)
        self.threshold_input.valueChanged.connect(self.worker.set_threshold, Qt.QueuedConnection)

        nn_layout = QFormLayout()
        nn_layout.addRow("Threshold:", self.threshold_input)

        main_layout.addLayout(nn_layout)

    @Slot()
    def start(self):
        if not self.worker_thread.isRunning():
            self.worker.initialize(self.configuration)
            self.worker_thread.start()

    @Slot()
    def stop(self):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker.frame_counter = 0

    @Slot()
    def update_configuration(self, configuration):
        self.configuration.update(configuration)
