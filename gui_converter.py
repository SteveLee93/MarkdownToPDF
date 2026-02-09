import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QProgressBar, QMessageBox, QListWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont

import converter

class ConversionThread(QThread):
    progress_update = pyqtSignal(str)
    finished_one = pyqtSignal(str, bool, str) # title, success, message
    all_finished = pyqtSignal()

    def __init__(self, items):
        super().__init__()
        self.items = items # List of file/dir paths

    def run(self):
        files_to_process = []
        for item in self.items:
            if os.path.isfile(item):
                if item.lower().endswith('.md'):
                    files_to_process.append(item)
            elif os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for file in files:
                        if file.lower().endswith('.md'):
                            files_to_process.append(os.path.join(root, file))
        
        total = len(files_to_process)
        if total == 0:
            self.progress_update.emit("No Markdown files found to process.")
            self.all_finished.emit()
            return

        for i, input_path in enumerate(files_to_process):
            try:
                self.progress_update.emit(f"Processing ({i+1}/{total}): {os.path.basename(input_path)}")
                
                # Determine output path (same dir, same name, .pdf extension)
                output_path = os.path.splitext(input_path)[0] + ".pdf"
                
                converter.convert_markdown_to_pdf(input_path, output_path)
                
                self.finished_one.emit(os.path.basename(input_path), True, "Success")
            except Exception as e:
                self.finished_one.emit(os.path.basename(input_path), False, str(e))
        
        self.progress_update.emit("All tasks completed.")
        self.all_finished.emit()

class MarkdownToPDFApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Markdown to PDF Converter (Drag & Drop)")
        self.setGeometry(100, 100, 600, 400)
        self.setAcceptDrops(True)

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Instructions Label
        self.label = QLabel("Drag and Drop Markdown files or folders here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 14))
        self.label.setStyleSheet("border: 2px dashed #aaa; border-radius: 10px; padding: 20px; color: #555;")
        layout.addWidget(self.label)

        # Log List
        self.log_list = QListWidget()
        layout.addWidget(self.log_list)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate by default
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if not urls:
            return
        
        file_paths = [u.toLocalFile() for u in urls]
        self.start_conversion(file_paths)

    def start_conversion(self, file_paths):
        self.label.setText("Processing...")
        self.label.setStyleSheet("border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; color: #4CAF50;")
        self.progress_bar.show()
        self.log_list.clear()

        self.worker = ConversionThread(file_paths)
        self.worker.progress_update.connect(self.update_status)
        self.worker.finished_one.connect(self.log_result)
        self.worker.all_finished.connect(self.conversion_finished)
        self.worker.start()

    def update_status(self, message):
        self.label.setText(message)

    def log_result(self, filename, success, message):
        if success:
            self.log_list.addItem(f"✅ {filename}: Converted")
        else:
            self.log_list.addItem(f"❌ {filename}: Failed - {message}")

    def conversion_finished(self):
        self.label.setText("Drop files again")
        self.label.setStyleSheet("border: 2px dashed #aaa; border-radius: 10px; padding: 20px; color: #555;")
        self.progress_bar.hide()
        QMessageBox.information(self, "Done", "All processing finished.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownToPDFApp()
    window.show()
    sys.exit(app.exec())
