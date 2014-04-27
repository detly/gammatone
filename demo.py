#!/usr/bin/python3
import audiolab
import matplotlib.pyplot as plt
import numpy as np

import gammatone.plot

# Take the first ten seconds of music
duration = 10
# Something easy to identify visually
music = audiolab.Sndfile('samples/FurElise.ogg')
# Average the stereo signal
signal = music.read_frames(10 * music.samplerate).mean(1)

# Gammatone-based spectrogram parameters
twin = 0.008
thop = twin/2
channels = 256
fmin = 20

# Set up the plot
fig = plt.figure()
axes = fig.add_axes([0.1,0.1,0.8,0.8])

gammatone.plot.gtgram_plot(
    axes,
    signal,
    music.samplerate,
    twin, thop, channels, fmin)

plt.show()
