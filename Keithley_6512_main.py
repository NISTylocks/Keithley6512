# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 15:17:48 2023

@author: rnn1
"""
__author__ = 'NISTylocks'

import sys
import pyvisa

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDialog, QMessageBox, QPushButton, QTextEdit, QGridLayout, QFileDialog, QGraphicsTextItem


import Keithley_GUI as GUI
from Keithley6512 import Keithley6512 as keithley
from Instrument import Instrument as _inst

# TODO : Find the hang up for the gui (wont close properly)

class Electrometer6512(QMainWindow, GUI.Ui_MainWindow):
    def __init__(self, parent = None):
        super(Electrometer6512, self).__init__(parent)
        self.setupUi(self)
        self.keithley = keithley(gpibBoardIndex=0, gpibAddress=27, usbAddress=-1, ethernetAddress=-1, alias=-1, echoFlag=True, virtual=False)
        self.settings = Settings6512()
        self.getsettings()
        self.rangedisplay()
        self.timer = QtCore.QTimer()
        self.timer.start(500)
        self.timer.timeout.connect(self.update)
        # self.pushButton_14.clicked.connect(self.update)
        # self.pushButton_15.clicked.connect(self.Stop)
        self.VOLTS.clicked.connect(self.volts)
        self.AMPS.clicked.connect(self.amps)
        self.OHMS.clicked.connect(self.ohms)
        self.COULOMBS.clicked.connect(self.coulombs)
        self.range_up.clicked.connect(self.rangeup)
        self.range_down.clicked.connect(self.rangedown)
        self.auto_range.clicked.connect(self.autorange)
        self.zero_check.clicked.connect(self.zerocheck)
        self.zero_correct.clicked.connect(self.zerocorrect)
        self.Suppress.clicked.connect(self.suppress)
        self.Trigger.currentIndexChanged.connect(self.trigger)
        # self.pushButton_15.clicked.connect(self.Stop)
        
    def getsettings(self):
        # Get the current settings on the Keithley 6512 Electrometer
        status = self.keithley.Status('0')
        # Store the status in function holders
        self.model = status[:4]
        self.settings.functionval = int(status[4])
        self.settings.rangeval = int(status[5:7])
        self.settings.zerocheck = int(status[7])
        self.settings.zerocorrect = int(status[8])
        self.settings.suppress = int(status[9])
        self.settings.trigger = int(status[10])
        # status[11] Always 0
        self.settings.readMode = int(status[12])
        self.settings.dataprefix = int(status[13])
        # status[14] Always 0
        self.settings.datastore = int(status[15])
        self.settings.SRQ = int(status[16:18])
        self.settings.EOI = int(status[18])
        self.settings.terminator = status[19:21]
        
        # removing the termiantors at end of data line 
        self.keithley.Terminator()
        
        # Set the GUI to match the current settings
        if self.settings.zerocheck == 1:
            self.zerocheck_radio.setChecked(True)
        if self.settings.zerocorrect == 1:
            self.zerocorrect_radio.setChecked(True)
        if self.settings.suppress == 1:
            self.suppress_radio.setChecked(True)
        self.Trigger.setCurrentIndex(self.settings.trigger)
    
    def trigger(self):
        self.settings.trigger = int(self.Trigger.currentIndex())
        self.keithley.Trigger(str(self.settings.trigger))
        if (self.settings.trigger %2) == 0:
            self.trigger_radio.setChecked(False)
        else:
            self.trigger_radio.setChecked(True)
    
    def zerocheck(self):
        value = self.settings.zerocheck
        if value == 0:
            self.settings.zerocheck = 1
            self.keithley.ZeroCheck(str(self.settings.zerocheck))
            self.zerocheck_radio.setChecked(True)
        else:
            self.settings.zerocheck = 0
            self.keithley.ZeroCheck(str(self.settings.zerocheck))
            self.zerocheck_radio.setChecked(False)
            
    def zerocorrect(self):
        value = self.settings.zerocorrect
        if value == 0:
            self.settings.zerocorrect = 1
            self.keithley.ZeroCorrect(str(self.settings.zerocorrect))
            self.zerocorrect_radio.setChecked(True)
        else:
            self.settings.zerocorrect = 0
            self.keithley.ZeroCorrect(str(self.settings.zerocorrect))
            self.zerocorrect_radio.setChecked(False)
            
    def suppress(self):
        value = self.settings.suppress
        if value == 0:
            self.suppress_radio.nextCheckState()
            self.settings.suppress = 1
            self.keithley.Suppression(str(self.settings.suppress))
            
        else:
            self.suppress_radio.nextCheckState()
            self.settings.suppress = 0
            self.keithley.Suppression(str(self.settings.suppress))
            
    def autorange(self):
        self.settings.rangeval = 0
        self.autorange_radio.setChecked(True)
        self.keithley.Range(str(self.settings.rangeval))
        self.rangedisplay()
            
    def rangeup(self):
        self.autorange_radio.setChecked(False) 
        value = self.settings.rangeval
        value += 1
        if value < 12:
            self.keithley.Range(str(value))
            self.settings.rangeval = value
            self.rangedisplay()
    
    def rangedown(self):
        self.autorange_radio.setChecked(False) 
        value = self.settings.rangeval
        value -=1
        if value < 0:
            value = 1
        if value > 0:
            self.keithley.Range(str(value))
            self.settings.rangeval = value
            self.rangedisplay()
            
    def rangedisplay(self):
        self.range_label.setText(self.settings.span[self.settings.rangeval][self.settings.functionval])
        
    def volts(self):
        self.settings.functionval = 0
        self.keithley.Function(str(self.settings.functionval))
        self.rangedisplay()
        
    def amps(self):
        self.settings.functionval = 1
        self.keithley.Function(str(self.settings.functionval))
        self.rangedisplay()
        
    def ohms(self):
        self.settings.functionval = 2
        self.keithley.Function(str(self.settings.functionval))
        self.rangedisplay()
        
    def coulombs(self):
        self.settings.functionval = 3
        self.keithley.Function(str(self.settings.functionval))
        self.rangedisplay()
        
    def external(self):
        self.settings.functionval = 4
        self.keithley.Function(str(self.settings.functionval))
        self.rangedisplay()
        
    def update(self):
        self.LCD.display('{:.2E}'.format(float(self.keithley.DataFormat('1'))))
    
    def Stop(self):
        sys.exit()
        
class Settings6512:
    def __init__(self):
        self.functionval = 0
        self.rangeval = 0
        self.zerocheck = 0
        self.zerocorrect = 0
        self.suppress = 0
        self.trigger = 0
        self.readmode = 0
        self.dataprefix = 0
        self.datastore = 0
        self.srq = 0
        self.eoi = 0
        self.terminator = 0
             # Volts, Amps, Ohms, Coul., External Feedback
        self.span = {
            0: ['Auto V', 'Auto A', 'Auto Ohm',   'Auto C', 'Auto V'],
            1: ['200mV',  '2pA',    '2K Ohm',     '200pC',  '200mV'],
            2: ['2V',     '20pA',   '20K Ohm',    '2nC',    '2V'],
            3: ['20V',    '200pA',  '200K Ohm',   '20nC',   '20V'],
            4: ['200V',   '2nA',    '2M Ohm',     '20nC',   '20V'],
            5: ['200V',   '20nA',   '20M Ohm',    '20nC',   '20V'],
            6: ['200V',   '200nA',  '200M Ohm',   '20nC',   '20V'],
            7: ['200V',   '2uA',    '2G Ohm',     '20nC',   '20V'],
            8: ['200V',   '20uA',   '20G Ohm',    '20nC',   '20V'],
            9: ['200V',   '200uA',  '200G Ohm',   '20nC',   '20V'],
            10:['200V',   '2mA',    '200G Ohm',   '20nC',   '20V'],
            11:['200V',   '20mA',   '200G Ohm',   '20nC',   '20V']
                }
        self.funciton = {
            0: 'VOLTS',
            1: 'AMPS',
            2: 'OHMS',
            3: 'COULOMBS',
            4: 'EXTERNAL'
            }

def main():
    app = QtWidgets.QApplication(sys.argv)
    meter = Electrometer6512()
    meter.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    
    