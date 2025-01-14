from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QGroupBox,
    QFormLayout,
    QLineEdit,
)
from PySide6.QtNetwork import QAbstractSocket

from indicator import Indicator
from connectorworker import ConnectorWorker


class ConnectorWidget(QGroupBox):
    def __init__(self, title):
        super().__init__()

        self.is_connected = False
        self.configuration = {}
        self.worker = ConnectorWorker()
        self.worker.connectionState.connect(self.state_changed)

        self.create_ui(title)

    def create_ui(self, title):
        self.setTitle("Connector: " + title)

        host_layout = QFormLayout()

        #
        self.address = "127.0.0.1"
        self.address_input = QLineEdit(self.address)
        self.address_input.textEdited.connect(self.set_address)

        self.port = "8081"
        self.port_input = QLineEdit(self.port)
        self.port_input.textEdited.connect(self.set_port)

        self.frame_hop = 0.0
        self.frame_hop_input = QLineEdit()
        self.frame_hop_input.textEdited.connect(self.set_frame_hop)

        self.indicator = Indicator(25, 25)

        host_layout.addRow("Address:", self.address_input)
        host_layout.addRow("Port:", self.port_input)
        host_layout.addRow("Frame hop, %:", self.frame_hop_input)
        host_layout.addRow("Connection Status", self.indicator)

        self.setLayout(host_layout)

    @Slot()
    def set_address(self, address):
        self.address = address

    @Slot()
    def set_port(self, port):
        self.port = port

    @Slot()
    def set_frame_hop(self, hop):
        self.frame_hop = hop

    @Slot()
    def connect_to_host(self):
        if not self.is_connected:
            self.worker.set_frame_size(
                int(
                    len(self.configuration["MIC_ARRAY"].keys())
                    * 2
                    * int(self.configuration["SAMPLE_RATE"])
                    * float(self.configuration["FEATURE_DURATION"])
                )
            )
            self.worker.set_frame_hop(float(self.frame_hop) / 100)
            self.worker.connect_to_server(self.address, int(self.port))

    @Slot()
    def disconnect_from_host(self):
        self.worker.disconnect_from_server()
        self.worker.data_part = False

    @Slot(QAbstractSocket.SocketState)
    def state_changed(self, state):
        print(state)
        if state == QAbstractSocket.SocketState.ConnectedState:
            self.is_connected = True
            self.indicator.setState("green")
        else:
            self.is_connected = False
            self.indicator.setState("red")

    @Slot()
    def update_configuration(self, configuration):
        self.configuration.update(configuration)
