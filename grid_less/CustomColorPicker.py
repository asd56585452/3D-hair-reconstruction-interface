import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
import numpy as np

class CustomColorPicker(QWidget):
    def __init__(self,image_frame):
        super().__init__()
        self.image_frame = image_frame
        self.color = None
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.label = QLabel('选择一个颜色', self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.color_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.color_buttons_layout)

        self.setLayout(self.layout)

        self.addColorButtons([(255.0, 0.0, 0.0), (0.0, 255.0, 0.0), (0.0, 0.0, 255.0),
                              (255.0, 255.0, 0.0), (255.0, 0.0, 255.0), (0.0, 255.0, 255.0)])
                              

    def addColorButtons(self, colors):
        for color in colors:
            hex_color = self.rgb_to_hex(*color)
            btn = QPushButton()
            btn.setStyleSheet(f'background-color: {hex_color};')
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, color=hex_color: self.setColor(color))
            self.color_buttons_layout.addWidget(btn)

    def setColor(self, color):
        rgb = self.hex_to_rgb(color)
        if rgb[0]+rgb[1]+rgb[2]>255*3/2:
            self.label.setStyleSheet(f'QWidget {{ background-color: {color}; color: #000000 }}')
        else:
            self.label.setStyleSheet(f'QWidget {{ background-color: {color}; color: #FFFFFF }}')
        self.label.setText(f'selected color: {color}')
        self.color = np.array([rgb[0],rgb[1],rgb[2]], dtype=np.float32)
        self.image_frame.color = np.array([rgb[0],rgb[1],rgb[2]], dtype=np.float32)/255
        self.image_frame.repaint()
    def getColor(self):
        return hex_to_rgb(self.color)

    def resetColors(self,colors):
        # 移除 color_buttons_layout 中的所有小部件
        while self.color_buttons_layout.count():
            child = self.color_buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 重新添加预定义颜色按钮
        self.addColorButtons(colors)

    def rgb_to_hex(self, r, g, b):
        r = int(r)
        g = int(g)
        b = int(b)
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CustomColorPicker()
    ex.setWindowTitle('自定义颜色选择器示例')
    ex.resize(300, 200)
    ex.show()
    sys.exit(app.exec())
