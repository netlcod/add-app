import librosa
import librosa.display
import matplotlib.pyplot as plt
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class FeaturePlotter(QGroupBox):
    def __init__(self, title):
        super().__init__()

        self.configuration = {}

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)

        self.create_ui(title)

    def create_ui(self, title):
        self.setTitle("Feature: " + title)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)

    @Slot()
    def plot(self, feature_type, feature):
        self.ax.clear()
        if feature_type == "mfcc":
            plt.title("MFCC")
            librosa.display.specshow(
                feature,
                ax=self.ax,
                sr=int(self.configuration["SAMPLE_RATE"]),
                y_axis="linear",
                x_axis="time",
            )
            self.canvas.draw()
        elif feature_type == "mel":
            plt.title("Mel")
            librosa.display.specshow(
                feature,
                ax=self.ax,
                sr=int(self.configuration["SAMPLE_RATE"]),
                y_axis="mel",
                x_axis="time",
            )
            self.canvas.draw()

    @Slot()
    def update_configuration(self, configuration):
        self.configuration.update(configuration)
