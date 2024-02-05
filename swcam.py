#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------#
#                                                                                #
# IP Cam (2)                                                                     #
#                                                                                #
# Module       : swcam.py (main module)                                          #
# Version      : 24/01/20 R 2.0.0                                                #
# Last updated : 24/01/25                                                        #
# Author       : Swen Hopfe SH (dj)                                              #
#                                                                                #
# This is our ip-cam script in Python3, picamera2-library based on libcamera     #
# software. Tested with Raspberry Pi Zero 2 W and Camera Module 3.               #
#                                                                                #
#--------------------------------------------------------------------------------#
#                                                                                #
# Presets                                                                        #
#                                                                                #
# The scripts are located in a "scripts" folder in the Pi's home directory       #
# under "/home/~/scripts". To install paramiko and pythonmagick please do        #
# sudo apt install python3-paramiko                                              #
# sudo apt install python3-pythonmagick                                          #
#                                                                                #
# Notes                                                                          #
#                                                                                #
# This is our first build in this configuration. Reason for version number "2"   #
# is that there is a previous model in our development with different hardware.  #
#                                                                                #
#--------------------------------------------------------------------------------#
#                                                                                #
# Blink codes                                                                    #
#                                                                                #
# 3x short - boot finished, starting recording                                   #
# 2x long  - recording finished, sftp upload starts                              #
# 4x short - sftp upload finished, now shutting down                             #
# 1x long  - sftp upload error                                                   #
#                                                                                #
#--------------------------------------------------------------------------------#

import os
import signal
import sys
import time
import datetime
import subprocess
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import paramiko
import PythonMagick as pmagick
import RPi.GPIO as GPIO
from random import randint

#--------------------------------------------------------------------------------#
# settings

fuser     = "user"
fpass     = "path"
fhost     = "myhost.net"
fpath01   = "/httpdocs/.../.../"
fpath02   = "/httpdocs/.../.../"
flocal    = "/home/pi/scripts/"

psize     = (2304, 1296)        # image size px x px
pcrop     = "1680x944+250+170"  # cropping image with offset
pfont     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

filestamp = "%Y-%m-%d_%H-%M-%S"
picstamp  = "%d.%m.%Y %H:%M"

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(20, GPIO.OUT)
GPIO.output(20, GPIO.HIGH)

#--------------------------------------------------------------------------------#
# blink codes

def blink(type):

   if type == 1: # 3 x short
      GPIO.output(20, GPIO.LOW)
      time.sleep(0.3)
      GPIO.output(20, GPIO.HIGH)
      time.sleep(0.3)
      GPIO.output(20, GPIO.LOW)
      time.sleep(0.3)
      GPIO.output(20, GPIO.HIGH)
      time.sleep(0.3)
      GPIO.output(20, GPIO.LOW)
      time.sleep(0.3)
      GPIO.output(20, GPIO.HIGH)
   if type == 2: # 2 x long
      GPIO.output(20, GPIO.LOW)
      time.sleep(1)
      GPIO.output(20, GPIO.HIGH)
      time.sleep(1)
      GPIO.output(20, GPIO.LOW)
      time.sleep(1)
      GPIO.output(20, GPIO.HIGH)
   if type == 3: # 4 x short
      GPIO.output(20, GPIO.LOW)
      time.sleep(0.3)
      GPIO.output(20, GPIO.HIGH)
      time.sleep(0.3)
      GPIO.output(20, GPIO.LOW)
      time.sleep(0.3)
      GPIO.output(20, GPIO.HIGH)
      time.sleep(0.3)
      GPIO.output(20, GPIO.LOW)
      time.sleep(0.3)
      GPIO.output(20, GPIO.HIGH)
      time.sleep(0.3)
      GPIO.output(20, GPIO.LOW)
      time.sleep(0.3)
      GPIO.output(20, GPIO.HIGH)
   if type == 4: # 1 x long
      GPIO.output(20, GPIO.LOW)
      time.sleep(1)
      GPIO.output(20, GPIO.HIGH)

#--------------------------------------------------------------------------------#
# program entry
#--------------------------------------------------------------------------------#

if __name__ == "__main__":

   # console welcome screen
   print(" ")
   print("--------------------------------")
   print("  Starte IP Cam R2.0 240120...  ")
   print("--------------------------------")
   print(" ")
   
#----------------------------------------------
# preparing
   
   print("Nehme Foto auf...")
   print(" ")
   
   blink(1)
   
   fname01 = "swcam.jpg"
   
   fname02 = datetime.datetime.now().strftime(filestamp) + ".jpg"
   pstring = datetime.datetime.now().strftime(picstamp)
   
#----------------------------------------------
# recording
   
   picam2 = Picamera2()
   picam2.start_preview(Preview.NULL)
   preview_config = picam2.create_preview_configuration()
   still_config = picam2.create_still_configuration({'size': psize})
   picam2.configure(still_config)
   picam2.start()
   time.sleep(2)
   metadata = picam2.capture_file("ftemp.jpg")
   picam2.close()
   
#----------------------------------------------
# image processing
   
   img = pmagick.Image("ftemp.jpg")
   img.quality(96)
   img.crop(pcrop)
   img.write("ftemp2.jpg")
   
   img2 = pmagick.Image("ftemp2.jpg")
   text = pmagick.DrawableText(200, 920,"Webcam Auerbach                 " + pstring + "                 www.smartewelt.de")
   img2.quality(96)
   img2.font(pfont)
   img2.fontPointsize(33)
   img2.penColor("#FFF")
   img2.draw(text)
   img2.write(fname01)
   
#----------------------------------------------
# sftp upload
   
   blink(2)
   print(" ")
   print("FTP-Uebertragung...")
   
   try:
      
      transport = paramiko.Transport((fhost))
      transport.connect(username=fuser, password=fpass)
      sftp = paramiko.SFTPClient.from_transport(transport)
      
      sftp.put(flocal + fname01, fpath01 + fname01)
      sftp.put(flocal + fname01, fpath02 + fname02)
      
      sftp.close()
      transport.close()
      
      print(" ")
      print("Fertig.")
      print(" ")
      blink(3)
   
   except:
   
      print(" ")
      print("Keine FTP-Uebertragung moeglich.")
      print(" ") 
      blink(4)
   
#----------------------------------------------
# ending up
   
   #bfl = False
   #if GPIO.input(21) == 0: bfl = True
   
   GPIO.cleanup()
   
   #if bfl : subprocess.call(["sudo","shutdown","now"])
   
   subprocess.call(["sudo","shutdown","now"])

#--------------------------------------------------------------------------------#
# physical end
#--------------------------------------------------------------------------------#
