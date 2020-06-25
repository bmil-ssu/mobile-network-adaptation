from digi.xbee.models.status import PowerLevel
from digi.xbee.devices import XBeeDevice
import numpy as np
import pandas as pd

PORT = "COM17" # port number
BAUD_RATE = 9600
DATA_TO_SEND = "Hello XBee!"
POWER_LEVEL0 = PowerLevel.LEVEL_LOWEST #the lowest power level
POWER_LEVEL1 = PowerLevel.LEVEL_LOW
POWER_LEVEL2 = PowerLevel.LEVEL_MEDIUM
POWER_LEVEL3 = PowerLevel.LEVEL_HIGH
POWER_LEVEL4 = PowerLevel.LEVEL_HIGHEST #the highest power level
POWER = [POWER_LEVEL0,POWER_LEVEL1,POWER_LEVEL2,POWER_LEVEL3,POWER_LEVEL4]

ID_LIST = ["miseon2","mk2","seraeE","mk1","seraeC"]
#the list of the names of receivers
result = np.zeros([5,5])
length = 0
device = XBeeDevice(PORT, BAUD_RATE)

for p in range(99,-1,-1):
    # repeat for 100 times
    print(" +----------------------------------------+")
    print(" | XBee Python Library Send Data Sample "+str(p+1)+" |")
    print(" +----------------------------------------+\n")

    try:
        device.open()
        xbee_network = device.get_network()
        xbee_network.clear()
        
        for d in range(5):
            # send data with each power level
            xbee_network._XBeeNetwork__last_search_dev_list = []
            device.set_power_level(POWER[d]) # set power level to power[d]
            print(device.get_power_level())
    
            # Obtain the remote XBee device from the XBee network.
            remote_devices = xbee_network.discover_devices(ID_LIST)
        
            if len(remote_devices[length:]) == 0:
                print("Could not find the remote device")
            else:
                for i in range(length,len(remote_devices)):
                    node_id = remote_devices[i]._node_id
                    if(node_id == ID_LIST[0]):
                        j = 0
                    elif(node_id == ID_LIST[1]):
                        j = 1
                    elif(node_id == ID_LIST[2]):
                        j = 2
                    elif(node_id == ID_LIST[3]):
                        j = 3
                    elif(node_id == ID_LIST[4]):
                        j = 4
                    print("Sending data to %s >> %s..." % (node_id, DATA_TO_SEND))
                    try:
                        device.send_data(remote_devices[i], DATA_TO_SEND)
                        result[d,j] = result[d,j]+1
                        print("Success")
                    except :
                        print("timeout")
    
                    #length = len(remote_devices)
        if(p%10 == 0 ):
            df = pd.DataFrame({'mk2(110)': result[:, 0],'miseon2(210)' : result[:, 1],
                               'seraeE(270)': result[:, 2],'mk1(320)': result[:, 3],
                               'seraeC(400)': result[:, 4]})
            df.to_csv("real_data"+str(100-p)+".csv",mode='w')

    finally:
        if device is not None and device.is_open():
            device.close()

result = result.astype('int')
df = pd.DataFrame({'miseon2(110)': result[:, 0], 'mk2(210)': result[:, 1],
                   'seraeE(270)': result[:, 2],'mk1(320)': result[:, 3],
                   'seraeC(400)': result[:, 4]})
df.to_csv("real_data_final"+".csv",mode='w')
print(df)

