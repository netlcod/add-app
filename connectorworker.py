from PySide6.QtCore import QObject, Signal, Slot, QByteArray
from PySide6.QtNetwork import QAbstractSocket, QTcpSocket


class ConnectorWorker(QObject):
    dataReady = Signal(QByteArray)
    frameReady = Signal(QByteArray)
    connectionState = Signal(QAbstractSocket.SocketState)

    def __init__(self, parent=None):
        super(ConnectorWorker, self).__init__(parent)

        self.data_part = False
        self.frame_hop = 0
        self.frame_size = 0
        self.data_buffer = QByteArray()
        self.socket = QTcpSocket()

        self.socket.stateChanged.connect(self.on_state_changed)
        self.socket.readyRead.connect(self.on_data_received)

    @Slot()
    def set_frame_hop(self, hop: float):
        self.frame_hop = hop

    @Slot()
    def set_frame_size(self, size: int):
        self.frame_size = size

    @Slot(QAbstractSocket.SocketState)
    def on_state_changed(self, state):
        self.connectionState.emit(state)

    @Slot()
    def connect_to_server(self, ip: str, port: int):
        if self.socket.state() == QAbstractSocket.UnconnectedState:
            self.socket.connectToHost(ip, port)

    @Slot()
    def disconnect_from_server(self):
        if self.socket.state() in [
            QAbstractSocket.ConnectingState,
            QAbstractSocket.ConnectedState,
        ]:
            self.socket.disconnectFromHost()

    @Slot()
    def on_data_received(self):
        data = self.socket.readAll()

        if not self.data_part:
            index = data.indexOf(b"\r\n\r\n")
            if index >= 0:
                self.data_part = True
                data = data[index + 4 :]

        if self.data_part:
            self.data_buffer.append(data)
            self.dataReady.emit(data)

            if self.data_buffer.size() >= self.frame_size:
                frame = self.data_buffer.sliced(0, self.frame_size)
                self.data_buffer.remove(0, self.frame_hop * self.frame_size)
                self.frameReady.emit(frame)
