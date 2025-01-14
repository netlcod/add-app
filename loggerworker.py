import datetime

from PySide6.QtCore import (
    QObject,
    Slot,
    QTimer,
    QByteArray,
    QFile,
    QDataStream,
    QTextStream,
)


class LoggerWorker(QObject):
    def __init__(self, parent=None):
        super(LoggerWorker, self).__init__(parent)

        self.configuration = {}

        self.filename = str()
        self.fp_binary = None
        self.fp_processor = None

        self.audio_buffer = QByteArray()
        self.processor_buffer = QByteArray()

        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 секунда
        self.timer.timeout.connect(self.write_chunk)

    def initialize(self, configuration):
        self.configuration = configuration

        filename = "".join(
            [
                "logs\\",
                datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S "),
                self.filename,
            ]
        )

        self.fp_binary = QFile("".join([filename, ".bin"]))
        if not self.fp_binary.open(QFile.WriteOnly):
            return

        self.fp_processor = QFile("".join([filename, ".txt"]))
        if not self.fp_processor.open(QFile.WriteOnly):
            return

    @Slot()
    def set_filename(self, filename: str):
        self.filename = filename

    @Slot()
    def append_audio_data(self, data: QByteArray):
        self.audio_buffer.append(data)

    @Slot()
    def append_processor_data(self, predicted_class: str, probability: str):
        self.processor_buffer += QByteArray(f"{datetime.datetime.now()}\t{predicted_class}\t{probability}\n")

    @Slot()
    def write_chunk(self):
        ds_binary = QDataStream(self.fp_binary)
        ds_binary.setByteOrder(QDataStream.ByteOrder.LittleEndian)
        ds_binary.writeRawData(self.audio_buffer)

        ds_processor = QTextStream(self.fp_processor)
        ds_processor << self.processor_buffer

        self.audio_buffer.clear()
        self.processor_buffer.clear()

    @Slot()
    def start(self):
        self.timer.start()

    @Slot()
    def stop(self):
        self.timer.stop()
        self.fp_binary.close()
        self.fp_processor.close()
