import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QAction, QFileDialog
from PyQt5.QtCore import QTimer, Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pandas as pd
import tensorflow as tf  
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler

# Load the pre-trained models without compiling
modelbad = tf.keras.models.load_model("AE_bad2.h5", compile=False)
modelgood = tf.keras.models.load_model("AE_good2.h5", compile=False)

# Define a new optimizer and compile models with it
optimizer = tf.keras.optimizers.Adam()
modelbad.compile(optimizer=optimizer, loss='mse')
modelgood.compile(optimizer=optimizer, loss='mse')


class VisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulator")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.toolbar = self.addToolBar("Main Toolbar")
        self.add_toolbar_actions()

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Test entry')
        self.ax.set_ylabel('Mean square error (MSE)')
        self.line_good, = self.ax.plot([], [], 'r', label='Good AE')
        self.line_bad, = self.ax.plot([], [], 'b', label='Bad AE')
        self.ax.legend()

        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.healthy_label = QLabel("State of toolwear: HEALTHY", self)
        self.healthy_label.setStyleSheet("color: green; font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.healthy_label, alignment=Qt.AlignTop | Qt.AlignRight)
        self.healthy_label.hide()  # Hide initially

        self.warning_label = QLabel("State of toolwear: UNHEALTHY!!", self)
        self.warning_label.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.warning_label, alignment=Qt.AlignTop | Qt.AlignRight)
        self.warning_label.hide()  # Hide initially

        self.btn_start = QPushButton("Start")
        self.btn_start.setFixedWidth(100)  # Set fixed width
        self.btn_start.clicked.connect(self.start_evaluation)
        self.layout.addWidget(self.btn_start, alignment=Qt.AlignHCenter)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setFixedWidth(100)  # Set fixed width
        self.btn_stop.clicked.connect(self.stop_evaluation)
        self.layout.addWidget(self.btn_stop, alignment=Qt.AlignHCenter)

        self.evaluating = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.index = 0
        self.window_size = 10

        self.files = []

    def start_evaluation(self):
        # Load the test dataset and scale it
        if self.files:
            rawdataset = pd.read_excel(self.files[0])
            sc = StandardScaler()
            self.rawdataset = sc.fit_transform(rawdataset)   
        else:
            print("no file imported")
        if not self.evaluating:
            self.evaluating = True
            self.index = 0
            self.timer.start(1000)  # Start QTimer after "start" button clicked
    
    def add_toolbar_actions(self):
        # 添加 'Import' 动作
        import_action = QAction("Import", self)
        import_action.triggered.connect(self.import_excel)  # 连接到导入功能
        self.toolbar.addAction(import_action)
    
    def import_excel(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Excel File", "", "Excel Files (*.xls *.xlsx)", options=options)
        if file_name:
            print(f"File selected: {file_name}")
            self.files.append(file_name)
        else:
            print("No file selected or selection canceled.")
        return self.files


    def stop_evaluation(self):
        if self.evaluating:
            self.evaluating = False
            self.timer.stop()  # Stop the QTimer

    def update_plot(self):
        if self.files:
        # Ensure we do not go out of index bounds
            if self.index <= len(self.rawdataset) - self.window_size:
                window_data = self.rawdataset[self.index:self.index + self.window_size]

                # Make predictions
                pred_good = modelgood.predict(window_data)
                pred_bad = modelbad.predict(window_data)

                # Calculate mean absolute errors
                mae_good = mean_absolute_error(window_data, pred_good)
                mae_bad = mean_absolute_error(window_data, pred_bad)

                # Update the plot
                self.line_good.set_data(range(len(self.line_good.get_xdata()) + 1), list(self.line_good.get_ydata()) + [mae_good])
                self.line_bad.set_data(range(len(self.line_bad.get_xdata()) + 1), list(self.line_bad.get_ydata()) + [mae_bad])

                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw()

                # Show warning label if bad AE performs better than good AE
                if mae_bad < mae_good:
                    self.warning_label.show()
                else:
                    self.warning_label.hide()

                if mae_bad > mae_good:
                    self.healthy_label.show()
                else:
                    self.healthy_label.hide()

                # Increment the index for the next window
                self.index += 1
        else: 
            print("please import excel first")
            self.evaluating = False
            self.timer.stop()

def main():
    app = QApplication(sys.argv)
    window = VisualizationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
