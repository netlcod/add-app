from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QActionGroup, QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QWidget,
    QTabWidget,
    QVBoxLayout,
)

from pandevice import PanDevice


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.create_devices()
        self.create_toolbar()
        self.create_ui()

    def create_devices(self):
        self.pan = PanDevice("pan")

    def create_toolbar(self):
        toolbar = QToolBar("Control Toolbar")
        self.addToolBar(toolbar)

        agroup_connection = QActionGroup(self)

        action_connect = QAction(QIcon("icons/connect-96px.png"), "Connect", agroup_connection)
        action_connect.setStatusTip("Connect")
        action_connect.triggered.connect(self.connect)

        action_disconnect = QAction(QIcon("icons/disconnect-96px.png"), "Disconnect", agroup_connection)
        action_disconnect.setStatusTip("Disconnect")
        action_disconnect.triggered.connect(self.disconnect)

        toolbar.addAction(action_connect)
        toolbar.addAction(action_disconnect)
        toolbar.addSeparator()

    def create_ui(self):
        self.setWindowTitle("add-app")
        self.main_widget = QTabWidget()

        self.tab1 = QWidget()
        self.main_widget.addTab(self.tab1, "Parameters")
        self.layout_tab1 = QVBoxLayout()
        self.layout_tab1.addWidget(self.pan.configurator)
        self.layout_tab1.addWidget(self.pan.connector)
        self.layout_tab1.addWidget(self.pan.processor)
        self.layout_tab1.addWidget(self.pan.logger)
        self.tab1.setLayout(self.layout_tab1)

        self.tab2 = QWidget()
        self.main_widget.addTab(self.tab2, "Processing")
        self.layout_tab2 = QVBoxLayout()
        self.layout_tab2.addWidget(self.pan.plotter)
        self.layout_tab2.addWidget(self.pan.status)
        self.tab2.setLayout(self.layout_tab2)

        self.setCentralWidget(self.main_widget)

    @Slot()
    def connect(self):
        self.pan.start()

    @Slot()
    def disconnect(self):
        self.pan.stop()


if __name__ == "__main__":
    import sys

    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
