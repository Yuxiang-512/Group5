from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
from PyQt5.QtGui import QIntValidator

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Settings")
        self.layout = QVBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        self.speed_label = QLabel("Read Speed (ms):", self)
        self.speed_input = QLineEdit(self)
        self.speed_input.setValidator(QIntValidator(1, 10000, self))  # 设置读取速度的有效范围为1到10000毫秒
        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.speed_input)

        self.channel_label = QLabel("Channel Count:", self)
        self.channel_input = QLineEdit(self)
        self.channel_input.setValidator(QIntValidator(1, 128, self))  # 设置通道数的有效范围为1到128
        self.layout.addWidget(self.channel_label)
        self.layout.addWidget(self.channel_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_settings(self):
        return {
            'speed': self.speed_input.text(),
            'channels': self.channel_input.text()
        }

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    if dialog.exec_():
        settings = dialog.get_settings()
        print("Settings:", settings)
    sys.exit(app.exec_())

