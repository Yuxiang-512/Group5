import json
import sys
import threading
import time

import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
from keras.models import Model, load_model
from keras.layers import Input, Dense
from keras.optimizers import Adam


from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler

autoencoder_bad = tf.keras.models.load_model(
    "AE_bad.keras",
    custom_objects={'mse': tf.keras.losses.MeanSquaredError()}
)
autoencoder_good = tf.keras.models.load_model("AE_good.keras", custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

# defining the threshold that was determined during training
GAE_threshold = 0.3943116993758422
BAE_threshold = 0.29779311009455334

if len(sys.argv) > 1:
    try:
        # 直接获取第一个命令行参数并尝试解析 JSON 字符串
        address_list = json.loads(sys.argv[1])
        print("Received list:", address_list)

        # 读取 Excel 文件并打印成功信息
        rawdataset = pd.read_excel(address_list[0]).values
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
else:
    print("No file paths provided.")
    sys.exit(1)

sc = StandardScaler()
rawdataset = sc.fit_transform(rawdataset)




class DataGenerator:
    def __init__(self):
        self.integers = []
        self.floats = []
        self.indexnumber=0




    def generate_data(self):
        while True:
            time.sleep(1)

            #random_integer = random.randint(1, 420)
            row_data = rawdataset[self.indexnumber].reshape(1, 66)  
            pred_resultbad = autoencoder_good.predict(row_data)
            pred_resultgood = autoencoder_bad.predict(row_data)
            self.integers.append(mean_absolute_error(row_data,pred_resultgood) )
            self.floats.append(mean_absolute_error(row_data,pred_resultbad) )
            self.indexnumber +=1


class VisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AE")
        self.setGeometry(100, 100, 800, 600)

        self.data_generator = DataGenerator()
        self.data_generator_thread = threading.Thread(target=self.data_generator.generate_data)
        self.data_generator_thread.daemon = True
        self.data_generator_thread.start()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('time')
        self.ax.set_ylabel('MSE')
        self.line_integers, = self.ax.plot([], [], 'r', label='Good AE')
        self.line_floats, = self.ax.plot([], [], 'b', label='Bad AE')
        self.ax.legend()

        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.btn_begin = QPushButton("begin")
        self.btn_begin.clicked.connect(self.start_generation)
        self.layout.addWidget(self.btn_begin)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # triger

    def start_generation(self):
        self.data_generator_thread = threading.Thread(target=self.data_generator.generate_data)
        self.data_generator_thread.daemon = True
        self.data_generator_thread.start()

    def update_plot(self):
        self.line_integers.set_data(range(len(self.data_generator.integers)), self.data_generator.integers)
        self.line_floats.set_data(range(len(self.data_generator.floats)), self.data_generator.floats)

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        # check weather need warning
        if len(self.data_generator.integers) > 0 and len(self.data_generator.floats) > 0:
            latest_integer = self.data_generator.integers[-1]
            latest_float = self.data_generator.floats[-1]
            if latest_float < latest_integer:
                QMessageBox.warning(self, "warning!!", "Waining!!", QMessageBox.Ok)

def main():
    app = QApplication(sys.argv)
    window = VisualizationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()