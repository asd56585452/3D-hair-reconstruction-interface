import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QStackedLayout
from PyQt6.QtCore import QThread, pyqtSignal, Qt
class Mask(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")  # 半透明黑色背景
        self.label = QLabel("waiting...", self)
        self.label.setStyleSheet("color: white; font-size: 24px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # 使遮罩視窗覆蓋整個主視窗
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def resize(self, width,height):
        # 當主視窗大小改變時，調整遮罩大小
        self.setGeometry(0, 0, width, height)
