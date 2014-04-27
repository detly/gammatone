# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
# 
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
"""
Plotting utilities related to gammatone analysis, primarily for use with
``matplotlib``.
"""
import matplotlib.ticker
import numpy as np
import scipy.constants

from .filters import erb_point
import gammatone.gtgram


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
        axes, x, fs,
        window_time, hop_time, channels, f_min,
        imshow_args=None
        ):
    """
    Plots a spectrogram-like time frequency magnitude array based on gammatone
    subband filters. See the documentation for :func:`gtgram.gtgram`.
    """
    # Set a nice formatter for the y-axis
    formatter = ERBFormatter(f_min, fs/2, unit='Hz', places=0)
    axes.yaxis.set_major_formatter(formatter)
    
    # Figure out time axis scaling
    duration = len(x) / fs
    
    # Calculate 1:1 aspect ratio
    aspect_ratio = duration/scipy.constants.golden
    
    gtg = gammatone.gtgram.gtgram(x, fs, window_time, hop_time, channels, f_min)
    Z = np.flipud(20 * np.log10(gtg))
    
    img = axes.imshow(Z, extent=[0, duration, 1, 0], aspect=aspect_ratio)

