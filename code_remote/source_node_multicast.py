def coordinator():
    from digi.xbee.devices import XBeeDevice
    from digi.xbee.util import utils
    from random import randint
    import json
    PORT = "/dev/cu.usbserial-DN02P6WL" #port number
    BAUD_RATE = 9600 #boundary rate
    PL = ["POWER_LEVEL0", "POWER_LEVEL1", "POWER_LEVEL2", "POWER_LEVEL3", "POWER_LEVEL4"] #the list of power level
    PM = ["POWER_MODEOFF", "POWER_MODEON"] #the list of power mode
    ID_LIST = ["01","02"] #the list of the names of remote devices
    length = 0 #the number of remote deives
    device = XBeeDevice(PORT, BAUD_RATE) #select xbee device
    his = ["00"] #to record the list of xbee number that comes through
    hop = 1 #the number of hop
    pack = ["00", "07", his, hop, "Hello Xbee!"] #data packet
    packet = json.dumps(pack) #to change the type of packet list to string
    try:
        xbee_network = device.get_network() #to transmit data, network should be generated
        xbee_network.clear()
        device.open() #device should be open to transmit data

        rand_PL = randint(0, 4) #select random number for power level
        device.set_parameter("PL", utils.int_to_bytes(rand_PL))  # set power level
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
                print("Sending data to %s >> %s..." % (node_id, packet))
                try:
                    device.send_data(remote_devices[i], packet) #send the data packet to remote device
                    print("Success")
                except:
                    print("timeout")
            #else:
             #   node_id = ID_LIST[i] #parameter to specify devices that is not remote
               # print(node_id + " doesn't exist in tx range")
    finally:
        if device is not None and device.is_open(): #device should be closed, end of code
            device.close()

coordinator()
