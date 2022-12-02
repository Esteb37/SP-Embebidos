# Raspberry pi program for reading serial input and sending it to client via mqtt
import serial
import paho.mqtt.client as mqtt
import time


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


# Serial port


# MQTT
client = mqtt.Client()

client.on_connect = on_connect


print("Connecting...")
client.connect("localhost", 1883, 60)
client.loop()

start = time.time()

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
)

while True:

    # Read serial input
    data = ser.readline()

    if(data is not None):
        if time.time() - start > 1:
            start = time.time()
            client.publish("RASP", 0b1000000000000000)
        else:
            client.publish("RASP", data)

    client.loop()
