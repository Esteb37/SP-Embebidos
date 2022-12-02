import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import time
import numpy as np

from numpy import pi, cos, sin, convolve
from scipy.fftpack import fft, ifft, fftshift
from scipy.signal import butter, sosfiltfilt

AMP_THRESHOLD = 150
NOISE_THRESHOLD = 15
SAMPLES_FOR_AVERAGE = 3

MIC_1_SR = 1580
MIC_2_SR = 1690


MIC_1_Y = []
MIC_2_Y = []

MIC_1_FREQS = []
MIC_2_FREQS = []

"""
MINY = 100
MAXY = 130
fig_signal = plt.figure()
ax_signal = fig_signal.add_subplot(1, 1, 1)
signal, = ax_signal.plot([], [], 'r')
"""

fig_fft = plt.figure()
ax_fft = fig_fft.add_subplot(1, 1, 1)
signal_fft, = ax_fft.plot([], [], 'r')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("mic")
    print("Subscribed to mic")


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
    topy = max(frequencies)
    ax_fft.set_ylim([0, topy*1.2])
    signal_fft.set_ydata(fftshift(frequencies))
    signal_fft.set_xdata(np.arange(-len(frequencies)//2, len(frequencies)//2))
    ax_fft.set_xlim([-len(frequencies)//2, len(frequencies)//2])
    plt.draw()
    plt.pause(0.01)


def remove_hum(data):
    fft_data = fft(data)
    fft_data[fft_data < THRESHOLD] = 0
    filt_1 = np.ones_like(fft_data)
    filt_1[0:NOISE_THRESHOLD] = 0
    data_filt = ifft(fft_data*filt_1)
    return np.real(data_filt)


def max_freq(frequencies, sampling_rate):
    return int(np.argmax(frequencies)/(1000/sampling_rate))


def is_same_freq(freq_1, freq_2, th=10):
    th = th/100
    low = 1 - th
    high = 1 + th
    return (freq_1*low <= freq_2 <= freq_1*high) or (freq_2*low <= freq_1 <= freq_2*high)


def remove_outliers(data):
    data = np.array(data)
    mean = np.mean(data)
    std = np.std(data)
    return data[np.abs(data - mean) < 2*std]


def get_average(freqs):
    return np.mean(remove_outliers(freqs))


def on_message(client, userdata, msg):
    global MIC_1_Y, MIC_2_Y, MIC_1_FREQS, MIC_2_FREQS

    payload = int.from_bytes(msg.payload, byteorder="little")

    is_mic_1 = payload >> 14 & 1
    finished_flag = payload >> 15 & 1

    y = MIC_1_Y if is_mic_1 else MIC_2_Y
    freqs = MIC_1_FREQS if is_mic_1 else MIC_2_FREQS
    payload &= 0x3FF

    if finished_flag:

        clean_data = remove_hum(y)

        frequencies = get_fft(clean_data)
        # graph_fft(frequencies)
        freq = max_freq(frequencies, MIC_1_SR if is_mic_1 else MIC_2_SR)

        if (freq > 0):
            freqs.append(freq)

        print("Mic {}: ".format("1" if is_mic_1 else "2"), end=" ")

        if len(remove_outliers(freqs)) > SAMPLES_FOR_AVERAGE:
            print("Average frequency: ", get_average(freqs))
            if is_mic_1:
                MIC_1_FREQS = []
            else:
                MIC_2_FREQS = []
        else:
            print(freq)

        if is_mic_1:
            MIC_1_Y = []
        else:
            MIC_2_Y = []

    else:
        y.append(payload)


print("Connecting to MQTT broker")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)


client.loop_forever()
