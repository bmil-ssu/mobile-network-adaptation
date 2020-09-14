from digi.xbee.devices import XBeeDevice
from digi.xbee.util import utils
import json
import serial
from xbee import XBee
import time
import RPi.GPIO as gpio
import math
import random
import numpy as np

PORT = "/dev/ttyUSB0"  # port number
BAUD_RATE = 9600  # boundary rate
device = XBeeDevice(PORT, BAUD_RATE)  # select xbee device
db = []  # make received real data to list
ser = serial.Serial(PORT, BAUD_RATE)  # set serial of xbee
xbee = XBee(ser, escaped=True)  # set xbee device
pilot = ["01", "08", ["pilot03"], 1, "ACK"]  # packet of pilot to check ack
pilot2 = json.dumps(pilot) # change the type of packet of pilot list to string
global cur_loc # variable to define current location of rc-car
cur_loc = [0, 0]
gpio.setwarnings(False) # set raspberry-pi's GPIO pin
gpio.setmode(gpio.BOARD)  # control rc-car's motor by raspberry-pi's GPIO pin
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

velocity = 0.8 # parameter represnting the speed of rc-car
moving_t = 2 # parameter representing the range of rc-car's once movement
static_d = velocity * moving_t # parameter representing the rc-car's movement in a straight line
moving_d = round(static_d / math.sqrt(2), 2) # parmeter representing the rc-car's diagonal movement

P = ["0", "45", "90", "135", "180", "225", "270", "315", "stop"]  # path list of moving rc car on clockwise
L = [[-static_d, 0], [-moving_d, moving_d], [0, static_d], [moving_d, moving_d], [static_d, 0], [moving_d, -moving_d],
     [0, -static_d], [-moving_d, -moving_d], [0, 0]] # list of rc-car's moving direction
num_move = len(P) # parmeter to designate the movement of rc-car
idx_move = np.arange(0, num_move) # set the array of the movement of rc-car
idx_move = idx_move.tolist() # change the type of idx_move array to list
block_size = 7 # parameter representing the length the rc-car moved

def stop():  # function that setting motor to teh rc car stop
    gpio.output(13, False)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, False)
    time.sleep(2)


def up():  # function that setting motor to move the rc car to the up
    gpio.output(13, True)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, True)
    time.sleep(2)
    stop()


def down():  # function that setting motor to move the rc car to the down
    gpio.output(13, False)
    gpio.output(15, True)
    gpio.output(18, True)
    gpio.output(22, False)
    time.sleep(2)
    stop()


def leftsteering():  # function to rotate the rc car to the left(90°)
    gpio.output(13, True)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, False)
    time.sleep(2)
    stop()


def half_leftsteering():  # function to rotate the rc car to the left(45°)
    gpio.output(13, True)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, False)
    time.sleep(0.5)
    stop()


def rightsteering():  # function to rotate the rc car to the right(90°)
    gpio.output(13, False)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, True)
    time.sleep(2)
    stop()


def half_rightsteering():  # function to rotate the rc car to the right(45°)
    gpio.output(13, False)
    gpio.output(15, False)
    gpio.output(18, False)
    gpio.output(22, True)
    time.sleep(0.5)
    stop()


def limit_coordinate(cur_loc, next_loc, move_idx): #the function to limit the rc car's moving on boundary
    if next_loc[0] < 0:
        del idx_move[move_idx] # delete the movement across boundary
        m = idx_move # set the list of the movement of rc-car without deleted movement
        print("left limit")

    elif next_loc[0] > block_size - 1:
        del idx_move[move_idx]
        m = idx_move
        print("right limit")

    elif next_loc[1] < 0:
        del idx_move[move_idx]
        m = idx_move
        print("upward limit")

    elif next_loc[1] > block_size - 1:
        del idx_move[move_idx]
        m = idx_move
        print("downward limit")

    else:
        return move_idx, next_loc

    loc_idx = random.randint(0, len(m) - 1) # select the movement of rc-car without passing over the boundary
    print("rechoiced move_idx: ", m[loc_idx])
    next_loc = [cur_loc[i] + L[m[loc_idx]][i] for i in range(len(cur_loc))] # set next location of rc-car
    print("rechoiced next_loc: ", next_loc)
    return limit_coordinate(cur_loc, next_loc, loc_idx)


def region(cur_loc):  # function to designate list of path, and make rc car move on received input
    rand_num = random.randint(0, 8) # select random number for rc-car's movement
    next_loc = [cur_loc[i] + L[rand_num][i] for i in range(len(cur_loc))] #set next location of rc-car
    print("next location checking...", next_loc)
    path_idx, next_loc = limit_coordinate(cur_loc, next_loc, rand_num) #check that rc-car does not cross the boundary
    print("move to ", next_loc)
    path = P[int(path_idx)] #select the rc-car's moving

    if path == "0":
        for i in range(moving_t):
            up()
            i += 1
        print("xbee moved forward")

    elif path == "45":
        half_rightsteering()
        for i in range(moving_t):
            up()
            i += 1
        half_leftsteering()
        print("xbee moved 45 clockwise")

    elif path == "90":
        rightsteering()
        for i in range(moving_t):
            up()
            i += 1
        leftsteering()
        print("xbee moved right")

    elif path == "135":
        rightsteering()
        half_rightsteering()
        for i in range(moving_t):
            up()
            i += 1
        leftsteering()
        half_leftsteering()
        print("xbee moved 135 clockwise")

    elif path == "180":
        for i in range(moving_t):
            down()
            i += 1
        print("xbee moved backward")

    elif path == "225":
        leftsteering()
        half_leftsteering()
        for i in range(moving_t):
            up()
            i += 1
        rightsteering()
        half_rightsteering()
        print("xbee moved 225 clockwise")

    elif path == "270":
        leftsteering()
        for i in range(moving_t):
            up()
            i += 1
        rightsteering()
        print("xbee moved left")

    elif path == "315":
        half_leftsteering()
        for i in range(moving_t):
            up()
            i += 1
        half_rightsteering()
        print("xbee moved 315 clockwise")

    elif path == "stop":
        stop()
        print("xbee stopped")

    return next_loc, path

ack = []  # list of ack to send and receive ack
global neighbor
neighbor = 0  # parameter to check the number of neighboring nodes by ack
device.open() # to send data, device should be opened
while True:
    def data_receive_callback(xbee_message): # function that receiving and transmitting data
        global cur_loc
        print("respon is", xbee_message.data.decode())
        respon = xbee_message.data.decode() # parameter representing received data
        response = json.loads(respon) # change the type of received data string to list
        if response[4] == "ACK" and response[3] < 2: # condition to check the received ack
            print("sending ack...")
            response[2].append("03") # record the device's number in the received data
            response[3] = 2 # change the number of hop in the received data
            time.sleep(2) # solution for timing issue
            device.send_data_broadcast(json.dumps(response)) # send received pilot by broadcast method

        elif response[4] == "ACK" and response[3] == 2 and response[2][0] == "pilot03": # condition to check the received data that this device transmitted
            global neighbor
            neighbor += 1 # increase the number of neighboring nodes by checking ack
            print("get ack and neighbor + 1")

        elif response[4] == "Hello XBee!": # condition to check the received data is pilot data or real data
            datapacket = response # parameter that set the received real data
            print("received packet and sending pilot...")
            device.send_data_broadcast(pilot2) # send pilot to check the number of neighboring nodes
            time.sleep(2) # solution for timing issue
            print("num of neighbor: ", neighbor)
            print("Received packet: ", datapacket)
            datapacket[2].append("03") # record the device's own number in the received data's history
            hop = datapacket[3]
            datapacket[3] += 1 # change the number of hop in the received data
            print("Sending datapacket: ", datapacket)
            sending_packet = json.dumps(datapacket) # to send the data, change the type of the data list to string

            if hop < 7: # to prevent repeating receive same data, limit the range of the number of hop
                xbee_network = device.get_network()  # to transmit data, network should be formed
                xbee_network.clear()

                rand_PL = random.randint(0, 4) # select random number for power level
                rand_PM = random.randint(0, 1) # select random number for power mode

                device.set_parameter("PL", utils.int_to_bytes(rand_PL))  # set power level
                device.set_parameter("PM", utils.int_to_bytes(rand_PM))  # set power mode

                next_loc, path = region(cur_loc) #move the rc-car to selected locastion
                cur_loc = next_loc # set current location of rc-car
                try:
                    device.send_data_broadcast(sending_packet)  # transmit data by broadcasting to the other nodes around
                    print("Success")  # if transmitting is success, then print "Success"
                    neighbor = 0
                except:
                    print("timeout")  # if transmitting is failed or there is no other node around, then print "timeout"



    device.add_data_received_callback(data_receive_callback) # when received input, callback function
    print("Waiting for data...\n")
    input() # wait for input