# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
# 
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
"""
This module contains functions for calculating weights to approximate a
gammatone filterbank-like "spectrogram" from a Fourier transform.
"""
from __future__ import division
import numpy as np

import gammatone.filters as filters
import gammatone.gtgram as gtgram

def specgram_window(
        nfft,
        nwin,
    ):
    """
    Window calculation used in specgram replacement function. Hann window of
    width `nwin` centred in an array of width `nfft`.
    """
    halflen = nwin // 2
    halff = nfft // 2 # midpoint of win
    acthalflen = int(np.floor(min(halff, halflen)))
    halfwin = 0.5 * ( 1 + np.cos(np.pi * np.arange(0, halflen+1)/halflen))
    win = np.zeros((nfft,))
    win[halff:halff+acthalflen] = halfwin[0:acthalflen];
    win[halff:halff-acthalflen:-1] = halfwin[0:acthalflen];
    return win


def specgram(x, n, sr, w, h):
    """ Substitute for Matlab's specgram, calculates a simple spectrogram.

    :param x: The signal to analyse
    :param n: The FFT length
    :param sr: The sampling rate
    :param w: The window length (see :func:`specgram_window`)
    :param h: The hop size (must be greater than zero)
    """
    # Based on Dan Ellis' myspecgram.m,v 1.1 2002/08/04
    assert h > 0, "Must have a hop size greater than 0"

    s = x.shape[0]
    win = specgram_window(n, w)

    c = 0

    # pre-allocate output array
    ncols = 1 + int(np.floor((s - n)/h))
    d = np.zeros(((1 + n // 2), ncols), np.dtype(complex))

    for b in range(0, s - n, h):
      u = win * x[b : b + n]
      t = np.fft.fft(u)
      d[:, c] = t[0 : (1 + n // 2)].T
      c = c + 1

    return d


def fft_weights(
    nfft,
    fs,
    nfilts,
    width,
    fmin,
    fmax,
    maxlen):
    """
    :param nfft: the source FFT size
    :param sr: sampling rate (Hz)
    :param nfilts: the number of output bands required (default 64)
    :param width: the constant width of each band in Bark (default 1)
    :param fmin: lower limit of frequencies (Hz)
    :param fmax: upper limit of frequencies (Hz)
    :param maxlen: number of bins to truncate the rows to
    
    :return: a tuple `weights`, `gain` with the calculated weight matrices and
             gain vectors
    
    Generate a matrix of weights to combine FFT bins into Gammatone bins.
    
    Note about `maxlen` parameter: While wts has nfft columns, the second half
    are all zero. Hence, aud spectrum is::
    
        fft2gammatonemx(nfft,sr)*abs(fft(xincols,nfft))
    
    `maxlen` truncates the rows to this many bins.
    
    | (c) 2004-2009 Dan Ellis dpwe@ee.columbia.edu  based on rastamat/audspec.m
    | (c) 2012 Jason Heeris (Python implementation)
    """
    ucirc = np.exp(1j * 2 * np.pi * np.arange(0, nfft / 2 + 1) / nfft)[None, ...]
    
    # Common ERB filter code factored out
    cf_array = filters.erb_space(fmin, fmax, nfilts)[::-1]

    _, A11, A12, A13, A14, _, _, _, B2, gain = (
        filters.make_erb_filters(fs, cf_array, width).T
    )
    
    A11, A12, A13, A14 = A11[..., None], A12[..., None], A13[..., None], A14[..., None]

    r = np.sqrt(B2)
    theta = 2 * np.pi * cf_array / fs    
    pole = (r * np.exp(1j * theta))[..., None]
    
    GTord = 4
    
    weights = np.zeros((nfilts, nfft))

    weights[:, 0:ucirc.shape[1]] = (
          np.abs(ucirc + A11 * fs) * np.abs(ucirc + A12 * fs)
        * np.abs(ucirc + A13 * fs) * np.abs(ucirc + A14 * fs)
        * np.abs(fs * (pole - ucirc) * (pole.conj() - ucirc)) ** (-GTord)
        / gain[..., None]
    )

    weights = weights[:, 0:int(maxlen)]

    return weights, gain


def fft_gtgram(
    wave,
    fs,
    window_time, hop_time,
    channels,
    f_min):
    """
    Calculate a spectrogram-like time frequency magnitude array based on
    an FFT-based approximation to gammatone subband filters.

    A matrix of weightings is calculated (using :func:`gtgram.fft_weights`), and
    applied to the FFT of the input signal (``wave``, using sample rate ``fs``).
    The result is an approximation of full filtering using an ERB gammatone
    filterbank (as per :func:`gtgram.gtgram`).

    ``f_min`` determines the frequency cutoff for the corresponding gammatone
    filterbank. ``window_time`` and ``hop_time`` (both in seconds) are the size
    and overlap of the spectrogram columns.

    | 2009-02-23 Dan Ellis dpwe@ee.columbia.edu
    |
    | (c) 2013 Jason Heeris (Python implementation)
    """
    width = 1 # Was a parameter in the MATLAB code

    nfft = int(2 ** (np.ceil(np.log2(2 * window_time * fs))))
    nwin, nhop, _ = gtgram.gtgram_strides(fs, window_time, hop_time, 0);

    gt_weights, _ = fft_weights(
            nfft,
            fs,
            channels,
            width,
            f_min,
            fs / 2,
            nfft / 2 + 1
        )

    sgram = specgram(wave, nfft, fs, nwin, nhop)

    result = gt_weights.dot(np.abs(sgram)) / nfft

    return result
