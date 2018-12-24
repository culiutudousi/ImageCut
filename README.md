# ImageCut

## What Is ImageCut?

It can cut a long vertical image to many pieces conveniently, some parameters such as max resolution and max file size can be set when cutting.
It is designed to cut these kind of images:
    screenshot of a long web page
    a doc or pdf file that saved as one image

## How to Use ImageCut?

A basic process is as follows:

* Press "Open" button to open a image
* Add cut lines
    * "Left Click" on image to add cut line 
    * "Right Click" to remove cut line 
    * "Clear" button on remove all cut lines 
    * "Ctrl" + "Mouse Wheel" to zoom in and out
* Press "Set" button to set parameters such as max resolution and max file size
* Press "Save" button to save cut pieces, finish when the "Save" button turns to green 
    * cut pieces will be saved in the same directory as the origin image 
    * cut pieces will be saved in jpg format

## Some Disadvantages

1. When pack into exe, the start-up time is to slow
2. The method to show display image wastes too much calculation

## Introduction of Code

This code is based on python3 with PyQt5.
There are 4 classes: MainWindow, SettingsDialog, ImgWidget, ImgProcess
1. MainWindow: main window that connects the other parts
2. SettingsDialog: a dialog that sets parameters when cutting
3. ImgWidget: a widget based on QLabel and ImgProcess that can display and peocess images conveniently
4. ImgProcess: contains almost all algorithms of images such as zoom and cut
