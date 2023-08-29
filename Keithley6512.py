# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 15:25:33 2023

@author: rnn1
"""
# from Instrument import Instrument as _inst 

import pyvisa as visa

class Keithley6512():
    def __init__(self, gpibBoardIndex=-1, gpibAddress=-1, usbAddress=-1,
                 ethernetAddress=-1, alias=-1, echoFlag=True, virtual=False):
                 
        if not virtual:
            self._echo_flag = echoFlag
            if(gpibBoardIndex != -1):
                self._boardIndex = gpibBoardIndex
                self._gpibAddress = gpibAddress
                self._rm = visa.ResourceManager()
                self._inst = self._rm.open_resource('GPIB' + str(self._boardIndex) + '::' + str(self._gpibAddress))
            elif(usbAddress != -1):
                self._rm = visa.ResourceManager()
                self._inst = self._rm.open_resource(usbAddress)
            elif(ethernetAddress != -1):
                self._rm = visa.ResourceManager()
                self._inst = self._rm.open_resource(ethernetAddress)
            elif(alias != -1):
                self._rm = visa.ResourceManager()
                self._inst = self._rm.open_resource(alias)
        
        # self._inst = _inst(gpibBoardIndex=0, gpibAddress=27, usbAddress=-1, ethernetAddress=-1, alias=-1, echoFlag=True, virtual=False)
    # Keithlye 6512 needs an X at the end of every command to execute device dependant commands. Section 3-2 of manual explains
    
    def ReadingMode(self, value):
        # B0 = Electrometer; B1 = Buffer reading; B2 = Maximum Reading; B3 = Minimum reading
        reading = f'B{value}X' 
        return self._inst.write(reading)    
    
    def ZeroCheck(self, value):
        check = f'C{value}X'
        return self._inst.write(check)
    
    def Function(self, value):
        # F0 = Volts; F1 = Amps; F2 = Ohms; F3 = Coulombs; F4 = External Feedback
        function = f'F{value}X'
        return self._inst.write(function)
        
    def DataFormat(self, value):
        # G0 = Reading with prefix; G1 Reading without prefix; G2 = Reading with prefix and buffer suffix
        data = f'G{value}X'
        return self._inst.query(data)
    
    def EOIBus(self, value):
        status = f'K{value}X'
        return self._inst.write(status)
    
    def StoreCalibration(self):
        return self._inst.write('L1X')
    
    def SystemStatus(self, value):
        # M0 = Disable SRQ; M1 = Reading Overflow; M2 = Buffer Full; M8 = Reading Done; M16 = Ready; M32 = Error
        status = f'M{value}X'
        return self._inst.write(status)
    
    def Suppression(self, value):
        status = f'N{value}X'
        return self._inst.write(status)
    
    def DataStore(self, value):
        # Q0 = Conversion rate; Q6 = Triggered; Q7 = Disabled
        data = f'Q{value}X'
        return self._inst.write(data)
    
    def Range(self, value):
        # R0 = Auto; R12 = Cancel auto-ranging for all functions
        span = f'R{value}X'
        return self._inst.write(span)
    
    def Trigger(self, value):
        trigger = f'T{value}X'
        return self._inst.write(trigger)
    
    def Status(self, value):
        # U0 = Send status word; U1 = Send error condition; U2 Send data conditions
        status = f'U{value}X'
        return self._inst.query(status)
    
    def Terminator(self):
        '''
        Y<LF CR> : Terminator = <LF><CR>
        Y<CR LF> : Terminator = <CR><LF>
        Y<ASCII> : Terminator = ASCII character (except A-Z)
        YX       : No Terminator
        
        example: Y\r\nX returns 'NDCA+0.00017E-11\r\n'
                 YX returns 'NDCA-0.00002E-11'
        '''
        return self._inst.write('YX')
        
    def ZeroCorrect(self, value):
        zero = f'Z{value}X'
        return self._inst.write(zero)    
    
    # Uniline Commands
    
    def remote(self):  # Set up for remote operation
        return self._inst.write('RST')
    
    def interface_clear(self): # Clears interface
        return self._inst.write('IFC')
        
    def eoi(self):   # Marks end of transmission
        return self._inst.write('EOI')
    
    def attention(self): # defines bus contents
        return self._inst.write('ATN')
    
    def service(self): # Device requesting service 
        return self._inst.write('SRQ')
    
    # Multiline commands    
    
    def local_Lockout(self):  # Locks out front panel controls
        return self._inst.write('*LLO')
    
    def clear(self): # Returns device to default conditions
        return self._inst.write('DCL')
    
    def poll_enable(self): # Enables serial polling
        return self._inst.write('SPE')
    
    def poll_disable(self):  # Disables serial polling
        return self._inst.write('SPD')
    
    def select_clear(self): # Returns to default conditions (selective device clear)
        return self._inst.write('SDC')
    
    def local(self):   # Cancels remote state
        return self._inst.write('GTL')
    
    def execute(self): # Triggers device for reading (Group Execute Trigger)
        return self._inst.write('GET')
    
    def deaf(self): # Removes all listeners from bus (Unlisten)
        return self._inst.write('UNL')
    
    def mute(self): # Removes talker from bus (Untalk)
        return self._inst.write('UNT')
    
    def supress(self):
        return self._inst.query('N1X')
    
    def no_supress(self):
        return self._inst.query('N0X')
    
        
    