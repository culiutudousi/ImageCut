# -*- coding: utf-8 -*-

# ===========================================================================================
# 
# What is ImageCut?
# 
# It can cut a long vertical image to many pieces conveniently, 
#   some parameters such as max resolution and max file size can be set when cutting.
# It is designed to cut these kind of images:
#   screenshot of a long web page
#   a doc or pdf file that saved as one image
# 
# ===========================================================================================
# 
# How to use ImageCut?
# 
# A basic process is as follows:
#   1. press "Open" button to open a image
#   2. "Left Click" on image to set cut line
#       "Right Click" to remove cut line
#       "Clear" button on remove all cut lines
#       "Ctrl" + "Mouse Wheel" to zoom in and out
#   3. press "Set" button to set parameters such as max resolution and max file size
#   4. press "Save" button to save cut pieces, finish when the "Save" button turns to green
#       cut pieces will be saved in the same directory as the origin image
#       cut pieces will be saved in jpg format
# 
# ===========================================================================================
# 
# Some disadvantages:
#
#   1. When pack into exe, the start-up time is to slow
#   2. The method to show display image wastes too much calculation
# 
# ===========================================================================================
# 
# Introduction of code
# 
# This code is based on python3 with PyQt5.
# There are 4 classes: MainWindow, SettingsDialog, ImgWidget, ImgProcess
#   1. MainWindow: main window that connects the other parts
#   2. SettingsDialog: a dialog that sets parameters when cutting
#   3. ImgWidget: a widget based on QLabel and ImgProcess 
#                   that can display and peocess images conveniently
#   4. ImgProcess: contains almost all algorithms of images such as zoom and cut
# 
# ===========================================================================================

import io
import sys
import math
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qt import Qt, QSize
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,  QLineEdit,
    QApplication, QScrollArea, QPushButton, QSpinBox, QDialog, QFileDialog, QInputDialog, QProgressDialog)
from PyQt5.QtGui import QPixmap, QImage, QPalette
from PyQt5.QtCore import QTimer


# Main window that connects the other parts
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        w = QWidget()
        self.setCentralWidget(w)
        self.setWindowTitle("ImageCut")
        self.setWindowIcon(QtGui.QIcon("img/cut.png"))
        self.resolution_limit = 6000000  # 6,000,000 Pixels
        self.file_size_limit = 2000  # 2,000 KB
        w.setStyleSheet("QWidget {background-color: rgb(70, 70, 70); color: beige};")

        # Set image with scroll
        self.canvas = ImgWidget()
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.canvas)
        self.scroll.setStyleSheet("QScrollArea {background-color: rgb(80, 80, 80); color: beige; border-style: outset; border-width: 1px; border-color: beige;};")

        # Set buttons
        self.contol = QWidget()
        btn_icon_size = QSize(30, 30)
        btn_style = "QPushButton {background-color: rgb(70, 70, 70); color: beige; border-style: outset; border-radius: 2px; border-width: 1px; border-color: beige; min-width: 3em; padding: 8px; font-size: 18px}" \
                    "QPushButton:pressed {background-color: rgb(60, 60, 60); border-color: rgb(100, 100, 100);};"
        
        self.open_btn = QPushButton('', self.contol)
        self.open_btn.clicked.connect(self.canvas.openFile)
        self.open_btn.setIcon(QtGui.QIcon("img/open.png"))
        self.open_btn.setIconSize(btn_icon_size)
        self.open_btn.setToolTip("Open")
        self.open_btn.setStyleSheet(btn_style)

        self.setting_btn = QPushButton('', self.contol)
        self.setting_btn.clicked.connect(self.settings)
        self.setting_btn.setIcon(QtGui.QIcon("img/set.png"))
        self.setting_btn.setIconSize(btn_icon_size)
        self.setting_btn.setToolTip("Set")
        self.setting_btn.setStyleSheet(btn_style)

        self.clear_btn = QPushButton('', self.contol)
        self.clear_btn.clicked.connect(self.canvas.clearCutPoint)
        self.clear_btn.setIcon(QtGui.QIcon("img/clear.png"))
        self.clear_btn.setIconSize(btn_icon_size)
        self.clear_btn.setToolTip("Clear")
        self.clear_btn.setStyleSheet(btn_style)

        self.save_btn = QPushButton('', self.contol)
        self.save_btn.clicked.connect(self.saveResult)
        self.save_btn.setIcon(QtGui.QIcon("img/save.png"))
        self.save_btn.setIconSize(btn_icon_size)
        self.save_btn.setToolTip("Save")
        self.save_btn.setStyleSheet(btn_style)

        self.btn_vbox = QVBoxLayout()
        self.btn_vbox.addWidget(self.open_btn)
        self.btn_vbox.addWidget(self.setting_btn)
        self.btn_vbox.addWidget(self.clear_btn)
        self.btn_vbox.addWidget(self.save_btn)
        self.btn_vbox.addStretch()
        
        self.contol.setLayout(self.btn_vbox)
        self.contol.setMaximumSize(70, 200)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.contol)
        self.hbox.addWidget(self.scroll)
        w.setLayout(self.hbox)

        self.resize(600, 400)
    
    # Called when "Set" button is pressed
    def settings(self):
        dialog_style = "* {background-color: rgb(90, 90, 90); color: beige; selection-background-color: rgb(5, 9, 61); font-size: 16px}" \
                       "QSpinBox:up-button {subcontrol-position: left top}" \
                       "QSpinBox:down-button {subcontrol-position: left bottom}"
        sd = SettingsDialog()
        sd.setStyleSheet(dialog_style)
        sd.setWindowIcon(QtGui.QIcon("img/cut.png"))
        sd.setInitDisplay(self.resolution_limit, self.file_size_limit)
        # When "ok" is pressed
        if sd.exec_():
            self.resolution_limit, self.file_size_limit = sd.getSettings()
        sd.destroy()
    
    # Called when "Save" button is pressed
    def saveResult(self):
        if self.canvas.hasFile():
            self.canvas.saveResult(self.resolution_limit, self.file_size_limit)
            self.save_btn.setIcon(QtGui.QIcon("img/finish.png"))
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.recoverSaveBtn)
            self.timer.setSingleShot(True)
            self.timer.start(1500)
    
    # Called in self.saveResult() to recover the icon of "Save" button
    def recoverSaveBtn(self):
        self.save_btn.setIcon(QtGui.QIcon("img/save.png"))


# A dialog that sets parameters such as max resolution and max file size
class SettingsDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Settings')
        grid = QGridLayout()

        grid.addWidget(QLabel('Max Resolution:', self), 0, 0, 1, 1)
        self.max_resolution_edit = QSpinBox(self)
        self.max_resolution_edit.setRange(1, 10000)
        self.max_resolution_edit.setSingleStep(100)
        self.max_resolution_edit.setWrapping(True)
        self.max_resolution_edit.setAlignment(Qt.AlignRight)
        grid.addWidget(self.max_resolution_edit, 0, 1, 1, 1)
        grid.addWidget(QLabel('0000 Px', self), 0, 2, 1, 1)

        grid.addWidget(QLabel('Max File Size:', self), 1, 0, 1, 1)
        self.max_file_size_edit = QSpinBox(self)
        self.max_file_size_edit.setRange(1, 1000)
        self.max_file_size_edit.setSingleStep(5)
        self.max_file_size_edit.setWrapping(True)
        self.max_file_size_edit.setAlignment(Qt.AlignRight)
        grid.addWidget(self.max_file_size_edit, 1, 1, 1, 1)
        grid.addWidget(QLabel('00 KB', self), 1, 2, 1, 1)

        buttonBox = QtWidgets.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(grid)

        spacerItem = QtWidgets.QSpacerItem(10, 6, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
    
    # Set init parameters when dialog is displayed
    def setInitDisplay(self, max_resolution, max_file_size):
        # Input Value: max resolution in Px, max file size in KB
        self.max_resolution_edit.setValue(int(max_resolution / 10000))
        self.max_file_size_edit.setValue(int(max_file_size / 100))
    
    def getSettings(self):
        # Return Value: max resolution in Px, max file size in KB
        return (self.max_resolution_edit.value() * 10000, self.max_file_size_edit.value() * 100)


# A widget based on QLabel and ImgProcess that can display and peocess images conveniently
# Main purpose is to set mousePressEvent and wheelEvent
class ImgWidget(QWidget):

    def __init__(self):
        super().__init__()
        
        self.img_clickable = True
        self.img = ImgProcess()
        self.lbl = QLabel(self)  # self.lbl.setPixmap() will be used to set display image
        self.file_name = ''
    
    def hasFile(self):
        if self.file_name:
            return True
        return False
    
    def setDisplayPercentage(self, percentage):
        self.lbl.setPixmap(self.img.setDisplayPercentage(percentage))
        self.setMinimumSize(self.img.getDisplaySize(0), self.img.getDisplaySize(1))
        self.setMaximumSize(self.img.getDisplaySize(0), self.img.getDisplaySize(1))
    
    def clearCutPoint(self):
        if self.file_name:
            self.lbl.setPixmap(self.img.clearCutPoint())

    def openFile(self):
        self.file_name, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'Image files(*.jpg , *.png , *.bmp)')
        print("Open file: {}".format(self.file_name))
        self.img.open(self.file_name)
        pixmap = self.img.getQPixmap()
        if pixmap:
            self.lbl.setPixmap(pixmap)
            self.lbl.adjustSize()
            self.setMinimumSize(self.img.getDisplaySize(0), self.img.getDisplaySize(1))
            self.setMaximumSize(self.img.getDisplaySize(0), self.img.getDisplaySize(1))
    
    def getPieceNum(self):
        return self.img.cleanCutPoint()

    def saveResult(self, resolution_limit=6000000, file_size_limit=2000):
        if self.file_name:
            folder = self.file_name.split('.')
            folder = ''.join(folder[0:-1])
            print("Cut resolution_limit: {}".format(resolution_limit))
            self.img.cutAndSave(folder=folder, resolution_limit=resolution_limit, file_size_limit=file_size_limit)

    def mousePressEvent(self, event):
        # Left click: add a cut line (number)
        if event.button() == Qt.LeftButton and self.img_clickable:
            self.lbl.setPixmap(self.img.addCutPoint(event.y()))
            print("Left click point: {}".format(event.y()))
        # Right click: remove cut lines (numbers) nearby
        elif event.button() == Qt.RightButton and self.img_clickable:
            self.lbl.setPixmap(self.img.removeCutPoint(event.y()))
            print("Right click point: {}".format(event.y()))
    
    def wheelEvent(self, event):
        # Ctrl + Wheel to zoom in and out
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            numDegrees = event.angleDelta().y() / 8
            if numDegrees > 0:
                self.lbl.setPixmap(self.img.reduceDisplay())
            elif numDegrees < 0:
                self.lbl.setPixmap(self.img.amplifyDisplay())
            self.setMinimumSize(self.img.getDisplaySize(0), self.img.getDisplaySize(1))
            self.setMaximumSize(self.img.getDisplaySize(0), self.img.getDisplaySize(1))
            self.lbl.adjustSize()
        else:
            return super().wheelEvent(event)


# Most algorithms of images
class ImgProcess():

    def __init__(self, img_name=None, display_percentage=0.3):
        self.has_img = False
        self.display_percentage = display_percentage
        self.cut_points = []
        self.open(img_name)

    def open(self, img_name=None):
        if img_name:
            try:
                self.img = Image.open(img_name).convert('RGB')
                self.img_w, self.img_h = self.img.size
                self.has_img = True
            except:
                self.img = None
                self.img_w, self.img_h = 0, 0

    def refreshDisplayImage(self):
        if self.has_img:
            # Resize the display image
            self.img_dp_w = int(self.img_w * self.display_percentage)
            self.img_dp_h = int(self.img_h * self.display_percentage)
            self.img_dp = self.img.resize((self.img_dp_w, self.img_dp_h), Image.ANTIALIAS)
            # Add cut lines
            for cp in self.cut_points:
                draw = ImageDraw.Draw(self.img_dp)
                cp_dp = int(cp * self.display_percentage)
                draw.line((0, cp_dp, self.img_dp_w, cp_dp), fill='red')
        else:
            self.img_dp = None
            self.img_dp_w, self.img_dp_h = 0, 0

    def getQPixmap(self):
        # Return Value: PyQt5.QtGui.QPixmap / None
        # When this function is called, the display image will be redrawn
        self.refreshDisplayImage()
        if self.has_img:
            return self.pil2Pixmap(self.img_dp)
        return None
    
    def getDisplaySize(self, n=None):
        if n == 0:
            return self.img_dp_w
        elif n == 1:
            return self.img_dp_h
        return (self.img_dp_w, self.img_dp_h)
    
    def setDisplayPercentage(self, percentage):
        self.display_percentage = percentage
        return self.getQPixmap()
    
    def amplifyDisplay(self):
        if self.display_percentage > 0.15:
            self.display_percentage = self.display_percentage - 0.1
        return self.getQPixmap()
    
    def reduceDisplay(self):
        self.display_percentage = self.display_percentage + 0.1
        return self.getQPixmap()

    def addCutPoint(self, cut_point_display):
        cut_point = int(cut_point_display / self.display_percentage)
        self.cut_points.append(cut_point)
        return self.getQPixmap()
    
    def removeCutPoint(self, cut_point_display, cut_radius=20):
        cut_point = int(cut_point_display / self.display_percentage)
        cut_range = range(cut_point - cut_radius, cut_point + cut_radius + 1)
        self.cut_points = [i for i in self.cut_points if i not in cut_range]
        return self.getQPixmap()
    
    def clearCutPoint(self):
        self.cut_points.clear()
        return self.getQPixmap()
    
    def cleanCutPoint(self):
        self.cut_points = [i for i in self.cut_points if 1 < i < self.img_h]
        self.cut_points = list(set(self.cut_points))
        self.cut_points.sort()
        self.piece_num = len(self.cut_points) + 1
        return self.piece_num
    
    def cutAndSave(self, folder='', resolution_limit=6000000, file_size_limit=2000):
        # Input Value: max resolution in Px, max file size in KB
        self.cleanCutPoint()
        reduce_scale = 0.95
        cut_points = [0] + self.cut_points + [self.img_h]
        img = self.img
        for i in range(len(cut_points) - 1):
            file_name = folder + "_part_{:2d}.jpg".format(i + 1)

            # Cut and zoom in to resolution_limit
            img_part = img.crop((0, cut_points[i], self.img_w, cut_points[i + 1]))
            part_width, part_height = img_part.size
            if part_width * part_height > resolution_limit:
                new_width = int(math.sqrt(resolution_limit / part_height * part_width)) - 1
                new_height = int(math.sqrt(resolution_limit / part_width * part_height)) - 1
                img_part = img_part.resize((new_width, new_height), Image.ANTIALIAS)
            
            # Zoom in to file size limit
            cur_size = img_part.size
            while True:
                cur_size = (int(cur_size[0] * reduce_scale), int(cur_size[1] * reduce_scale))
                resized_file = img_part.resize(cur_size, Image.ANTIALIAS)

                with io.BytesIO() as file_bytes:
                    # Using IO Bytes instead of Hard Disc
                    resized_file.save(file_bytes, optimize=True, quality=90, format='jpeg')
                    print("bytes size: {}".format(file_bytes.tell()))

                    if file_bytes.tell() < file_size_limit * 1000:  # from KB to bytes
                        file_bytes.seek(0, 0)
                        with open(file_name, 'wb') as f_output:
                            f_output.write(file_bytes.read())
                        break
            print("Saved {}".format(file_name))

    def pil2Pixmap(self, im):
        # Convert a image form PIL.Image to PyQt5.QtGui.QPixmap
        # Using ImageQt in Pillow is directly, but will crash in win10
        if im.mode == "RGB":
            r, g, b = im.split()
            im = Image.merge("RGB", (b, g, r))
        elif  im.mode == "RGBA":
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))
        elif im.mode == "L":
            im = im.convert("RGBA")
        im2 = im.convert("RGBA")
        data = im2.tobytes("raw", "RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap


if __name__ == '__main__':

    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec_())
