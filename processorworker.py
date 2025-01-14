from PySide6.QtCore import QObject, Slot, Signal, QByteArray
import librosa
import tensorflow as tf
import numpy as np

# import debugpy

tf.config.set_visible_devices([], "GPU")
# tf.debugging.set_log_device_placement(True)


class _Predict_Service:
    _instance = None
    model = None

    def extract_feature(self, params, frame):
        FEATURE_TYPE = params["FEATURE_TYPE"]
        FEATURE_SIZE = int(params["FEATURE_SIZE"])
        SAMPLE_RATE = int(params["SAMPLE_RATE"])
        N_FFT = int(params["N_FFT"])
        HOP_LENGTH = int(params["HOP_LENGTH"])

        if FEATURE_TYPE == "mel":
            feature = self.extract_mel(
                frame=frame,
                sr=SAMPLE_RATE,
                n_fft=N_FFT,
                n_mels=FEATURE_SIZE,
                hop_length=HOP_LENGTH,
            )
        elif FEATURE_TYPE == "mfcc":
            feature = self.extract_mfcc(
                frame=frame,
                sr=SAMPLE_RATE,
                n_fft=N_FFT,
                n_mfcc=FEATURE_SIZE,
                hop_length=HOP_LENGTH,
            )

        return feature

    def extract_mel(self, frame, sr, n_mels, n_fft, hop_length):
        mel = librosa.feature.melspectrogram(y=frame, sr=sr, n_fft=n_fft, n_mels=n_mels, hop_length=hop_length)
        db_mel = librosa.power_to_db(mel)

        return db_mel

    def extract_mfcc(self, frame, sr, n_mfcc, n_fft, hop_length):
        mfcc = librosa.feature.mfcc(y=frame, sr=sr, n_fft=n_fft, n_mfcc=n_mfcc, hop_length=hop_length)

        return mfcc

    def predict(self, feature):
        probabilities = self.model.predict(feature, verbose=0)

        return probabilities


def Predict_Service(model):
    if _Predict_Service._instance is None:
        _Predict_Service._instance = _Predict_Service()

    tf.keras.backend.clear_session()
    _Predict_Service.model = tf.keras.models.load_model(model)
    return _Predict_Service._instance


class ProcessorWorker(QObject):
    newPrediction = Signal(str, str)
    newFeature = Signal(str, object)

    def __init__(self, parent=None):
        super(ProcessorWorker, self).__init__(parent)

        self.mapping = ["background", "uav"]
        self.predictor = None
        self.configuration = {}
        self.frame_counter = 0
        self.channels_count = 0
        self.physical_idx = []
        self.threshold = 0.5

    def initialize(self, configuration):
        self.configuration = configuration
        self.frame_counter = 0
        self.channels_count = len(configuration["MIC_ARRAY"].keys())
        self.physical_idx = list(
            map(
                lambda item: int(item[0]),
                filter(
                    lambda item: item[1].get("type") == "physical",
                    configuration["MIC_ARRAY"].items(),
                ),
            )
        )
        self.predictor = Predict_Service(self.configuration["MODEL_PATH"])

    def convert_data(self, data):
        ba = data.data()

        frame = np.frombuffer(ba, dtype=np.dtype("<i2"))
        frame = frame.reshape((-1, self.channels_count))

        signal2double = lambda signal: signal.astype(np.float32) / np.iinfo(np.int16).max
        frame = signal2double(frame)

        return frame

    def make_signal(self, buffer):
        payload = np.mean(buffer[:, self.physical_idx], axis=1)

        return payload

    @Slot()
    def set_threshold(self, threshold):
        self.threshold = threshold

    @Slot()
    def run_task(self, data: QByteArray):
        # debugpy.debug_this_thread()
        self.frame_counter += 1

        frame_buffer = self.convert_data(data)
        signal = self.make_signal(frame_buffer)

        frame_mean = np.mean(signal)
        frame_std = np.std(signal)
        frame_norm = (signal - frame_mean) / frame_std

        feature = self.predictor.extract_feature(self.configuration, frame_norm)
        self.newFeature.emit(self.configuration["FEATURE_TYPE"], feature)

        if self.configuration["NN_TYPE"] in ["cnn", "crnn", "cnn4", "cnn14"]:
            feature = feature[np.newaxis, ..., np.newaxis]
        elif self.configuration["NN_TYPE"] == "rnn":
            feature = feature[np.newaxis, ...]

        probabilities = self.predictor.predict(feature)

        predicted_index = 1 if probabilities[0][1] >= self.threshold else 0
        predicted_class = self.mapping[predicted_index]
        probability = probabilities[0, predicted_index]

        print(f"{self.frame_counter}\tPredicted: {predicted_class}\tProbability: {probability}")

        self.newPrediction.emit(predicted_class, str(probability))
