from PyQt5.QtWidgets import QFileDialog

def import_excel():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_name, _ = QFileDialog.getOpenFileName(None, "Select Excel File", "", "Excel Files (*.xls *.xlsx)", options=options)
    if file_name:
        print(f"File selected: {file_name}")
        return file_name  # 返回选中的文件路径
    else:
        print("No file selected.")
        return None  # 如果没有选择文件，返回 None
    
    