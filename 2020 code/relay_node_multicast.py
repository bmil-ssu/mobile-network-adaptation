from digi.xbee.devices import XBeeDevice
from digi.xbee.util import utils
from random import randint
from xbee import XBee
import serial
import json
import time
import RPi.GPIO as gpio
PORT = "/dev/ttyUSB0"  # port number
BAUD_RATE = 9600 # boundary rate
PL = ["POWER_LEVEL0", "POWER_LEVEL1", "POWER_LEVEL2", "POWER_LEVEL3", "POWER_LEVEL4"] #the list of power level
PM = ["POWER_MODEOFF", "POWER_MODEON"] #the list of power mode
ID_LIST = ["03", "04"] #the list of the names of remote devices
length = 0 #the number of remote deives
device = XBeeDevice(PORT, BAUD_RATE) #select xbee device
ser = serial.Serial(PORT, BAUD_RATE) # set serial of xbee
xbee = XBee(ser, escaped=True) # set xbee device
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD) #by motor driver, connect motor to raspberry-pi(GPIO pin)
gpio.setup(7, gpio.OUT)
gpio.setup(11, gpio.OUT)
gpio.setup(13, gpio.OUT)
gpio.setup(15, gpio.OUT)
gpio.setup(12, gpio.OUT)
gpio.setup(16, gpio.OUT)
gpio.setup(18, gpio.OUT)
gpio.setup(22, gpio.OUT)

gpio.output(7, True)
gpio.output(11, True)
gpio.output(12, True)
gpio.output(16, True)

def stop(): #function that setting motor to teh rc car stop
    gpio.output(13, False)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, False)
    time.sleep(2)


def up(): #function that setting motor to move the rc car to the up
    gpio.output(13, True)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, True)
    time.sleep(2)
    stop()


def down(): #function that setting motor to move the rc car to the down
    gpio.output(13, False)
    gpio.output(15, True)
    gpio.output(18, True)
    gpio.output(22, False)
    time.sleep(2)
    stop()

def leftsteering(): #function to rotate the rc car to the left(90°)
    gpio.output(13, True)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, False)
    time.sleep(2)
    stop()

def rightsteering(): #function to rotate the rc car to the right(90°)
    gpio.output(13, False)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, True)
    time.sleep(2)
    stop()
def clockwise_mobility(): #function for random mobility
    for t in range(0, 10):
        rightsteering()
        up()
        t += 1
ser.close()
device.open() #device should be open to transmit data
while True:
    def data_receive_callback(xbee_message): # when received input(data packet), function works
        print("received packet: ", xbee_message.data.decode())
        response = xbee_message.data.decode() # parameter to represent received data
        received_packet = json.loads(response) # received data packet type str to list
        node_num = "02" # specify the node number
        received_packet[2].append(node_num) #append node_num in history list
        received_packet[3] += 1 #add hop
        print("sending packet: ", received_packet)
        sending_packet = json.dumps(received_packet) #change types list to str

        try:
            xbee_network = device.get_network() #to transmit data, network should be generated
            xbee_network.clear()
            rand_PL = randint(0, 4) #select random number for power level
            device.set_parameter("PL", utils.int_to_bytes(rand_PL)) # set power level
            print(PL[rand_PL])
            rand_PM = randint(0, 1) # select random number for power mode
            device.set_parameter("PM", utils.int_to_bytes(rand_PM)) #set power mode
            print(PM[rand_PM])
            remote_devices = xbee_network.discover_devices(ID_LIST) #set for remote devices
            if len(remote_devices[length:]) == 0: #check the number of remote devices
                print("Could not find the remote device")
            else:
                for i in range(0, 2): #to transmit the data, limit the range of the number of remote devices
                    node_id = remote_devices[i]._node_id #parameter to select remote devices
                    print("Sending data to %s >> %s..." % (node_id, sending_packet))
                    try:
                        time.sleep(5)
                        device.send_data(remote_devices[i], sending_packet) #send the data packet to remote device
                        print("Success")
                    except:
                        print("timeout")
                    i += 1
        except:
            print("failed")
    device.add_data_received_callback(data_receive_callback) # when received input, callback function
    clockwise_mobility() #rc car moves with mobility
    print("Waiting for data...\n")
    input() # to wait for input
