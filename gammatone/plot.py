# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
#
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
"""
Plotting utilities related to gammatone analysis, primarily for use with
``matplotlib``.
"""
from __future__ import division
import argparse
import os.path

import matplotlib.pyplot
import matplotlib.ticker
import numpy as np
import scipy.constants
import scipy.io.wavfile

from .filters import erb_point
import gammatone.gtgram
import gammatone.fftweight


class ERBFormatter(matplotlib.ticker.EngFormatter):
    """
    Axis formatter for gammatone filterbank analysis. This formatter calculates
    the ERB spaced frequencies used for analysis, and renders them similarly to
    the engineering axis formatter.

    The scale is changed so that `[0, 1]` corresponds to ERB spaced frequencies
    from ``high_freq`` to ``low_freq`` (note the reversal). It should be used
    with ``imshow`` where the ``extent`` argument is ``[a, b, 1, 0]`` (again,
    note the inversion).
    """

    def __init__(self, low_freq, high_freq, *args, **kwargs):
        """
        Creates a new :class ERBFormatter: for use with ``matplotlib`` plots.
        Note that this class does not supply the ``units`` or ``places``
        arguments; typically these would be ``'Hz'`` and ``0``.

        :param low_freq: the low end of the gammatone filterbank frequency range
        :param high_freq: the high end of the gammatone filterbank frequency
          range
        """
        self.low_freq = low_freq
        self.high_freq = high_freq
        super().__init__(*args, **kwargs)

    def _erb_axis_scale(self, fraction):
        return erb_point(self.low_freq, self.high_freq, fraction)

    def __call__(self, val, pos=None):
        newval = self._erb_axis_scale(val)
        return super().__call__(newval, pos)


def gtgram_plot(
        gtgram_function,
        axes, x, fs,
        window_time, hop_time, channels, f_min,
        imshow_args=None
        ):
    """
    Plots a spectrogram-like time frequency magnitude array based on gammatone
    subband filters.

    :param gtgram_function: A function with signature::

        fft_gtgram(
            wave,
            fs,
            window_time, hop_time,
            channels,
            f_min)

    See :func:`gammatone.gtgram.gtgram` for details of the paramters.
    """
    # Set a nice formatter for the y-axis
    formatter = ERBFormatter(f_min, fs/2, unit='Hz', places=0)
    axes.yaxis.set_major_formatter(formatter)

    # Figure out time axis scaling
    duration = len(x) / fs

    # Calculate 1:1 aspect ratio
    aspect_ratio = duration/scipy.constants.golden

    gtg = gtgram_function(x, fs, window_time, hop_time, channels, f_min)
    Z = np.flipud(20 * np.log10(gtg))

    img = axes.imshow(Z, extent=[0, duration, 1, 0], aspect=aspect_ratio)


# Entry point for CLI script

HELP_TEXT = """\
Plots the gammatone filterbank analysis of a WAV file.

If the file contains more than one channel, all channels are averaged before
performing analysis.
"""


def render_audio_from_file(path, duration, function):
    """
    Renders the given ``duration`` of audio from the audio file at ``path``
    using the gammatone spectrogram function ``function``.
    """
    samplerate, data = scipy.io.wavfile.read(path)

    # Average the stereo signal
    if duration:
        nframes = duration * samplerate
        data = data[0 : nframes, :]

    signal = data.mean(1)

    # Default gammatone-based spectrogram parameters
    twin = 0.08
    thop = twin / 2
    channels = 1024
    fmin = 20

    # Set up the plot
    fig = matplotlib.pyplot.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    gtgram_plot(
        function,
        axes,
        signal,
        samplerate,
        twin, thop, channels, fmin)

    axes.set_title(os.path.basename(path))
    axes.set_xlabel("Time (s)")
    axes.set_ylabel("Frequency")

    matplotlib.pyplot.show()


def main():
    """
    Entry point for CLI application to plot gammatonegrams of sound files.
    """
    parser = argparse.ArgumentParser(description=HELP_TEXT)

    parser.add_argument(
        'sound_file',
        help="The sound file to graph. See the help text for supported formats.")

    parser.add_argument(
        '-d', '--duration', type=int,
        help="The time in seconds from the start of the audio to use for the "
             "graph (default is to use the whole file)."
        )

    parser.add_argument(
        '-a', '--accurate', action='store_const', dest='function',
        const=gammatone.gtgram.gtgram, default=gammatone.fftweight.fft_gtgram,
        help="Use the full filterbank approach instead of the weighted FFT "
             "approximation. This is much slower, and uses a lot of memory, but"
             " is more accurate."
        )

    args = parser.parse_args()

    return render_audio_from_file(args.sound_file, args.duration, args.function)
