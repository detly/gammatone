# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
# 
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
from __future__ import division
import numpy as np

from .filters import make_erb_filters, centre_freqs, erb_filterbank

"""
This module contains functions for rendering "spectrograms" which use gammatone
filterbanks instead of Fourier transforms.
"""

def round_half_away_from_zero(num):
    """ Implement the round-half-away-from-zero rule, where fractional parts of
    0.5 result in rounding up to the nearest positive integer for positive
    numbers, and down to the nearest negative number for negative integers.
    """
    return np.sign(num) * np.floor(np.abs(num) + 0.5)


def gtgram_strides(fs, window_time, hop_time, filterbank_cols):
    """
    Calculates the window size for a gammatonegram.
    
    @return a tuple of (window_size, hop_samples, output_columns)
    """
    nwin        = int(round_half_away_from_zero(window_time * fs))
    hop_samples = int(round_half_away_from_zero(hop_time * fs))
    columns     = (1
                    + int(
                        np.floor(
                            (filterbank_cols - nwin)
                            / hop_samples
                        )
                    )
                  )
        
    return (nwin, hop_samples, columns)


def gtgram_xe(wave, fs, channels, f_min):
    """ Calculate the intermediate ERB filterbank processed matrix """
    cfs = centre_freqs(fs, channels, f_min)
    fcoefs = np.flipud(make_erb_filters(fs, cfs))
    xf = erb_filterbank(wave, fcoefs)
    xe = np.power(xf, 2)
    return xe


def gtgram(
    wave,
    fs,
    window_time, hop_time,
    channels,
    f_min):
    """
    Calculate a spectrogram-like time frequency magnitude array based on
    gammatone subband filters. The waveform ``wave`` (at sample rate ``fs``) is
    passed through an multi-channel gammatone auditory model filterbank, with
    lowest frequency ``f_min`` and highest frequency ``f_max``. The outputs of
    each band then have their energy integrated over windows of ``window_time``
    seconds, advancing by ``hop_time`` secs for successive columns. These
    magnitudes are returned as a nonnegative real matrix with ``channels`` rows.
    
    | 2009-02-23 Dan Ellis dpwe@ee.columbia.edu
    |
    | (c) 2013 Jason Heeris (Python implementation)
    """
    xe = gtgram_xe(wave, fs, channels, f_min)    
    
    nwin, hop_samples, ncols = gtgram_strides(
        fs,
        window_time,
        hop_time,
        xe.shape[1]
    )
    
    y = np.zeros((channels, ncols))
    
    for cnum in range(ncols):
        segment = xe[:, cnum * hop_samples + np.arange(nwin)]
        y[:, cnum] = np.sqrt(segment.mean(1))
    
    return y
