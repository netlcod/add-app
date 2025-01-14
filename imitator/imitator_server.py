import sys
import os
import datetime
import numpy as np
from PySide6.QtCore import (
    QCoreApplication,
    QObject,
    QTimer,
    QByteArray,
    QDataStream,
    QIODevice,
)
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))


class TcpServer(QObject):
    def __init__(self, file_path, port: int):
        super().__init__()

        CHANNELS_COUNT = 67

        self.timer = QTimer()
        self.server = QTcpServer()
        self.sockets = []
        self.server.newConnection.connect(self.on_new_connection)
        self.server.listen(QHostAddress.Any, port)
        self.client_available = False
        self.bytes_send = 0

        self.signal = np.fromfile(file_path, dtype=np.int16)
        self.signal = self.signal.reshape(-1, CHANNELS_COUNT)

        print(f"Сервер запущен {self.server.serverAddress()}:{self.server.serverPort()}")

    def on_new_connection(self):
        self.client_available = True
        socket = self.server.nextPendingConnection()
        self.sockets.append(socket)
        socket.disconnected.connect(lambda: self.on_disconnected(socket))
        print("Клиент подключен")

        socket.write(b"HTTP HEADER\r\n\r\n")

        self.send_data(socket)

    def on_disconnected(self, socket: QTcpSocket):
        self.client_available = False
        self.sockets.remove(socket)
        socket.deleteLater()
        print("Клиент отключен")
        self.bytes_send = 0

    def send_data(self, socket: QTcpSocket):
        print("Отправка пакета")
        for i in range(0, self.signal.shape[0]):
            if self.client_available:
                data_vector = self.signal[i, :]

                byte_array = QByteArray()
                data_stream = QDataStream(byte_array, QIODevice.WriteOnly)
                data_stream.setByteOrder(QDataStream.LittleEndian)

                for value in data_vector:
                    data_stream.writeInt16(value)
                    self.bytes_send += 16

                socket.write(byte_array)
                socket.flush()
                print(f"Send {self.bytes_send} bytes")


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    file_path = os.path.join(SCRIPT_FOLDER, "fly_phantom06_sg_r.bin")
    server1 = TcpServer(file_path, 8081)

    sys.exit(app.exec())
