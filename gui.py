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

class GUI:
    def __init__(self, server, outputQueue, inputQueue):
        self.root = Tk()
        self.server = server
        self.outputQueue = outputQueue
        self.inputQueue = inputQueue
        self.running = False
        self.root.title("Minecraft Server")
        self.root.geometry("600x400")
        self.root.iconbitmap('.\img\icon.ico')
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.root.bind("<Return>", self.submit_command)

        ## Menubar
        self.tabControl = ttk.Notebook(self.root)
        self.dashboardTab = ttk.Frame(self.tabControl, padding="5px")
        self.consoleTab = ttk.Frame(self.tabControl, padding="5px")
        self.serverSettingsTab = ttk.Frame(self.tabControl, padding="5px")
        self.tabControl.add(self.dashboardTab, text="Dashboard")
        self.tabControl.add(self.consoleTab, text="Console")
        self.tabControl.add(self.serverSettingsTab, text="Server Settings")

        self.tabControl.pack(expand=1, fill="both")

        ## Dashboard
        # Controls Frame
        self.controlsFrame = ttk.Frame(self.dashboardTab, relief=GROOVE, padding="5px")
        self.controlsFrame.grid(row=0, column=0)

        self.startServerButton = ttk.Button(self.controlsFrame, text="Start Server", command=self.server.start_server)
        self.stopServerButton = ttk.Button(self.controlsFrame, text="Stop Server", command=self.server.stop_server, state=DISABLED)

        self.startServerButton.pack(side=LEFT)
        self.stopServerButton.pack(side=RIGHT)

        # System Usage Frame
        self.systemUsageFrame = ttk.Frame(self.dashboardTab, relief=GROOVE, padding="5px")
        self.systemUsageFrame.grid(row=1, column=0, sticky=EW)
        
        self.cpuUsage = StringVar()
        self.ramUsage = StringVar()

        self.systemUsageLabel = ttk.Label(self.systemUsageFrame, text="System Usage: ")
        self.cpuUsageLabel = ttk.Label(self.systemUsageFrame, textvariable=self.cpuUsage)
        self.ramUsageLabel = ttk.Label(self.systemUsageFrame, textvariable=self.ramUsage)

        self.systemUsageLabel.pack(fill="x")
        self.cpuUsageLabel.pack(fill="x")
        self.ramUsageLabel.pack(fill="x")

        # Players Frame
        self.players = []
        self.playersUI = []

        self.playersFrame = ttk.Frame(self.dashboardTab, padding="5px", relief=GROOVE)
        # self.playersFrame.pack(expand=1, fill="y", side=RIGHT)

        self.playersLabel = ttk.Label(self.playersFrame, text="Players:         ").pack(side=TOP)
        

        ## Console Tab
        self.consoleText = Text(self.consoleTab, state=DISABLED)
        self.scrollbar = Scrollbar(self.consoleTab, command=self.consoleText.yview)
        self.consoleText["yscrollcommand"] = self.scrollbar.set
        self.consoleInput = Entry(self.consoleTab)
        self.consoleInput.pack(fill="x", side=BOTTOM)
        self.scrollbar.pack(fill="y", side=RIGHT)
        self.consoleText.pack(expand=1, fill="both", side=TOP)

        ## Server Settings
        # External Settings
        self.externalSettingsFrame = ttk.Frame(self.serverSettingsTab, padding="5px", relief=GROOVE)
        self.externalSettingsFrame.grid(row=0, column=0, sticky=NW)

        self.externalSettingsLabel = ttk.Label(self.externalSettingsFrame, text="JAR Settings:")
        self.externalSettingsLabel.grid(row=0, column=0, sticky=NW)
        self.ramVal = IntVar()
        self.ramScale = ttk.Scale(self.externalSettingsFrame, orient=HORIZONTAL,
                                    length=150,
                                    from_=1, to= round(psutil.virtual_memory().total / 1073000000),
                                    variable=self.ramVal,
                                    command=self.accept_whole_number_only)

        self.ramSpinbox = Spinbox(self.externalSettingsFrame, from_=1, to=round(psutil.virtual_memory().total / 1073000000),
                                    textvariable=self.ramVal,
                                    command=self.update,
                                    width=10)
        self.ramLabel = ttk.Label(self.externalSettingsFrame, text="RAM: ")
        self.ramLabel.grid(row=1, column=0, sticky=NW)
        self.ramScale.grid(row=2, column=0)
        self.ramSpinbox.grid(row=2, column=1)
        # Server.properties


    
    def accept_whole_number_only(self, e=None): #
        value = self.ramScale.get()                #
        if int(value) != value:                 # here to allow the ram scale
            self.ramScale.set(round(value))        # to only accept whole numbers
                                                #
    def update(self, e=None):                   #    #
        self.ramScale.set(self.ramSpinbox.get())      #

    def add_console_line(self):
        if not self.outputQueue.empty():
            try:
                line = self.outputQueue.get()
                self.consoleText.config(state=NORMAL)
                self.consoleText.insert(END, f"{line}\n")
                self.consoleText.config(state=DISABLED)
                self.consoleText.yview_moveto("1.0")
                if " INFO]: Closing Server" in line:
                    self.server.stop_server(False)
            except Exception:
                print(Exception)
        self.root.after(10, self.add_console_line)

    def updateUI(self):
        ## System Usage
        self.cpuUsage.set(f"CPU Usage: {psutil.cpu_percent()}%")
        self.ramUsage.set(f"RAM Usage: {str(psutil.virtual_memory().used / 1073000000)[:4]}/{round(psutil.virtual_memory().total / 1073000000)} GB")

        self.root.after(1000, self.updateUI)

    def submit_command(self, event):
        global console

        command = self.consoleInput.get()
        self.inputQueue.put(command)
        self.consoleInput.delete(0, END)

    def on_exit(self):
        if not self.running:
            self.root.destroy()
            sys.exit()
        else:
            messagebox.showerror("Error", "Please stop the server before closing.")