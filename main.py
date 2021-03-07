# import sys
# import os
# import subprocess
# import psutil
# import multiprocessing
# from threading import Thread 
# from tkinter import *
# from tkinter import ttk
# from tkinter import messagebox
from multiprocessing import Process, Queue, freeze_support
from server import Server
from gui import GUI
import json

def start_gui(server, outputQueue, inputQueue):
    global gui
    global running

    # gui = GUI(server, outputQueue, inputQueue)
    server.gui = GUI(server, outputQueue, inputQueue)
    server.gui.root.after(10, server.gui.add_console_line)
    server.gui.root.after(10, server.gui.updateUI)
    server.gui.root.mainloop()

def check_for_updates():
    with open("config.json", "r") as file:
        currentVersion = json.load(file)["version"]
    print(currentVersion)


if __name__ == "__main__":
    freeze_support()
    global server

    check_for_updates()

    outputQueue = Queue()
    inputQueue = Queue()
    server = Server(outputQueue, inputQueue)

    pGUI = Process(target=start_gui, args=(server,outputQueue,inputQueue,))
    pGUI.start()
    pGUI.join()