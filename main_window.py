import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QPushButton, QWidget, QVBoxLayout
from config import ConfigDialog
from import_data import *
import pandas as pd
from model_plot import DynamicPlot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import subprocess
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 800, 600)  # 设置窗口大小和位置

        self.file_name = None

        # 创建工具栏
        self.toolbar = self.addToolBar("Main Toolbar")
        self.add_toolbar_actions()

        # 使用 QVBoxLayout 管理器来布局
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # 添加线性图显示区域
        self.plot = DynamicPlot(window_width=100, y_range=(0, 20))
        self.layout.addWidget(self.plot)

        # 添加启动按钮
        self.init_start()
        

    def init_start(self):
        self.start_button = QPushButton("Start", self)
        self.start_button.setFixedSize(200, 50)
        self.start_button.clicked.connect(self.process_excel)
        self.layout.addWidget(self.start_button)  # 添加按钮到布局中

    def open_config_dialog(self):
        dialog = ConfigDialog(self)  # 假设 ConfigDialog 不需要特别的 parent 参数
        if dialog.exec_():
            settings = dialog.get_settings()
            print("Settings:", settings)  # 或者其他处理设置的代码

    def import_file(self):
        # Import the file once and store the path
        self.file_name = import_excel()
        self.list_str = json.dumps(self.file_name)
    
    def process_excel(self):
        if self.file_name:
            print(self.list_str)
            subprocess.run([sys.executable, "predwindow.py", self.list_str], check=True)
        else:
            print("File loading canceled by the user.")
    

    def add_toolbar_actions(self):
        # 添加 'Import' 动作
        import_action = QAction("Import", self)
        import_action.triggered.connect(self.import_file)  # 连接到导入功能
        self.toolbar.addAction(import_action)

        # 添加 'Config' 动作
        config_action = QAction("Config", self)
        config_action.triggered.connect(self.open_config_dialog)  # 连接到配置功能
        self.toolbar.addAction(config_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
