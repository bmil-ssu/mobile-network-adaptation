from digi.xbee.devices import XBeeDevice
from digi.xbee.util import utils
import json
import serial
from xbee import XBee
import time
from threading import Timer

# import RPi.GPIO as gpio
PORT = "/dev/ttyUSB0"  # port number
BAUD_RATE = 9600  # boundary rate
device = XBeeDevice(PORT, BAUD_RATE)  # select xbee device
db = []  # make received real data to list
ser = serial.Serial(PORT, BAUD_RATE)  # set serial of xbee
xbee = XBee(ser, escaped=True)  # set xbee device
pilot = ["01", "09", ["pilot05"], 1, "ACK"]  # packet of pilot to check ack
ack = []  # list of ack to send and receive ack
global neighbor
neighbor = 0  #parameter to check how many nodes are around by ack
device.open() #device should be closed to receive data
device.set_sync_ops_timeout(30) #to prevent timeout exception, expand time limit
while True:
   def data_receive_callback(xbee_message): #when received input(data packet),function works
       print("respon is ", xbee_message.data.decode())
       respon = xbee_message.data.decode()#parameter to represent received data

       response = json.loads(respon)#received data packet type str to list
       if response[4] == "ACK" and response[3] < 2:#when received pilot packet

           print("sending ack...")
           response[2].append("05") #record xbee number
           response[3] = 2 # the number of hop
           time.sleep(1) #timing issue solution
           device.send_data_broadcast(json.dumps(response))#send pilot to check neighbors around relay node
           print("sending ack success")
       elif response[4] == "ACK" and response[3] == 2 and response[2][0] == "pilot05":#conditions to check neighbors by counting acks
           global neighbor
           neighbor += 1
           print("get ack and neighbor + 1")
       elif response[4] == "Hello XBee!":#when received data packet
           print("received packet and sending pilot...")
           device.send_data_broadcast(json.dumps(pilot))#send the data using broadcast method

           time.sleep(5)#timing issue solution
           print ("num of neighbor: ", neighbor)
           print("Received packet: ", response)
           response[2].append("05")  # insert its node number to history of packet
           hop = response[3] #checking # of hop
           response[3] += 1  # increase hop of packet
           print("Sending packet: ", response)
           sending_packet = json.dumps(response)  # to send the data change the data form of a list to a string
           if hop < 5: #to prevent repeating receive same data, limit the range of # of hop
               try:
                   xbee_network = device.get_network()  # set network
                   xbee_network.clear()
                   device.set_parameter("PL", utils.int_to_bytes(0))  # set power level
                   device.set_parameter("PM", utils.int_to_bytes(0))  # set power mode
                   # region()
                   try:
                       device.send_data_broadcast(
                           sending_packet)  # transmit data by broadcasting to the other nodes around
                       print("sending packet Success")  # if transmitting is success, then print "Success"
                       neighbor = 0
                   except:
                       print(
                           "timeout")  # if transmitting is failed or there is no other node around, then print "timeout"

               except:
                   print("failed")
           else:
               print("hop is over")


   device.add_data_received_callback(data_receive_callback) #when received input, callback function

   print("Waiting for data...\n")
   input() #to wait for input
