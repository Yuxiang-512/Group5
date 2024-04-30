import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QPushButton
from config import ConfigDialog
from import_data import *
import pandas as pd

file_name = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 800, 600)  # 设置窗口大小和位置

        # 创建工具栏
        self.toolbar = self.addToolBar("Main Toolbar")

        # 添加导入和配置按钮
        self.add_toolbar_actions()
        self.init_start()

    def init_start(self):
        self.start_button = QPushButton("Start", self)
        self.start_button.setFixedSize(200, 50)
        self.start_button.move(100, 100)  # 设置按钮的位置

        self.start_button.clicked.connect(self.process_excel)
        self.setCentralWidget(self.start_button)

    def open_config_dialog(self):
        dialog = ConfigDialog(self)  # 假设 ConfigDialog 不需要特别的 parent 参数
        if dialog.exec_():
            settings = dialog.get_settings()
            print("Settings:", settings)  # 或者其他处理设置的代码

    def import_file(self):
        # Import the file once and store the path
        self.file_name = import_excel()
    
    def process_excel(self):
        file_path = self.file_name  # 获取用户选择的文件路径
        if file_path:
            df = pd.read_excel(file_path, engine='openpyxl')  # 使用pandas加载Excel文件
            print(df.head())  # 显示数据的前几行，或进行其他数据处理操作
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
