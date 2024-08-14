import sys
from PyQt6.QtGui import (QAction, QPixmap, QImage)
from PyQt6.QtCore import (QSize, Qt)
from PyQt6.QtWidgets import (
  QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
  QPushButton, QFileDialog
)

import gl_widgets
import canvas
import torch
import cv2
import numpy as np
from PIL import Image
import torch
import torch.utils.data as data
import open3d as o3d
from numpy.linalg import inv
import glob
import subprocess
import shutil
import os
from sklearn.cluster import KMeans
import CustomColorPicker

device = 'cuda' if torch.cuda.is_available() else 'cpu'
class Parameter(QWidget):


  def __init__(self, title, start_value):

    super().__init__()
    self.layout = QHBoxLayout()
    self.label = QLabel(title)
    self.field = QLineEdit(str(start_value))
    self.layout.addWidget(self.label)
    self.layout.addWidget(self.field)
    self.setLayout(self.layout)
  
  def get_value(self):

    return self.field.text()

class Window(QMainWindow):


  def __init__(self):

    super().__init__()

    self.setWindowTitle("Image Editor")

    self.createMenu()

    self.create_widgets()

  def create_widgets(self):

    self.input_qpixmap = QPixmap()
    self.input_qpixmap.load('../HairStep/results/real_imgs/resized_img/grid.png')
    self.input_qpixmap = self.input_qpixmap.scaled(150,150,aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio)
    self.input_label = QLabel(self)
    self.input_label.setPixmap(self.input_qpixmap)
    
    self.mask_label = canvas.Canvas('../HairStep/results/real_imgs/resized_img/grid.png', '../HairStep/results/real_imgs/seg/grid.png')

    line_set = o3d.io.read_line_set("../HairStep/results/real_imgs/hair3D/grid.ply")
    self.image_frame = gl_widgets.ImageFrame(512,512,line_set)

    self.parameter_layout = QVBoxLayout()
    self.blender_btn = QPushButton("Blender")
    self.blender_btn.pressed.connect(self.blender_hair)
    self.update_btn = QPushButton("Update Hair")
    self.update_btn.pressed.connect(self.update_hair)
    self.cut_btn = QPushButton("Cut Hair")
    self.cut_btn.pressed.connect(self.cut_hair)
    self.add_btn = QPushButton("Add Mask")
    self.add_btn.pressed.connect(self.add_mask)
    self.rem_btn = QPushButton("Remove Mask")
    self.rem_btn.pressed.connect(self.rem_mask)
    self.col_btn = QPushButton("Hair Colors")
    self.col_btn.pressed.connect(self.col_mask)
    self.color_picker_weight = CustomColorPicker.CustomColorPicker(self.image_frame)
    self.col_mask()
    self.parameter_layout.addWidget(self.input_label)
    self.parameter_layout.addWidget(self.add_btn)
    self.parameter_layout.addWidget(self.rem_btn)
    self.parameter_layout.addWidget(self.col_btn)
    self.parameter_layout.addWidget(self.color_picker_weight)
    self.parameter_layout.addWidget(self.update_btn)
    self.parameter_layout.addWidget(self.blender_btn)

    self.parameter_frame = QWidget()
    self.parameter_frame.setFixedSize(QSize(300,512))
    self.parameter_frame.setLayout(self.parameter_layout)
    
    self.main_layout = QHBoxLayout()
    self.main_layout.addWidget(self.mask_label)
    self.main_layout.addWidget(self.image_frame)
    self.main_layout.addWidget(self.parameter_frame)
    self.main_widget = QWidget()
    self.main_widget.setLayout(self.main_layout)

    self.setCentralWidget(self.main_widget)
  
  def createMenu(self):

    self.menu_bar = self.menuBar()
    self.file_menu = self.menu_bar.addMenu("File")
    self.import_button = QAction("Import", self)
    self.import_button.triggered.connect(self.importImages)
    self.file_menu.addAction(self.import_button)
  def roty_hair(self):
    self.image_frame.rotate(0,0.1)
    self.image_frame.repaint()
  def rotx_hair(self):
    self.image_frame.rotate(0.1,0)
    self.image_frame.repaint()
  def cut_hair(self):
    self.image_frame.cut()
    self.image_frame.repaint()
  def add_mask(self):
    self.mask_label.brush_color = (255, 255, 255) 
    return
  def rem_mask(self):
    self.mask_label.brush_color = (0, 0, 0)
    return
  def col_mask(self):
    mask = np.equal(self.mask_label.imgv[:,:,0:1],255)
    colors = self.mask_label.imgr.reshape((-1,3))[mask.reshape((-1,))]
    colors = np.flip(colors,1)
    # 使用KMeans进行颜色分群
    num_clusters = 6  # 可以根据需要调整
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(colors)
    # 获取聚类中心 (即主颜色)
    colors = kmeans.cluster_centers_
    color = colors[0]
    self.color_picker_weight.resetColors(colors)
    self.color_picker_weight.setColor(self.color_picker_weight.rgb_to_hex(color[0],color[1],color[2]))
    return
  def update_hair(self):
    if os.path.exists("../HairStep/results/real_imgs/lmk"):
        shutil.rmtree("../HairStep/results/real_imgs/lmk")
    if os.path.exists("../HairStep/results/real_imgs/lmk_proj"):
        shutil.rmtree("../HairStep/results/real_imgs/lmk_proj")
    if os.path.exists("../HairStep/results/real_imgs/param"):
        shutil.rmtree("../HairStep/results/real_imgs/param")
    if os.path.exists("../HairStep/results/real_imgs/hair3D"):
        shutil.rmtree("../HairStep/results/real_imgs/hair3D")
    if os.path.exists("../HairStep/results/real_imgs/mesh"):
        shutil.rmtree("../HairStep/results/real_imgs/mesh")
    subprocess.run('cd .. && cd HairStep && python scripts/get_lmk.py --device cpu ', shell=True)
    subprocess.run('cd .. && cd HairStep && python -m scripts.opt_cam --device cpu ', shell=True)
    subprocess.run('cd .. && cd HairStep && python -m scripts.recon3D --device cpu', shell=True)
    self.main_layout.removeWidget(self.image_frame)
    self.image_frame.deleteLater()
    line_set = o3d.io.read_line_set("../HairStep/results/real_imgs/hair3D/grid.ply")
    self.image_frame = gl_widgets.ImageFrame(512,512,line_set)
    self.main_layout.insertWidget(1, self.image_frame)
    self.color_picker_weight.image_frame = self.image_frame
    self.col_mask()
  def blender_hair(self):
    color = self.color_picker_weight.color/255.0
    subprocess.run('blender --python blender/script.py -- '+str(color[0])+' '+str(color[1])+' '+str(color[2])+'', shell=True)
    return
  def importImages(self):
  
    filename = QFileDialog.getOpenFileName(self)
    if len(filename[0]) > 0:
        self.input_qpixmap.load(filename[0])
        self.input_qpixmap = self.input_qpixmap.scaled(150,150,aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio)
        self.input_label.setPixmap(self.input_qpixmap)
        
        
        
        imgr=cv2.imread(filename[0])
        cv2.imwrite('../HairStep/results/real_imgs/img/grid.png', imgr)
        
        subprocess.run('cd .. && cd HairStep && python -m scripts.img2hairstep --device cpu', shell=True)
        
        self.main_layout.removeWidget(self.mask_label)
        self.mask_label.deleteLater()
        self.mask_label = canvas.Canvas('../HairStep/results/real_imgs/resized_img/grid.png', '../HairStep/results/real_imgs/seg/grid.png')
        self.main_layout.insertWidget(0, self.mask_label)
        self.col_mask()

app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()
