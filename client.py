import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import time
import numpy as np

from numpy import pi, cos, sin, convolve
from scipy.fftpack import fft, ifft, fftshift
from scipy.signal import butter, sosfiltfilt

start = time.time()
count = 0
MINY = 100
MAXY = 130

y = []

"""fig_signal = plt.figure()
ax_signal = fig_signal.add_subplot(1, 1, 1)
signal, = ax_signal.plot([], [], 'r')"""

fig_fft = plt.figure()
ax_fft = fig_fft.add_subplot(1, 1, 1)
signal_fft, = ax_fft.plot([], [], 'r')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("mic")
    print("Subscribed to mic")


maxi = 0


pos = 0


def graph_signal(y):
    topy = max([MAXY, max(y)])
    boty = min([MINY, min(y)])
    ax_signal.set_ylim([boty, topy])
    ax_signal.set_xlim([0, len(y)])
    signal.set_ydata(y)
    signal.set_xdata(np.arange(0, len(y)))
    plt.draw()
    plt.pause(0.01)


def get_fft(data):
    hamm = np.hamming(len(data))
    return np.abs(fft(data*hamm))


def graph_fft(frequencies):
    topy = max([MAXY, max(frequencies)])
    ax_fft.set_ylim([0, topy*1.2])
    signal_fft.set_ydata(fftshift(frequencies))
    signal_fft.set_xdata(np.arange(-len(frequencies)//2, len(frequencies)//2))
    ax_fft.set_xlim([-len(frequencies)//2, len(frequencies)//2])
    plt.draw()
    plt.pause(0.01)


def remove_hum(data):
    fft_data = fft(data)
    fft_data[fft_data < 200] = 0
    filt_1 = np.ones_like(fft_data)
    filt_1[0:15] = 0
    data_filt = ifft(fft_data*filt_1)
    return np.real(data_filt)


def max_freq(frequencies):
    return int(np.argmax(frequencies)/(1.75))


def is_same_freq(freq_1, freq_2):
    return (freq_1*0.9 <= freq_2 <= freq_1*1.1) or (freq_2*0.9 <= freq_1 <= freq_2*1.1)


def on_message(client, userdata, msg):
    global y

    payload = int.from_bytes(msg.payload, byteorder="little")

    if payload & 0x8000:
        clean_data = remove_hum(y)
        frequencies = get_fft(clean_data)
        # graph_fft(frequencies)
        freq = max_freq(frequencies)
        print(freq, is_same_freq(freq, 2200))

        y = []

    else:
        y.append(payload)


print("Connecting to MQTT broker")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)


client.loop_forever()
