import sys
import os
import subprocess
import psutil
import multiprocessing
from multiprocessing import Process, Queue
from threading import Thread 
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

class Server:
    def __init__(self, outputQueue, inputQueue):
        self.outputQueue = outputQueue
        self.inputQueue = inputQueue
        self.running = True
        self.linebuffer = []
        self.gui = None

    def console_reader(self, f, buffer):
        while True:
            line=f.readline()
            if line:
                buffer.append(line)
            else:
                break

    def start_server(self):
        self.gui.running = True
        self.gui.startServerButton.config(state=DISABLED)
        self.gui.stopServerButton.config(state=NORMAL)
        self.process = Thread(target = self.p_start_server)
        self.process.daemon = True
        self.process.start()

    def p_start_server(self):
        while not self.inputQueue.empty():
            self.inputQueue.get()
        self.console = subprocess.Popen(["run.bat", "-u"], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd="./serverfiles")

        self.reader=Thread(target=self.console_reader,args=(self.console.stdout,self.linebuffer))
        self.reader.daemon = True
        self.reader.start()

        while True:
            if self.linebuffer:
                self.outputQueue.put(self.linebuffer.pop(0).rstrip().decode())
            if not self.inputQueue.empty():
                temp = self.inputQueue.get()
                self.console.stdin.write(f"{temp}\n".encode())
                self.console.stdin.flush()

    def stop_server(self, fromButton=True):
        if fromButton:
            self.inputQueue.put("stop")
        self.gui.startServerButton.config(state=NORMAL)
        self.gui.stopServerButton.config(state=DISABLED)
        self.gui.running = False