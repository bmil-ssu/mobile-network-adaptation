from digi.xbee.devices import XBeeDevice
import json
import serial
from xbee import XBee
import numpy as np
import pandas as pd
import openpyxl
PORT = "/dev/cu.usbserial-DN02P9PA"  # port number
BAUD_RATE = 9600  # boundary rate
device = XBeeDevice(PORT, BAUD_RATE)  # select xbee device
ser = serial.Serial(PORT, BAUD_RATE)  # set serial of xbee
xbee = XBee(ser, escaped=True)  # set xbee device
result = np.zeros([8,6]) #to generate the 8x6 matrix
device.set_sync_ops_timeout(30) # to prevent timeout exception, expand time limit
wb = openpyxl.Workbook() # to create a sheet with workbook function
sheet = wb.active #to open the sheet that we made
sheet['A1'] = "source" # to write A1 down as a source
sheet['B1'] = "destination" # to write B1 down as a destination
sheet['C1'] = 'history' # to write C1 down as a history
sheet['D1'] = 'hop' # to write D1 down as a hop
sheet['E1'] = 'data' # to write E1 down as a data
while True:
    device.open()  # device should be closed to receive data
    def data_receive_callback(xbee_message): # when received input(data packet), function works
        print("response is ", xbee_message.data.decode())
        respon = xbee_message.data.decode() # parameter to represent received data
        response = json.loads(respon) # received data packet type str to list
        response[2] = json.dumps(response[2]) # to change the data form of a list to a string
        #history = json.dumps(response[2])
        sheet.append(response) #add a new row after the last row where data exists on the sheet
        wb.save("text.xlsx") # save the sheet under the name "text.xlsx"
    device.add_data_received_callback(data_receive_callback) # when received input, callback function

    print("Waiting for data...\n")
    input() # to wait for input

