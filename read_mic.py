# Raspberry pi program for reading serial input and sending it to client via mqtt
import serial
import paho.mqtt.client as mqtt
import time
from scipy.signal import butter, sosfiltfilt
from scipy.fftpack import fft, ifft, fftshift
from numpy import pi, cos, sin, convolve
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import time
import numpy as np


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def graph_signal(y):
    topy = max([MAXY, max(y)])
    boty = min([MINY, min(y)])
    ax_signal.set_ylim([boty, topy])
    ax_signal.set_xlim([0, len(y)])
    signal.set_ydata(y)
    signal.set_xdata(np.arange(0, len(y)))
    plt.draw()
    plt.pause(0.01)


signal = []

# Serial port


# MQTT
client = mqtt.Client()

client.on_connect = on_connect


print("Connecting...")
client.connect("localhost", 1883, 60)
client.loop()

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    timeout=1
)


def millis(): return int(round(time.time() * 1000))


start = millis()

count = 0

while True:

    # Read serial input
    data = ser.readline()

    if (data is not None):
        ellapsed = millis() - start
        if ellapsed > 1000:
            graph_signal(signal)
            client.publish("RASP", (0x8000 | ellapsed))
            start = millis()

        else:
            signal.append(int(data))
            client.publish("RASP", data)

        count += 1

    client.loop()
