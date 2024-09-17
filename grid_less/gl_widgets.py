import ctypes
import numpy as np
import pyrr
import open3d as o3d

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from PyQt6.QtCore import QSize, QRect, Qt, QPoint

from PyQt6.QtGui import QSurfaceFormat, QPixmap, QImage
from PyQt6.QtOpenGL import QOpenGLVersionProfile
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import time

class ImageFrame(QOpenGLWidget):

    def __init__(self, width, height,line_set,length=None,poscolor=None):
        super().__init__()
        self.color = np.array([1,0,1], dtype=np.float32)
        self.width=width
        self.height=height
        self.setFixedSize(QSize(width,height))
        self.image_loaded = False
        hair_box = np.array([-0.41,0.41,1.12 ,1.94 , -0.41, 0.41])
        hair_box_center = np.array([(hair_box[0]+hair_box[1])/2,(hair_box[2]+hair_box[3])/2,(hair_box[4]+hair_box[5])/2])
        self.hair_box_center=hair_box_center
        far = 5.0
        VIEW = np.array([hair_box[0]-hair_box_center[0],hair_box[1]-hair_box_center[0], hair_box[2]-hair_box_center[1], hair_box[3]-hair_box_center[1], far-(hair_box[5]-hair_box_center[2]), far-(hair_box[4]-hair_box_center[2])])  # 视景体的left/right/bottom/top/near/far六个面
        EYE = np.array([hair_box_center[0],hair_box_center[1], far]) 
        LOOK_AT = np.array([hair_box_center[0],hair_box_center[1], hair_box_center[2]])
        EYE_UP = np.array([0.0,1.0, 0.0])
        self.shift_to_zero_matrix = pyrr.matrix44.create_from_translation(-hair_box_center)
        self.rotate_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        self.shift_back_matrix = pyrr.matrix44.create_from_translation(hair_box_center)
        self.view_matrix = pyrr.matrix44.create_look_at(EYE, LOOK_AT, EYE_UP)
        self.proj_matrix = pyrr.matrix44.create_perspective_projection_from_bounds(VIEW[0], VIEW[1], VIEW[2], VIEW[3], VIEW[4], VIEW[5])
        self.line_set = line_set
        if length is not None:
            self.count_hair=np.asarray(length*2,dtype=np.intc)
        else:
            self.count_hair=None
        self.poscolor = poscolor

        self.button_mode = None
        self.last_pos = None
        self.delete_points = []
        self.l = 1

    def initializeGL(self):
        
        glClearColor(1.0,1.0,1.0,1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)

        self.make_assets()

        self.make_shaders()
    
    def make_assets(self):

        line_set = self.line_set
        self.hair_lineset_vbo = glGenBuffers(1)
        self.hair_lineset_vao = glGenVertexArrays(1)
        print("load",self.hair_lineset_vao)
        lines=np.asarray(line_set.lines)
        points=np.asarray(line_set.points)+[0,0.01,0]
        index = lines.reshape(-1)
        self.start_hair = [0]
        self.count_hair = []
        self.poscolor = []
        index_p=0
        length_p=0
        mu, sigma = 0, 20
        r = np.random.normal(mu, sigma)
        color = [r/255.0,r/255.0,r/255.0,0]
        self.poscolor.append(color)
        self.poscolor.append(color)
        for i in range(2,index.shape[0],2):
            if index[i]!=index[i-1]:
                r = np.random.normal(mu, sigma)
                color = [r/255.0,r/255.0,r/255.0,0]
                self.start_hair.append(i)
                self.count_hair.append(self.start_hair[-1]-self.start_hair[-2])
            self.poscolor.append(color)
            self.poscolor.append(color)
        print(index_p)
        self.count_hair.append(index.shape[0]-self.start_hair[-1])
        self.count_hair_len = len(self.count_hair)
        self.start_hair=np.asarray(self.start_hair,dtype=np.intc)
        self.count_hair=np.asarray(self.count_hair,dtype=np.intc)
        vertices = points[index]
        verticesCol = self.poscolor
        # vertices = points.reshape((-1,6000,3))[:,550,:]#[lines.reshape((-1,6000,2))[:,550,:].reshape((-1,))]#
        vertices = np.array(vertices, dtype=np.float32)
        verticesCol = np.array(verticesCol, dtype=np.float32)
        verticesverticesCol = np.concatenate([vertices.reshape((-1,)),verticesCol.reshape((-1,))])
        print("load",self.hair_lineset_vao)
        glBindVertexArray(self.hair_lineset_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.hair_lineset_vbo)
        glBufferData(GL_ARRAY_BUFFER, verticesverticesCol.nbytes, verticesverticesCol, GL_STATIC_DRAW)
        print(vertices.nbytes)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE,0, ctypes.c_void_p(vertices.nbytes))

        mesh = o3d.io.read_triangle_mesh("../HairStep/data/head_model.obj")
        mesh.compute_vertex_normals()
        triangles=np.asarray(mesh.triangles)
        vertices=np.asarray(mesh.vertices)
        vertices=vertices[triangles.reshape((-1,))]
        normals=np.asarray(mesh.triangle_normals)
        normals=np.repeat(normals,3,0)
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        verticesnormals = np.concatenate([vertices.reshape((-1,)),normals.reshape((-1,))])
        self.count_body = triangles.shape[0]*3
        self.body_vbo = glGenBuffers(1)
        self.body_vao = glGenVertexArrays(1)
        glBindVertexArray(self.body_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.body_vbo)
        glBufferData(GL_ARRAY_BUFFER, verticesnormals.nbytes, verticesnormals, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,0, ctypes.c_void_p(vertices.nbytes))
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def make_shaders(self):

        self.hair_shader = self.createShader(
            "shaders/hair_vertex.txt", 
            "shaders/hair_fragment.txt"
        )

        self.untextured_shader = self.createShader(
            "shaders/untextured_vertex.txt", 
            "shaders/untextured_fragment.txt"
        )

        glUseProgram(self.untextured_shader)
        self.model_matrix_location = glGetUniformLocation(self.untextured_shader, "model")
        self.tint_location = glGetUniformLocation(self.untextured_shader, "tint")
        glUseProgram(self.hair_shader)
        self.hair_model_matrix_location = glGetUniformLocation(self.hair_shader, "model")
        self.hair_tint_location = glGetUniformLocation(self.hair_shader, "tint")
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(m1 = model_transform,m2 = self.shift_to_zero_matrix)
        model_transform = pyrr.matrix44.multiply(m1 = model_transform,m2 = self.rotate_matrix)
        model_transform = pyrr.matrix44.multiply(m1 = model_transform,m2 = self.shift_back_matrix)
        model_transform = pyrr.matrix44.multiply(m1 = model_transform,m2 = self.view_matrix)
        model_transform = pyrr.matrix44.multiply(m1 = model_transform,m2 = self.proj_matrix)
        glUseProgram(self.untextured_shader)
        
        tint = np.array([0.5,0.5,0.5], dtype=np.float32)
        glUniform3fv(self.tint_location, 1, tint)
        glBindVertexArray(self.body_vao)
        glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, model_transform)
        glDrawArrays(GL_TRIANGLES, 0, self.count_body)
        
        glUseProgram(self.hair_shader)
        glUniformMatrix4fv(self.hair_model_matrix_location, 1, GL_FALSE, model_transform)

        tint = self.color
        glUniform3fv(self.hair_tint_location, 1, tint)
        glBindVertexArray(self.hair_lineset_vao)
        glMultiDrawArrays(GL_LINES, self.start_hair, self.count_hair, self.count_hair_len)
        
    def rotate(self,x,y):
        rotation_matrix = pyrr.matrix44.create_from_y_rotation(x)
        self.rotate_matrix = pyrr.matrix44.multiply(m1 = self.rotate_matrix,m2 = rotation_matrix)
        rotation_matrix = pyrr.matrix44.create_from_x_rotation(y)
        self.rotate_matrix = pyrr.matrix44.multiply(m1 = self.rotate_matrix,m2 = rotation_matrix)

    def mousePressEvent(self, event):
        if self.button_mode is None:
            if event.button() == Qt.MouseButton.RightButton:
                print('Right mouse button pressed at:', event.pos())
                self.button_mode = Qt.MouseButton.RightButton
                self.last_pos = event.pos()
    def mouseReleaseEvent(self, event):
        if event.button() == self.button_mode:
            if event.button() == Qt.MouseButton.RightButton:
                self.button_mode = None
    def mouseMoveEvent(self, event):
        if self.button_mode == Qt.MouseButton.RightButton:
            xy=event.pos()-self.last_pos
            self.rotate(xy.x()*-0.01,xy.y()*-0.01)
            self.last_pos = event.pos()
            self.repaint()
