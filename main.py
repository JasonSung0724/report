from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                            QFileDialog, QVBoxLayout, QMessageBox, QHBoxLayout, QButtonGroup)
from PyQt5.QtCore import Qt
import sys
from generate_report import ReportGenerator


class DragDropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.setText(files[0])


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.platform = "shopline"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("訂單整理")
        self.setGeometry(100, 100, 600, 250)

        layout = QVBoxLayout()

        platform_layout = QHBoxLayout()
        self.platform_group = QButtonGroup(self)
        
        platforms = [("SHOPLINE", "shopline"), ("C2C", "c2c"), ("MIXX", "mixx"), ("奧世國際", "aoshi")]
        for i, (platform_label, platform_key) in enumerate(platforms):
            btn = QPushButton(platform_label)
            btn.setCheckable(True)
            btn.setProperty("platform_key", platform_key)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 15px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                }
                QPushButton:checked {
                    background-color: #007bff;
                    color: white;
                    border-color: #0056b3;
                }
                QPushButton:hover:!checked {
                    background-color: #e9ecef;
                }
            """)
            if i == 0:
                btn.setChecked(True)
            self.platform_group.addButton(btn, i)
            platform_layout.addWidget(btn)
        
        platform_layout.addStretch()
        layout.addLayout(platform_layout)

        input_layout = QHBoxLayout()
        self.input_label = QLabel("選擇輸入檔案：")
        self.input_field = DragDropLineEdit(self)
        self.input_field.setPlaceholderText("拖曳檔案到此或點擊瀏覽按鈕")
        self.input_button = QPushButton("瀏覽", self)
        self.input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.input_button)
        layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        self.output_label = QLabel("輸出檔案檔名：")
        self.output_field = QLineEdit(self)
        self.output_field.setPlaceholderText("輸入檔案名稱 (不需要副檔名)")
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_field)
        layout.addLayout(output_layout)

        self.generate_button = QPushButton("生成報告", self)
        self.generate_button.clicked.connect(self.generate_report_handler)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.generate_button)

        self.platform_group.buttonClicked.connect(self.on_platform_changed)

        self.setLayout(layout)

    def on_platform_changed(self, button):
        self.platform = button.property("platform_key") or button.text().lower()

    def select_input_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "選擇輸入的 Excel 檔案", 
            "", 
            "Excel Files (*.xlsx *.xls);;All Files (*)", 
            options=options
        )
        if file_path:
            self.input_field.setText(file_path)

    def generate_report_handler(self):
        input_path = self.input_field.text()
        output_path = self.output_field.text()

        if not input_path or not output_path:
            QMessageBox.critical(self, "錯誤", "請選擇輸入檔案路徑和輸出檔案檔名")
            return

        if not input_path.lower().endswith(('.xlsx', '.xls')):
            QMessageBox.critical(self, "錯誤", "請選擇 Excel 檔案 (.xlsx 或 .xls)")
            return

        try:
            generator = ReportGenerator()
            generator.generate_report(
                input_data_path=input_path,
                output_path=output_path,
                platform=self.platform
            )
            QMessageBox.information(self, "成功", f"報告已成功生成！\n儲存於：{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"生成報告時發生錯誤：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = App()
    ex.show()
    sys.exit(app.exec_())
