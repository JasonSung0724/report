from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QMessageBox
import sys
from generate_report import ReportGenerator


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("訂單整理")
        self.setGeometry(100, 100, 600, 200)

        layout = QVBoxLayout()

        self.input_label = QLabel("選擇輸入檔案：")
        self.input_field = QLineEdit(self)
        self.input_button = QPushButton("瀏覽", self)
        self.input_button.clicked.connect(self.select_input_file)

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.input_button)

        self.output_label = QLabel("輸出檔案檔名：")
        self.output_field = QLineEdit(self)

        layout.addWidget(self.output_label)
        layout.addWidget(self.output_field)

        self.generate_button = QPushButton("生成報告", self)
        self.generate_button.clicked.connect(self.generate_report_handler)

        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def select_input_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇輸入的 Excel 檔案", "", "Excel Files (*.xlsx *.xls);;All Files (*)", options=options)
        if file_path:
            self.input_field.setText(file_path)

    def output_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "輸出檔案名", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_path:
            self.output_field.setText(file_path)

    def generate_report_handler(self):
        input_path = self.input_field.text()
        output_path = self.output_field.text()

        if not input_path or not output_path:
            QMessageBox.critical(self, "錯誤", "請選擇輸入檔案路徑和輸出檔案檔名")
            return

        try:
            generator = ReportGenerator()
            generator.generate_report(
                input_data_path=input_path,
                output_path=output_path,
            )
            QMessageBox.information(self, "成功", f"報告已成功生成！\n儲存於：{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"生成報告時發生錯誤：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
