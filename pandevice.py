from PySide6.QtCore import Qt, Slot
from PySide6.QtNetwork import QAbstractSocket

from configurationwidget import ConfigurationWidget
from connectorwidget import ConnectorWidget
from processorwidget import ProcessorWidget
from featurewidget import FeaturePlotter
from statuswidget import StatusWidget
from loggerwidget import LoggerWidget


class PanDevice:
    connector: ConnectorWidget
    processor: ProcessorWidget
    plotter: FeaturePlotter
    status: StatusWidget
    logger: LoggerWidget

    def __init__(self, name: str):
        self.configurator = ConfigurationWidget(name)
        self.connector = ConnectorWidget(name)
        self.processor = ProcessorWidget(name)
        self.plotter = FeaturePlotter(name)
        self.status = StatusWidget(name)
        self.logger = LoggerWidget(name)

        # Configurator
        self.configurator.configurationUpdated.connect(self.connector.update_configuration)
        self.configurator.configurationUpdated.connect(self.processor.update_configuration)
        self.configurator.configurationUpdated.connect(self.plotter.update_configuration)
        self.configurator.configurationUpdated.connect(self.logger.update_configuration)

        # Connector
        self.connector.worker.connectionState.connect(self.change_processor_state)
        self.connector.worker.frameReady.connect(self.processor.worker.run_task, Qt.QueuedConnection)

        # Processor
        self.processor.worker.newFeature.connect(self.plotter.plot, Qt.QueuedConnection)

        state_mapping = {"background": "red", "uav": "green"}
        self.processor.worker.newPrediction.connect(
            lambda pred, proba: self.status.updateState(state_mapping.get(pred, "yellow"), proba),
            Qt.QueuedConnection,
        )

        # Logger
        self.logger.toggled.connect(self.change_logger_state)

    @Slot()
    def start(self):
        self.connector.connect_to_host()

    @Slot()
    def stop(self):
        self.connector.disconnect_from_host()

    @Slot()
    def change_processor_state(self, state):
        if state == QAbstractSocket.SocketState.ConnectingState:
            self.processor.start()
            if self.logger.isChecked():
                self.logger.start()
        elif state == QAbstractSocket.SocketState.ClosingState:
            self.processor.stop()
            if self.logger.isChecked():
                self.logger.stop()

    @Slot()
    def change_logger_state(self, state):
        if state:
            self.connector.worker.dataReady.connect(self.logger.worker.append_audio_data, Qt.QueuedConnection)
            self.processor.worker.newPrediction.connect(self.logger.worker.append_processor_data, Qt.QueuedConnection)

        else:
            self.connector.worker.dataReady.disconnect(self.logger.worker.append_audio_data)
            self.processor.worker.newPrediction.disconnect(self.logger.worker.append_processor_data)
