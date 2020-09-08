PORT = "/dev/cu.usbserial-DN01AX92"  # port number
from digi.xbee.devices import XBeeDevice
from digi.xbee.util import utils
import json
import serial
from xbee import XBee
import time

BAUD_RATE = 9600  # boundary rate
device = XBeeDevice(PORT, BAUD_RATE)  # select xbee device
db = []  # make received real data to list
ser = serial.Serial(PORT, BAUD_RATE)  # set serial of xbee
xbee = XBee(ser, escaped=True)  # set xbee device
pilot = ["01", "08", ["pilot01"], 1, "ACK"]  # list of packet of pilot
pilot2 = json.dumps(pilot)  # packet of pilot to check ack
ack = []  # list of ack to send and receive ack
pack = ["01", "08", ["01"], 1, "Hello XBee!", [0, 1]]  # list of packet of data
packet = json.dumps(pack)  # to change list to string
global neighbor  # parameter to check how many nodes are around by ack
neighbor = 0
ser.close()
device.open()  # device should be close to receive data
print("sending ack...")
device.send_data_broadcast(pilot2)  # send pilot to check neighbors around source node


def data_receive_callback(xbee_message):  # when received input(data packet),function works
    respon = xbee_message.data.decode()  # parameter to represent received data
    response = json.loads(respon)  # received data packet type str to list
    if response[4] == "ACK" and response[3] == 2 and response[2][
        0] == "pilot01":  # conditions to check neighbors by counting acks
        print("ACK is ", xbee_message.data.decode())
        global neighbor
        neighbor += 1
        print("get ack and neighbor + 1")
        print("num of neighbor: ", neighbor)
        if neighbor < 2:  # to prevent repeating sending data, limit the range
            n = open('neigh_history.txt', 'a')  # to record the neighbor history
            n.write(str(neighbor) + "\n")  # insert the space
            n.close()  # close the neigh_history.txt file
            send_time = []  # to make send_time list
            now = time.gmtime(time.time())  # record current time
            send_time.append([now.tm_hour, now.tm_min, now.tm_sec])
            t = open('time_history.txt', 'a')  # open the time_history file and record the time data
            t.write(str(now.tm_hour) + ' ')
            t.write(str(now.tm_min) + ' ')
            t.write(str(now.tm_sec) + "\n")
            t.close()

            print("sending time:", send_time)

            print("Sending packet:", pack)
            packet = json.dumps(pack)
            xbee_network = device.get_network()  # to transmit data, network should be generated
            xbee_network.clear()

            ser.close()

            device.set_parameter("PL", utils.int_to_bytes(0))  # set power level
            device.set_parameter("PM", utils.int_to_bytes(1))  # set power boost mode

            try:

                time.sleep(5)  # timing issue solution
                device.send_data_broadcast(packet)  # send the data using broadcast method
                print("Success")
            except:
                print("timeout")
            neighbor = 0  # initialize # of neighbors


device.add_data_received_callback(data_receive_callback)  # when received input, callback function
print("Waiting for data...\n")
input()  # to wait for input
