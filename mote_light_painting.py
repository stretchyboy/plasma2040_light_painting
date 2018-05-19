#!/usr/bin/python
from __future__ import print_function

import cherrypy

try:
    import thread
except:
    from threading import Thread

import os

try:
    import tkinter as tk
    import tkinter.ttk as ttk
except:
    import Tkinter as tk

import pygubu
from PIL import Image #PILLOW
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename

import webcolors
import sys
import time
import functools
import random

import logging
import os
import subprocess
import sys
import re

import gphoto2 as gp
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

MODE_IMAGE    = 1
MODE_COLOR    = 2
MODE_GRADIENT = 3
MODE_RANDOM   = 4

#gphoto2_command = 'gphoto2 --capture-image --filename "../LightPaintings/%Y%m%d-%H%M%S-%03n.%C"'
gphoto2_command = '''gphoto2 --set-config capturetarget=1 --keep --capture-image-and-download --filename """../LightPaintings/%Y%m%d-%H%M%S-%03n.%C"""'''

class MoteLightPainting(object):
    def __init__(self, gui=True, web=True):
        
        self.doQuick = False
        
        self.timeSlices = 320
        self.motePixelInSceenPixels = 1
        self.graphWidth = self.timeSlices
        self.cameraLag = 3
        self.currentColumn = 0
        self.simulate = False
        self.animate = False
        self.completeRepeats = 0
        self.motePixelInCm = 1
        self.mode = MODE_IMAGE
        self.color = (255, 0, 0)
        self.colorend = (0, 0, 255)

        self.bCameraBusy = False
        
        self.bControlCamera = False
        self.bPaintFromLeft = True
        self.bFacingScreen = True
        self.bReverseImage = False
        self.bFlipVertical = False
        self.bGradient = False
        self.bPaintWhite = False
        self.bPaintBlack = False
        self.bTween = False
        
        self.bLines = False
        self.bSpeckles = False
        self.bRandomAcrossRange = False
        
        self.iDuration = 5
        self.iRepeats = 1
        self.iDelay = 0
        self.motePixelInSceenPixels = 2
        
        self.gui = gui
        if(self.gui):
          self.init_gui()
          
        self.web = web
        if(self.web):
          self.init_web()
        
        self.connectToMote()
        
        self.iPixels = len(self.yToStick)
        
        self.aColourGrid = []
        self.aRandomGrid = []
        
        self.updateControls()
        self.filename = "images/Spectrum Vertical.png"
        self.loadImage()
        
        self.makeRandom()
        
    
    def init_web(self):
        print("Init Web")
        if not os.path.exists("sessions"):
            os.makedirs("sessions")
        
      
    
    def init_gui(self):
        print("Init GUI")
        #1: Create a builder
        self.builder = builder = pygubu.Builder()
        #2: Load an ui file
        builder.add_from_file(os.path.join(CURRENT_DIR, 'main_repeats.ui'))
        
        self.mainwindow = builder.get_object('mainwindow')

        self.canPreview = builder.get_object('canPreview')

        self.msgMessage = builder.get_object('msgMessage')

        self.scaDelay = builder.get_object('scaDelay')

        self.scaDuration = builder.get_object('scaDuration')

        builder.connect_callbacks(self)
    
    def beep(self, duration = 0.1):
        if (self.gui):
            freq = 440  # Hz
            os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))

    def addStick(self, channel, up=True, length=16, gammacorrect=True):    #from top
        if not self.simulate :
            self.mote.configure_channel(channel, length, gammacorrect)
        for i in range(length):
            if up:
                offset = length - 1 - i
            else:
                offset = i
            self.yToStick.append((channel, offset))

    def connectToMote(self):
        self.showMessage("Connecting")
        try:
            from mote import Mote
            self.mote = Mote()
            self.simulate = False
            self.showMessage("Connected")
            if not self.simulate :
                self.mote.clear()
                self.mote.show()
        except IOError:
            self.simulate = True
            self.showMessage("Simulating")

        self.yToStick = []
        self.addStick(1)
        self.addStick(2)
        self.addStick(3)
        self.addStick(4)
    
    def takePhoto2(self):
        self.bCameraBusy = True
        os.system(gphoto2_command)        
        self.bCameraBusy = False
        return 0
        
    def takePhoto(self):
        return self.takePhoto2()
        
        logging.basicConfig(
            format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
        self.bCameraBusy = True
        gp.check_result(gp.use_python_logging())
        camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(camera))
        print('Capturing image')
        file_path = gp.check_result(gp.gp_camera_capture(
            camera, gp.GP_CAPTURE_IMAGE))
        print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
        target = os.path.join('~/tmp', file_path.name)
        target = os.path.join(CURRENT_DIR,'..','LightPaintings', file_path.name)
        print('Copying image to', target)
        camera_file = gp.check_result(gp.gp_camera_file_get(
            camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL))
        gp.check_result(gp.gp_file_save(camera_file, target))
        if(self.completeRepeats == self.iRepeats):
            subprocess.call(['xdg-open', target])
        gp.check_result(gp.gp_camera_exit(camera))
        self.bCameraBusy = False
        return 0

    def quit(self, event=None):
        if not self.simulate :
            self.mote.clear()
            self.mote.show()
        self.mainwindow.quit()
    
    def reloadImage(self):
        self.mode = MODE_IMAGE
        self.loadImage()
      
    def loadImage(self):
        filename = self.filename
        self.im = Image.open(filename)
        iOriginalWidth, iOriginalHeight = self.im.size
        fAspect = float(iOriginalWidth) / float(iOriginalHeight)
        #targetWidth = int(fAspect * len(self.yToStick) * self.motePixelInCm)
        targetWidth = int(fAspect * self.iPixels * self.motePixelInCm)
        message = "Opened \""+os.path.basename(filename) + "\" "+str(targetWidth)+"cm wide"
        self.showMessage(message)
        self.rgb_im = self.im.convert('RGB').resize((self.timeSlices, self.iPixels), Image.NEAREST)
        self.width, self.height = self.rgb_im.size
        
        self.aImageValues = [[self.rgb_im.getpixel((x, y)) for x in range(self.width)] for y in range(self.height)]
        
        self.aRandomGrid = [[1 for x in range(self.width)] for y in range(self.height)]
        
        if(self.mode == MODE_IMAGE):
            self.drawPreview()

    def onFileChoose(self, event=None):
        self.filename = askopenfilename(initialdir = "images/",title = "Select file",filetypes = (("gif files","*.gif"),("png files","*.png"),("jpeg files","*.jpg"),("all files","*.*")))
        self.mode = MODE_IMAGE
        self.loadImage()

    def getColor(self, event=None):
        color = askcolor(self.color)
        if(color[0] == None):
            return
        if self.bPaintBlack == False:
            self.mode = MODE_COLOR
        self.color = color[0]
        self.drawPreview()

    def gradientChanged(self, event=None):
        self.mode = MODE_COLOR
        self.drawPreview()

    def getColorEnd(self, event=None):
        color = askcolor(self.colorend)
        if(color[0] == None):
            return
        self.bGradient = True
        self.updateControls()
        self.mode = MODE_COLOR
        self.colorend = color[0]
        self.drawPreview()

    def getImageX(self, processX):
        direction = (1 if self.bPaintFromLeft else -1)
        x = (0 if (direction == 1) else (self.timeSlices-1)) + (direction * processX)
        return x

    def getPreviewX(self, processX):
        direction = (1 if self.bPaintFromLeft else -1) * (1 if self.bFacingScreen else -1)
        x = (0 if (direction == 1) else (self.timeSlices-1)) + (direction * processX)
        return x

    def showColumn(self, x):
        iImageX = self.getImageX(x)
        if not self.simulate :
            try:
                for y in range(0, self.iPixels):
                    try:
                      if(self.bFlipVertical):
                        colour = self.aPixels[(self.iPixels-y)-1][iImageX]
                      else:
                        colour = self.aPixels[y][iImageX]
                    except:
                        colour = (0,0,0)
                    channel, pixel= self.yToStick[y % len(self.yToStick)]
                    if colour != (0, 0, 0):
                        r,g,b = colour
                        self.mote.set_pixel(channel, pixel, r, g, b)
                    else:
                        self.mote.set_pixel(channel, pixel, 0, 0, 0)

                self.mote.show()
            except IOError:
                self.simulate = True
                self.showMessage("Connection Failed. Simulating")

    def updateControls(self):
      if(self.gui):
        self.builder.tkvariables.__getitem__('bGradient').set(self.bGradient)
        self.builder.tkvariables.__getitem__('bReverseImage').set(self.bReverseImage)
        self.builder.tkvariables.__getitem__('bFacingScreen').set(self.bFacingScreen)
        self.builder.tkvariables.__getitem__('bPaintFromLeft').set(self.bPaintFromLeft)
        self.builder.tkvariables.__getitem__('bPaintWhite').set(self.bPaintWhite)
        self.builder.tkvariables.__getitem__('iPixels').set(self.iPixels)
        self.builder.tkvariables.__getitem__('iDuration').set(self.iDuration)
        self.builder.tkvariables.__getitem__('iRepeats').set(self.iRepeats)
        self.builder.tkvariables.__getitem__('bControlCamera').set(self.bControlCamera)
        self.builder.tkvariables.__getitem__('bPaintBlack').set(self.bPaintBlack)
        self.builder.tkvariables.__getitem__('bTween').set(self.bTween)
        
        self.builder.tkvariables.__getitem__('bLines').set(self.bLines)
        self.builder.tkvariables.__getitem__('bSpeckles').set(self.bSpeckles)
        self.builder.tkvariables.__getitem__('bRandomAcrossRange').set(self.bRandomAcrossRange)
        self.builder.tkvariables.__getitem__('bFlipVertical').set(self.bFlipVertical)
        
        self.scaDelay.set(self.iDelay)

    def updateParams(self):
      if(self.gui):
        self.bGradient = self.builder.tkvariables.__getitem__('bGradient').get()
        self.bReverseImage = self.builder.tkvariables.__getitem__('bReverseImage').get()
        self.bFacingScreen = self.builder.tkvariables.__getitem__('bFacingScreen').get()
        self.bPaintFromLeft = self.builder.tkvariables.__getitem__('bPaintFromLeft').get()
        self.bPaintWhite = self.builder.tkvariables.__getitem__('bPaintWhite').get()
        self.iPixels = self.builder.tkvariables.__getitem__('iPixels').get()
        self.iDuration = self.builder.tkvariables.__getitem__('iDuration').get()
        self.iRepeats = self.builder.tkvariables.__getitem__('iRepeats').get()
        self.bControlCamera = self.builder.tkvariables.__getitem__('bControlCamera').get()
        self.bPaintBlack = self.builder.tkvariables.__getitem__('bPaintBlack').get()
        self.bTween = self.builder.tkvariables.__getitem__('bTween').get()
        
        self.bLines = self.builder.tkvariables.__getitem__('bLines').get()
        self.bSpeckles = self.builder.tkvariables.__getitem__('bSpeckles').get()        
        self.bRandomAcrossRange = self.builder.tkvariables.__getitem__('bRandomAcrossRange').get()
        self.bFlipVertical = self.builder.tkvariables.__getitem__('bFlipVertical').get()
        
        self.iDelay = self.scaDelay.get()

    def getColColour(self, px):
        if(self.bGradient):
            r = int(round(self.color[0] + float(self.colorend[0] - self.color[0])*(float(px) / float(self.graphWidth))))
            g = int(round(self.color[1] + float(self.colorend[1] - self.color[1])*(float(px) / float(self.graphWidth))))
            b = int(round(self.color[2] + float(self.colorend[2] - self.color[2])*(float(px) / float(self.graphWidth))))
            return (r,g,b)
        return self.color
        
    def getFrameColour(self):
        if(self.iRepeats > 1):
            j = self.completeRepeats
            r = int(round(self.color[0] + float(self.colorend[0] - self.color[0])*(float(j) / float(self.iRepeats-1))))
            g = int(round(self.color[1] + float(self.colorend[1] - self.color[1])*(float(j) / float(self.iRepeats-1))))
            b = int(round(self.color[2] + float(self.colorend[2] - self.color[2])*(float(j) / float(self.iRepeats-1))))
            return (r,g,b)
        return self.color
        
    def transformThroughRandom(self, color, x, y, base=(0,0,0)):
        try:
            fMultiply = self.aRandomGrid[y][x]
        except:
            fMultiply == False
            
        if(fMultiply == False):
            return (0,0,0)
        else:
            return (
                int(round(fMultiply * float(color[0]-base[0])))+base[0], 
                int(round(fMultiply * float(color[1]-base[1])))+base[1], 
                int(round(fMultiply * float(color[2]-base[2])))+base[2]
                )
                            
    def dontPaintWhite(self, colour):
        if colour == (255, 255, 255) :
            return (0,0,0)
        return colour
    
    def makeInvertedPixel(self, color,x,y,):
        if color == (0, 0, 0):
            return self.aColorPixels[y][x]  
        else:
            return (0, 0, 0)
                        
    def makePixels(self):
        if self.bTween:
            self.aColorPixels = [[self.getFrameColour() for x in range(self.width)] for y in range(self.height)]
        else:
            if self.bRandomAcrossRange:
                self.aColorPixels = [[self.transformThroughRandom(self.colorend, x, y, self.color) for x in range(self.width)] for y in range(self.height)]
            else:
                self.aColorPixels = [[self.getColColour(x) for x in range(self.width)] for y in range(self.height)]
            
        if (self.mode == MODE_IMAGE):
            if self.bPaintBlack :
                self.aPixels = [[self.makeInvertedPixel(self.aImageValues[y][x],x,y) for x in range(self.width)] for y in range(self.height)]
                
            else:
                self.aRawPixels = self.aImageValues
        else: 
            self.aRawPixels = self.aColorPixels
         
        if self.bPaintBlack == False :
            self.aPixels = [[self.transformThroughRandom(self.aRawPixels[y][x], x, y) for x in range(self.width)] for y in range(self.height)]
            
        if self.bPaintWhite == False:
            self.aPixels = [[self.dontPaintWhite(self.aPixels[y][x]) for x in range(self.width)] for y in range(self.height)]
          
        if self.bReverseImage == True:
            try:
                self.aPixels = [[self.aPixels[y][(self.width - x) - 1] for x in range(self.width)] for y in range(self.height)]
            except:
                print("failing", len(self.aPixels), self.width , x)
                
    def drawColumn(self, x):
        iImageX = self.getImageX(x)
        iPreviewX = self.getPreviewX(x)
        iPreviewXend = self.getPreviewX(x+1)

        for y in range(0, self.iPixels):
            try :
                colour = self.aPixels[y][iImageX]
            except :
                colour = (0, 0, 0)
                
            if colour != (0, 0, 0):
                color = str(webcolors.rgb_to_hex(colour))
                self.canPreview.create_rectangle( iPreviewX, (y * self.motePixelInSceenPixels), iPreviewXend, (y * self.motePixelInSceenPixels) + self.motePixelInSceenPixels, width=0, fill=color)
        if self.bPaintBlack & (self.currentColumn > 0  and self.currentColumn < self.graphWidth):
            self.canPreview.create_rectangle( iPreviewX, (0), iPreviewXend, self.motePixelInSceenPixels *5, width=0, fill="#0F0")
                
    def doPreview(self, event=None):
        self.drawPreview()
    
    def changeRandom(self):
        self.updateParams()
        self.makeRandom()
        self.makePixels()
        self.drawPreview()
        
    def drawPreview(self):
        self.updateParams()
        self.makePixels()
        self.canPreview.create_rectangle(0, 0, self.graphWidth, (len(self.yToStick) * self.motePixelInSceenPixels), fill="black")
        for x in range(0, self.graphWidth):
            self.drawColumn(x)
    
    def makeRandom(self):
        self.aRandomGrid = [[False for x in range(self.width)] for y in range(self.height)]
        
        for y in range(self.iPixels):
            if(self.bLines):
                line = [random.randint(0, self.timeSlices), random.randint(0, self.timeSlices)]
                line.sort()
                start = line[0]
                end = line[1]
            else:
                start = 0
                end = self.timeSlices
            
            for x in range(0, self.timeSlices):
                if(x >= start and x <= end):
                    if(self.bSpeckles or self.bRandomAcrossRange):
                        level = random.random()
                    else:
                        level = 1
                    self.aRandomGrid[y][x]= level
    
    def refreshPixels(self):
        self.aImageValues = [[self.rgb_im.getpixel((x, y)) for x in range(self.width)] for y in range(self.height)]
        self.makePixels()
    
    def onShowEnd(self):
        if not self.simulate :
            self.mote.clear()
            self.mote.show()

        self.showMessage("Lights Finished")
        self.completeRepeats += 1

        if self.bControlCamera:
            while self.bCameraBusy:
                pass

        message = "Show "+str(self.completeRepeats) + "/"+str(self.iRepeats)+" Complete in "+str(time.time() - self.startTime)+"s"
        self.showMessage(message)

        try:
            self.im.seek(self.im.tell()+1)
            self.rgb_im = self.im.convert('RGB').resize((self.timeSlices, self.iPixels))
            self.refreshPixels()
            self.showMessage("Loaded next frame")
            self.drawPreview()
        except EOFError:
            try:
                if (self.im.tell() > 0):
                    self.im.seek(0)
                    self.rgb_im = self.im.convert('RGB').resize((self.timeSlices, self.iPixels))
                    self.refreshPixels()
                    print("Animation Looped")
            except:
                if (self.im.tell() > 0):
                    self.im = Image.open(self.filename)
                    self.rgb_im = self.im.convert('RGB').resize((self.timeSlices, self.iPixels))
                    self.refreshPixels()
                    print("Could not loop - Reloaded")        

        if(self.completeRepeats < self.iRepeats):
            
            self.singleShow()
        else:
            self.completeRepeats = 0 
        
        self.makeRandom()
        self.drawPreview()

    def startPhoto(self):
        if self.bControlCamera:
            thread.start_new_thread ( self.takePhoto , ())

    def show(self):
        self.canPreview.create_rectangle(0, 0, self.graphWidth, (len(self.yToStick) * self.motePixelInSceenPixels), fill="#000")
        if self.simulate:
            message = "Simulating"
        else:
            message = "Show "+str(self.completeRepeats+1)+"/"+str(self.iRepeats)+" started"
        self.showMessage(message)
        duration = float(self.scaDuration.get())
        self.stepTime = int(1000 * duration / float(self.timeSlices))
        self.stepTimeS = duration / float(self.timeSlices)

        self.currentColumn = 0
        self.startTime = time.time()
        self.targetTime = time.time() + self.stepTimeS
        self.doColumn()

    def doColumn(self):
        if time.time() < self.targetTime:
            self.timer = self.mainwindow.after(1, self.doColumn)
            return

        thisColumn = self.currentColumn
        if self.currentColumn < self.graphWidth:
            self.targetTime += self.stepTimeS
            self.timer = self.mainwindow.after(1, self.doColumn)

            self.drawColumn(thisColumn)
            self.showColumn(thisColumn)

        else:
            self.onShowEnd()
        self.currentColumn += 1

    def showMessage(self, message):
        if(self.gui):
            self.builder.tkvariables.__getitem__('messageText').set(message)

    def on_btnDraw_clicked(self, event=None):
        if (self.currentColumn > 0  and self.currentColumn < self.graphWidth) or self.bCameraBusy:
            self.showMessage("Cannot start now, still running")
            return False
            
        self.updateParams()
        self.completeRepeats = 0
        self.singleShow()

    def drawCountdown(self):
        i = 1 + self.iFullDelay - self.delayRemaining
        width = self.graphWidth
        if self.iFullDelay > 0:
            width = i * self.graphWidth/self.iFullDelay
        
        self.canPreview.create_rectangle(0, 0, width, (len(self.yToStick) * self.motePixelInSceenPixels), fill="#000")
        message = "Show "+str(self.completeRepeats+1)+"/"+str(self.iRepeats)+" starts in "+str(self.delayRemaining)
        self.canPreview.itemconfigure(self.countdown_id, text=message)
        self.showMessage(message)

        
        if self.delayRemaining <= 4 and self.delayRemaining > 1:
            self.beep(0.1)
        
        self.delayRemaining -= 1
        
        if self.delayRemaining > 0:
            self.mainwindow.after(1000, self.drawCountdown)
        else:
          self.beep(0.3)

    def singleShow(self):
        if self.simulate:
            self.connectToMote()

        self.canPreview.create_rectangle(0, 0, self.graphWidth, (len(self.yToStick) * self.motePixelInSceenPixels), fill="#AAA")
        self.countdown_id = self.canPreview.create_text(100, self.graphWidth -100, fill="#F00", text=".....")
        
        delayTime = self.scaDelay.get()
        
        lag = 0
        if self.bControlCamera:
            lag = self.cameraLag
            
        #Start the countdown including the lag
        self.iFullDelay = delayTime + lag
        self.delayRemaining = self.iFullDelay
        self.drawCountdown()

        #start the camera shot after the delay without the lag
        self.mainwindow.after(delayTime * 1000, self.startPhoto)
        
        #start the show after waiting for delay & lag
        self.mainwindow.after((delayTime + lag) * 1000, self.show)

    def run(self):
        if(self.gui):
            self.mainwindow.mainloop()
            
    @cherrypy.expose
    def index(self):
        if 'count' not in cherrypy.session:
            cherrypy.session['count'] = 0
        cherrypy.session['count'] += 1
        return "Hello World!" + str(cherrypy.session['count'])
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def settings(self):
      data = cherrypy.request.json
      if(data):
        print("data", data);
        for field in data:
          self[field] = data[field]
        self.updateControls()
      
      return dict(self)
      

if __name__ == '__main__':
    web = True
    gui = not(web)
    app = MoteLightPainting(gui=gui, web=web)
    
    if web:
        #thread.start_new_thread (cherrypy.quickstart,(app, '/', "app.conf"))
        cherrypy.quickstart(app, '/', "app.conf")
    else:
        #thread.start_new_thread ( app.run , ())
        app.run()
    
        
    
