from scipy.signal import butter, sosfiltfilt
from scipy.fftpack import fft, ifft, fftshift
from numpy import pi, cos, sin, convolve
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import time
import numpy as np

AMP_THRESHOLD = 100
NOISE_THRESHOLD = 15
SAMPLES_FOR_AVERAGE = 3


NAMES = ["Node 1", "Node 2", "Rasp"]
SRS = [1750, 1750, 23800]
YS = [[], [], []]
FREQS = [[], [], []]

NODE_1_FREQ = 0
NODE_2_FREQ = 0
RASP_FREQ = 0

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
    client.subscribe("NODE_1")
    print("Subscribed to NODE_1")

    client.subscribe("NODE_2")
    print("Subscribed to NODE_2")

    client.subscribe("RASP")
    print("Subscribed to RASP")


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
    fft_data[fft_data < AMP_THRESHOLD] = 0
    filt_1 = np.ones_like(fft_data)
    filt_1[0:NOISE_THRESHOLD] = 0
    data_filt = ifft(fft_data*filt_1)
    return np.real(data_filt)


def max_freq(frequencies, sampling_rate):
    return int(np.argmax(frequencies)*sampling_rate)


def is_same_freq(freq_1, freq_2, th=20):
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
    global YS, FREQS, CONTROL_FREQ, COMPARE_FREQ, RASP_FREQ, NODE_1_FREQ, NODE_2_FREQ

    payload = 0

    if (msg.topic == "RASP"):
        payload = int(msg.payload.decode("utf-8"))
    else:
        payload = int.from_bytes(msg.payload, byteorder="little")

    finished_flag = payload & 0x8000

    is_mic_1 = msg.topic == "NODE_1"

    is_rasp = msg.topic == "RASP"

    mic_data = 0
    time_taken = 0

    if (finished_flag):
        time_taken = payload & 0x7FFF
    else:
        mic_data = payload & 0x3FF

    CURRENT_MIC = 2 if is_rasp else (0 if is_mic_1 else 1)
    y = YS[CURRENT_MIC]
    freqs = FREQS[CURRENT_MIC]
    name = NAMES[CURRENT_MIC]

    if finished_flag:

        clean_data = remove_hum(y)

        frequencies = get_fft(clean_data)
        # graph_fft(frequencies)
        sample_rate = len(y)/time_taken
        freq = max_freq(frequencies, sample_rate)

        if (freq > 0):
            freqs.append(freq)

        print("Message received from {} - Freq: {}".format(name, freq))

        if len(remove_outliers(freqs)) > SAMPLES_FOR_AVERAGE:
            avg = get_average(freqs)

            print("Average frequency {}: {}".format(name, avg))

            if CURRENT_MIC == 2:
                RASP_FREQ = avg
            else:
                if RASP_FREQ > 0:

                    if CURRENT_MIC == 0:
                        NODE_1_FREQ = avg
                    else:
                        NODE_2_FREQ = avg

                    if is_same_freq(RASP_FREQ, NODE_1_FREQ):
                        print("\n\n\n\n\n\nWent right\n\n\n\n\n\n")
                        RASP_FREQ = 0

                    elif is_same_freq(RASP_FREQ, NODE_2_FREQ):
                        print("\n\n\n\n\n\nWent left\n\n\n\n\n\n")
                        RASP_FREQ = 0
                    else:
                        print("\n\n\n\n\n\nWeird\n\n\n\n\n\n")

                    NODE_1_FREQ = 0
                    NODE_2_FREQ = 0

            freqs.clear()

        y.clear()

    else:
        y.append(mic_data)


print("Connecting to MQTT broker")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)


client.loop_forever()
