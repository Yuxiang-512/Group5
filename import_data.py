from PyQt5.QtWidgets import QApplication, QFileDialog

def import_excel():
    files = []
    while True:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Excel File", "", "Excel Files (*.xls *.xlsx)", options=options)
        if file_name:
            print(f"File selected: {file_name}")
            files.append(file_name)
        else:
            print("No file selected or selection canceled.")
            break
    return files

if __name__ == "__main__":
    app = QApplication([])
    selected_files = import_excel()
    print("Selected files:", selected_files)
