import serial.tools.list_ports
import json
import time
import paho.mqtt.client as mqttclient
from simple_ai import *
print("IoT Gateway")

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""
state = 1

# TODO: Add your token and your comport
# Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "nUEkJhzBZNXr3Vk4UmZ2"
bbc_port = "COM3"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    # TODO: Add your source code to publish data to the server
    collect_data = {splitData[1]: splitData[2]}
    if splitData[1] == "ACK":
        state = 1
    else:
        client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)


def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]
        ser.write((str(4) + "#").encode())    


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = 0
    # TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLED'] = jsonobj['params']
            client.publish('v1/devices/me/attributes',
                           json.dumps(temp_data), 1)
            print(jsonobj['params'])
            cmd = 1 if jsonobj['params'] == True else 0
        if jsonobj['method'] == "setFAN":
            temp_data['valueFAN'] = jsonobj['params']
            client.publish('v1/devices/me/attributes',
                           json.dumps(temp_data), 1)
            cmd = 3 if jsonobj['params'] == True else 2
    except:
        pass

    if len(bbc_port) > 0 and state == 1:
        ser.write((str(cmd) + "#").encode())
        state = 2


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


def detect(result):
    mes = True if result == 0 else False
    client.publish('v1/devices/me/attributes',
                           json.dumps({"valueH": mes}), 1)
    print(json.dumps({"valueH": mes}))


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message


while True:

    if len(bbc_port) > 0:
        readSerial()
    capture_image()
    detect(ai_detection())
    time.sleep(1)
