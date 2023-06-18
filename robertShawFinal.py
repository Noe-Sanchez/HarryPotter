from pathlib import Path
import serial
import sys
import csv
import os
import time
import matplotlib as mp
import matplotlib.pyplot as plt
import numpy as np
import random
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import Button


class Dashboard:

    def __init__(self, resolutionX, resolutionY, simulated=False, dark_mode = False) -> None:
        # start 115200 serial
        self.simulated=simulated
        if (not simulated):
            self.ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)
            self.ser.flushInput()
        self.currentResponse = None
        self.updateTime = 0.1 #100ms update time
        self.resolutionX = resolutionX
        self.resolutionY = resolutionY

        mp.use("TkAgg")
        self.graphEnabled = False

        self.counter = 0
        self.max_freq = 100
        self.max_v = 3.3

        if dark_mode:
            plt.style.use('dark_background')
        plt.ion()
        plt.show()

        self.win = 20
        self.max_l_min = 10
        self.max_psi = 100
        self.y = np.array(np.zeros([self.win]))
        self.y2 = np.array(np.zeros([self.win]))
        # setting the matplotlib    to be inside tkinter window
        self.fig, self.ax = plt.subplots(2)
        self.fig.tight_layout(pad=5.0)
        #get display dpi
        dpi = self.fig.get_dpi()
        # increase figure size considering current display dpi
        self.fig.set_size_inches(self.resolutionX/float(dpi),self.resolutionY/float(dpi))
        self.pline, = self.ax[0].plot(self.y, c = 'r')
        self.pline2, = self.ax[1].plot(self.y2, c = 'g')
        self.ax[0].set_title("Flow Sensor")
        self.ax[1].set_title("Pressure Sensor")
        self.ax[0].set_ylabel("l/min")
        self.ax[1].set_ylabel("psi")
        #set horizontal grid on
        self.ax[0].yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
        self.ax[1].yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
        self.ax[0].set_ylim(0, self.max_l_min)
        self.ax[1].set_ylim(0, self.max_psi)

        #set a button that runs the function start_graph
        self.axes = plt.axes([0.3, 0.000001, 0.4, 0.1])
        # show the plot without blocking the rest of the program
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def start_graph(self, val):
        print("Starting graph")
        startData='s'
        if not self.simulated:
            self.ser.write(startData.encode('utf-8'))
        self.graphEnabled = True

    def updateGraph(self):
        if (self.graphEnabled and ((time.time() -self.prevTime) > self.updateTime)):
            if self.counter>10000:
                pass
            else:
                # Flow sensor is a rand integer between 0 and 10
                if (self.simulated):
                    l_min = random.randint(0,10)
                    psi = random.randint(0,100)
                else:
                    print("reading line")
                    l_min, psi = self.readSerialLine()
                
                if not (l_min or psi):
                    print("Restart detected")
                    self.graphEnabled=False

                print(f"Sensor 1: {l_min}, Sensor 2: {psi}")

                self.y = np.append(self.y, l_min)
                self.y = self.y[1:self.win+1]
                self.y2 = np.append(self.y2, psi)
                self.y2 = self.y2[1:self.win+1]
                self.pline.set_ydata(self.y)
                self.pline2.set_ydata(self.y2)
                self.ax[0].relim(); self,self.ax[0].autoscale_view()
                self.ax[1].relim(); self,self.ax[1].autoscale_view()
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                self.bnext = Button(self.axes, 'START',color="#00d93a")
                self.bnext.label.set_fontsize(12)
                self.bnext.on_clicked(self.start_graph)
                plt.pause(0.00001)
        else:
            # Either timer has not passed or state is IDLE
                self.bnext = Button(self.axes, 'START',color="#01d93a")
                self.bnext.label.set_fontsize(12)
                self.bnext.on_clicked(self.start_graph)
                plt.pause(0.00001)
                pass
    
    def readSerialLine(self):
        self.ser.flushInput()
        self.ser.readline()
        line = self.ser.readline().decode('utf-8').rstrip()
        if not line:
            return 0, 0
        print(line)
        lineArray = line.split()
        try:
       	    flow_sensor = float(lineArray[0])
            pressure_sensor = float(lineArray[1])
        except:
            flow_sensor = 0
            pressure_sensor = 0
        return flow_sensor, pressure_sensor
    
    def run(self):
        print("Run start")
        self.prevTime = time.time()
        while(True):
            try:
                self.updateGraph()
                pass
            except KeyboardInterrupt:
                print("")
                print("Dashboard closed")
                break

# start Dashboard 
simulated = False
dark_mode = False
if "simulated" in sys.argv:
    simulated = True
if "dark_mode" in sys.argv:
    dark_mode = True
dashboard = Dashboard(600, 480, simulated=simulated, dark_mode = dark_mode)
plt.show(block=False)
dashboard.run()
