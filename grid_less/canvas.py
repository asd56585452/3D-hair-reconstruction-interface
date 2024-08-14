import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent
from PyQt6.QtCore import Qt, QPointF

class Canvas(QLabel):
    def __init__(self, imgr_path, imgv_path, brush_size=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brush_size = brush_size
        self.brush_color = (255, 255, 255)  # Black color
        self.last_point = None
        self.imgr=cv2.imread(imgr_path)
        self.imgv=cv2.imread(imgv_path)
        self.imgv_path=imgv_path
        # Convert image to QImage and display it
        self.update_image()

    def update_image(self):
        imgr = cv2.addWeighted(self.imgr,0.5,self.imgv,0.5,0)
        height, width, channel = imgr.shape
        bytes_per_line = 3 * width
        q_image = QImage(imgr.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        self.setPixmap(QPixmap.fromImage(q_image))
        
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            current_point = event.position()
            if self.last_point is not None:
                self.draw_line(self.last_point, current_point)
            self.last_point = current_point
        else:
            self.last_point = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = event.position()
            self.draw_line(self.last_point, self.last_point)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = None
            cv2.imwrite(self.imgv_path,self.imgv)

    def draw_line(self, start_point, end_point):
        start = (int(start_point.x()), int(start_point.y()))
        end = (int(end_point.x()), int(end_point.y()))
        cv2.line(self.imgv, start, end, self.brush_color, self.brush_size)
        self.update_image()
