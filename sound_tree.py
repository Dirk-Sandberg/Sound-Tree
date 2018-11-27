# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 22:36:31 2018

@author: Erik Sandberg
"""
import pythoncom
from pyHook import HookManager, HookConstants#, GetKeyState
import sys
#import winsound
import os
import pyaudio
import wave
import sys
import random


#print("Need to pip install pyaudio")
print("Made by Erik Sandberg")
#https://www.vb-audio.com/Cable/
print("Use this to install virtual cable: https://www.vb-audio.com/Cable/")
print("16 bit wav file necessary for audio files")
from threading import Thread


class SoundBoardPlayer():
    def __init__(self):
        self.baseFolder = os.getcwd()
        self.currentFolder = self.baseFolder
        self.audio = pyaudio.PyAudio()
        self.virtualCableIndex = self.getVirtualCableIndex()
        self.useVirtualCable = False

        
    def checkDirectory(self, listOfFiles, numpadKey):
        for file in listOfFiles:
            if numpadKey in file:
                # If it's a sound file, play it
                if (os.path.isfile(self.currentFolder + "/" + file)):
                    #print("File: " + file)
                    #self.playWav(self.currentFolder + "/" + file)
                    # ------------
                    thread = Thread(target=self.playWav, args=(self.currentFolder + "/" + file,))
                    thread.start()
                    #--------------
                    return self.baseFolder
                elif (os.path.isdir(self.currentFolder + "/" + file)):
                    # else if it's a directory, return that directory
                    #print("Dir: " + file)
                    return self.currentFolder + "/" + file
        print("No files exist with that numpadkey")
        return self.currentFolder

    def onKeyboardEvent(self,event):
        # in case you want to debug: uncomment1111 next line
        # print repr(event), event.KeyID, HookConstants.IDToName(event.KeyID), event.ScanCode , event.Ascii, event.flags
    #    if GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
    #        print("shift + snapshot pressed")
    #    elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and HookConstants.IDToName(event.KeyID) == 'D':
    #        print("ctrl + d pressed")
        keyStr = HookConstants.IDToName(event.KeyID).lower()
        #print(keyStr)
        if ("decimal" in keyStr) or ("oem_period" in keyStr):
            # Numpad period is "decimal"
            # Toggle using virtual cable / default audio device
            self.useVirtualCable = (not self.useVirtualCable)
        if "subtract" in keyStr:
            self.quitProgram()
            return True
        if "add" in keyStr:
            # Cancel path navigation, return to top
            self.currentFolder = self.baseFolder
            return True
        if "numpad" in keyStr:
            keyNum = keyStr[-1]
            if (keyNum != "0" ):
                self.currentFolder = self.checkDirectory(os.listdir(self.currentFolder), keyNum)
                #print("Moved into folder: " + self.currentFolder)
                return True
            elif "0" in keyStr:
                # Search below current folder for all .wav files and play one randomly
                randomWav = self.getRandomWav(self.currentFolder)
                self.playWav(randomWav)
                #thread = Thread(target=self.playWav,args=(randomWav    ,) )
                #thread.start()
                self.currentFolder = self.baseFolder
                return True

        return True
    def quitProgram(self):
        # EXIT PROGRAM
        self.audio.terminate()
        sys.exit(0)
        
    def playWav(self,absoluteWavFile):
        # Play wav over default output
        thread1 = Thread(target=self.playWavDefault, args = (absoluteWavFile,))
        thread1.start()
        # If they want to play over virtual cable as well
        if (self.useVirtualCable):
            thread = Thread(target=self.playWavVirtual, args = (absoluteWavFile,))
            thread.start()
       
    def playWavVirtual(self, absoluteWavFile):
        '''
        ************************************************************************
              This is the start of the "minimum needed to read a wave"
        ************************************************************************
        '''    
        # length of data to read.
        chunk = 1024
        # open the file for reading.
        wf = wave.open(absoluteWavFile, 'rb')
        #print("wf.getnchannels(): ", wf.getnchannels())
        # create an audio object
        # open stream based on the wave object which has been input.
        if (self.useVirtualCable):
            # Use the virtual cable as the output
            #print(self.audio.get_device_info_by_index(self.virtualCableIndex))
            stream =self.audio.open(format =
                            self.audio.get_format_from_width(wf.getsampwidth()),
                            channels = wf.getnchannels(),
                            rate = wf.getframerate(),
                            output = True,
                            output_device_index = self.virtualCableIndex)

        # read data (based on the chunk size)
        data = wf.readframes(chunk)
        # play stream (looping from beginning of file to the end)
        while data != b'':
            # writing to the stream is what *actually* plays the sound.
            #stream.write(data)
            stream.write(data)
            data = wf.readframes(chunk)
        # cleanup stuff.
        stream.close() 
        
    def playWavDefault(self, absoluteWavFile):
        '''
        ************************************************************************
              This is the start of the "minimum needed to read a wave"
        ************************************************************************
        '''    
        # length of data to read.
        chunk = 1024
        # open the file for reading.
        wf = wave.open(absoluteWavFile, 'rb')
        #print("wf.getnchannels(): ", wf.getnchannels())
        # create an audio object
        # open stream based on the wave object which has been input.

        # Use default audio output device
        stream =self.audio.open(format =
                        self.audio.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)                
        # read data (based on the chunk size)
        data = wf.readframes(chunk)
        # play stream (looping from beginning of file to the end)
        while data != b'':
            # writing to the stream is what *actually* plays the sound.
            #stream.write(data)
            stream.write(data)
            data = wf.readframes(chunk)
        # cleanup stuff.
        stream.close() 

    def getVirtualCableIndex(self):
        for i in range(self.audio.get_device_count()):
            audioDevice = self.audio.get_device_info_by_index(i)
            name = audioDevice['name'].lower()
            if ( ("virtual" in name ) and ( 'input' in name) ):
                return i # self.virtualCableIndex = i11.119
            
    def getRandomWav(self, curdir):
        possibleWavs = []
        for root, dirs, files in os.walk(curdir):
            for file in files:
                fullPath = os.path.realpath(root+"/"+file)
                if (fullPath.endswith(".wav") ) and (fullPath not in possibleWavs):
                    #print(fullPath)
                    possibleWavs.append(fullPath)
        n = random.randint(0,len(possibleWavs) - 1)
        #print("full: ", possibleWavs[n])
        return possibleWavs[n] # random wav file
        

soundBoard = SoundBoardPlayer()
hm = HookManager()
hm.KeyDown = soundBoard.onKeyboardEvent
hm.HookKeyboard()
# set the hook
pythoncom.PumpMessages()

