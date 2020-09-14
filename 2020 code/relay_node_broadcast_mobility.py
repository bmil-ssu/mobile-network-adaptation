# tx power minimum

# !/usr/bin/env python
# coding: utf-8

# 1. 2번씩 반복 2. DEVICE number
#
# moving & traking (check)
# using Q-matrix (-)

# In[1]:


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
PL = ["POWER_LEVEL0", "POWER_LEVEL1", "POWER_LEVEL2"]  # list of power level
PM = ["POWER_MODEOFF", "POWER_MODEON"]  # list of power mode
device = XBeeDevice(PORT, BAUD_RATE)  # select xbee device
db = []  # make received real data to list
ser = serial.Serial(PORT, BAUD_RATE)  # set serial of xbee
xbee = XBee(ser, escaped=True)  # set xbee device
pilot = ["01", "08", ["pilot03"], 1, "ACK"]  # packet of pilot to check ack
pilot2 = json.dumps(pilot)
global cur_loc
cur_loc = [0, 0]
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)  # by motor driver, connect motor to raspberry-pi(GPIO pin)
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

velocity = 0.8
moving_t = 2
static_d = velocity * moving_t
moving_d = round(static_d / math.sqrt(2), 2)

P = ["0", "45", "90", "135", "180", "225", "270", "315", "stop"]  # path list of moving rc car on clockwise
L = [[-static_d, 0], [-moving_d, moving_d], [0, static_d], [moving_d, moving_d], [static_d, 0], [moving_d, -moving_d],
     [0, -static_d], [-moving_d, -moving_d], [0, 0]]
num_move = len(P)
idx_move = np.arange(0, num_move)
idx_move = idx_move.tolist()
block_size = 7


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


def limit_coordinate(cur_loc, next_loc, move_idx):
    if next_loc[0] < 0:
        del idx_move[move_idx]
        m = idx_move
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

    loc_idx = random.randint(0, len(m) - 1)
    print("rechoiced move_idx: ", m[loc_idx])
    next_loc = [cur_loc[i] + L[m[loc_idx]][i] for i in range(len(cur_loc))]
    print("rechoiced next_loc: ", next_loc)
    return limit_coordinate(cur_loc, next_loc, loc_idx)


def region(cur_loc):  # function to designate list of path, and make rc car move on received input
    # pathnum = input("Please enter the path number: ")
    # intpathnum = int(pathnum)
    # path = P[intpathnum]
    rand_num = random.randint(0, 8)  # random direction moving
    next_loc = [cur_loc[i] + L[rand_num][i] for i in range(len(cur_loc))]
    print("next location checking...", next_loc)
    path_idx, next_loc = limit_coordinate(cur_loc, next_loc, rand_num)
    print("move to ", next_loc)
    path = P[int(path_idx)]

    print("path")

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


def rargmax(state_action):
    max_index_list = []
    max_value = state_action[0]
    for index, value in enumerate(state_action):
        if value > max_value:
            max_index_list.clear()
            max_value = value
            max_index_list.append(index)
        elif value == max_value:
            max_index_list.append(index)
    return max(max_index_list)


Q = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
     [2, 3, 4, 5, 6, 7, 8, 9, 1, 0],
     [3, 4, 5, 6, 7, 8, 9, 0, 1, 2],
     [4, 5, 6, 7, 8, 9, 0, 1, 2, 3],
     [5, 6, 7, 8, 9, 0, 1, 2, 3, 4],
     [6, 7, 8, 9, 0, 1, 2, 3, 4, 5],
     [7, 8, 9, 0, 1, 2, 3, 4, 5, 6],
     [8, 9, 0, 1, 2, 3, 4, 5, 6, 7],
     ]

T = [[0, 0], [0, 1], [1, 0], [2, 0], [1, 1]]

tx_range = [0, 9.23, 15.9, 19.2, 21.7, 24.9]
action_space = []

for i in range(len(tx_range)):
    for j in range(len(tx_range)):
        action_space.append(tx_range[i] - tx_range[j])
action_space.sort()
for i in range(len(tx_range) - 1):
    action_space.remove(0)
    i += 1

action_space = np.array(action_space)
print("action_space", action_space)
cur_txr = 0

ack = []  # list of ack to send and receive ack
global neighbor
neighbor = 0  # parameter to check how many nodes are around by ack
device.open()
while True:
    def data_receive_callback(xbee_message):
        l = open('/home/pi/loc_history.txt', 'a')
        m = open('/home/pi/move_history.txt', 'a')
        tx = open('/home/pi/tx_history.txt', 'a')
        n = open('/home/pi/neigh_history.txt', 'a')
        tx_range = [0, 9.23, 15.9, 19.2, 21.7, 24.9]
        # tx_range = np.array([0, 9.23, 15.9, 19.2, 21.7, 24.9])
        cur_txr = 0
        global cur_loc
        print("respon is", xbee_message.data.decode())
        respon = xbee_message.data.decode()
        response = json.loads(respon)
        if response[4] == "ACK" and response[3] < 2:
            print("sending ack...")
            response[2].append("03")
            response[3] = 2
            time.sleep(2)
            device.send_data_broadcast(json.dumps(response))

        elif response[4] == "ACK" and response[3] == 2 and response[2][0] == "pilot03":
            global neighbor
            neighbor += 1
            print("get ack and neighbor + 1")

        elif response[4] == "Hello XBee!":
            datapacket = response
            print("received packet and sending pilot...")
            # time.sleep(1)
            device.send_data_broadcast(pilot2)
            time.sleep(2)
            print("num of neighbor: ", neighbor)
            print("Received packet: ", datapacket)
            datapacket[2].append("03")
            hop = datapacket[3]
            datapacket[3] += 1
            print("Sending datapacket: ", datapacket)
            sending_packet = json.dumps(datapacket)

            if hop < 7:
                try:
                    xbee_network = device.get_network()  # set network
                    xbee_network.clear()

                    ############################################

                    # Q table 읽고 power level 정해야
                    # neighbor 값을 읽어서 max 인 level number 추출해야
                    state_action = Q[neighbor]
                    action_idx = rargmax(state_action)
                    next_txr = cur_txr + action_space[action_idx]
                    if next_txr < 0:
                        next_txr = 0
                    elif next_txr > 24.9:
                        next_txr = 24.9

                    print("tx range ", next_txr)
                    # next_txr_idx = np.where(tx_range == next_txr)
                    next_txr_idx = tx_range.index(next_txr)
                    print(next_txr_idx)
                    PL_idx = T[next_txr_idx][0]
                    PM_idx = T[next_txr_idx][1]
                    print("PL_idx", PL_idx)

                    # PL_rand_num = random.randint(0, 2)
                    # PM_rand_num = random.randint(0, 1)

                    device.set_parameter("PL", utils.int_to_bytes(PL_idx))  # set power level
                    device.set_parameter("PM", utils.int_to_bytes(PM_idx))  # set power mode

                    tx_range = [PL_idx, PM_idx]
                    tx.write(str(next_txr))
                    tx.write('\n')
                    tx.close()
                    cur_txr = next_txr
                    print("tx range ", tx_range)

                    ############################################
                    next_loc, path = region(cur_loc)
                    m.write(path)
                    m.write('\n')
                    m.close()
                    l.write(str(next_loc))
                    l.write('\n')
                    l.close()
                    n.write(str(neighbor))
                    n.write('\n')
                    n.close()
                    cur_loc = next_loc
                    try:
                        device.send_data_broadcast(
                            sending_packet)  # transmit data by broadcasting to the other nodes around
                        print("Success")  # if transmitting is success, then print "Success"
                        neighbor = 0
                    except:
                        print(
                            "timeout")  # if transmitting is failed or there is no other node around, then print "timeout"

                except:
                    l.close()
                    m.close()
                    tx.close()
                    n.close()


    device.add_data_received_callback(data_receive_callback)
    print("Waiting for data...\n")
    input()




