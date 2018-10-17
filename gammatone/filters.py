# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
# 
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
"""
This module contains functions for constructing sets of equivalent rectangular
bandwidth gammatone filters.
"""
from __future__ import division
from collections import namedtuple

import numpy as np
import scipy as sp
from scipy import signal as sgn

DEFAULT_FILTER_NUM = 100
DEFAULT_LOW_FREQ = 100
DEFAULT_HIGH_FREQ = 44100 / 4


def erb_point(low_freq, high_freq, fraction):
    """
    Calculates a single point on an ERB scale between ``low_freq`` and
    ``high_freq``, determined by ``fraction``. When ``fraction`` is ``1``,
    ``low_freq`` will be returned. When ``fraction`` is ``0``, ``high_freq``
    will be returned.
    
    ``fraction`` can actually be outside the range ``[0, 1]``, which in general
    isn't very meaningful, but might be useful when ``fraction`` is rounded a
    little above or below ``[0, 1]`` (eg. for plot axis labels).
    """
    # Change the following three parameters if you wish to use a different ERB
    # scale. Must change in MakeERBCoeffs too.
    # TODO: Factor these parameters out
    ear_q = 9.26449 # Glasberg and Moore Parameters
    min_bw = 24.7
    order = 1

    # All of the following expressions are derived in Apple TR #35, "An
    # Efficient Implementation of the Patterson-Holdsworth Cochlear Filter
    # Bank." See pages 33-34.
    erb_point = (
        -ear_q * min_bw
        + np.exp(
            fraction * (
                -np.log(high_freq + ear_q * min_bw)
                + np.log(low_freq + ear_q * min_bw)
                )
        ) *
        (high_freq + ear_q * min_bw)
    )
    
    return erb_point


def erb_space(
    low_freq=DEFAULT_LOW_FREQ,
    high_freq=DEFAULT_HIGH_FREQ,
    num=DEFAULT_FILTER_NUM):
    """
    This function computes an array of ``num`` frequencies uniformly spaced
    between ``high_freq`` and ``low_freq`` on an ERB scale.
    
    For a definition of ERB, see Moore, B. C. J., and Glasberg, B. R. (1983).
    "Suggested formulae for calculating auditory-filter bandwidths and
    excitation patterns," J. Acoust. Soc. Am. 74, 750-753.
    """
    return erb_point(
        low_freq,
        high_freq,
        np.arange(1, num + 1) / num
        )


def centre_freqs(fs, num_freqs, cutoff):
    """
    Calculates an array of centre frequencies (for :func:`make_erb_filters`)
    from a sampling frequency, lower cutoff frequency and the desired number of
    filters.
    
    :param fs: sampling rate
    :param num_freqs: number of centre frequencies to calculate
    :type num_freqs: int
    :param cutoff: lower cutoff frequency
    :return: same as :func:`erb_space`
    """
    return erb_space(cutoff, fs / 2, num_freqs)


def make_erb_filters(fs, centre_freqs, width=1.0):
    """
    This function computes the filter coefficients for a bank of 
    Gammatone filters. These filters were defined by Patterson and Holdworth for
    simulating the cochlea. 
    
    The result is returned as a :class:`ERBCoeffArray`. Each row of the
    filter arrays contains the coefficients for four second order filters. The
    transfer function for these four filters share the same denominator (poles)
    but have different numerators (zeros). All of these coefficients are
    assembled into one vector that the ERBFilterBank can take apart to implement
    the filter.
    
    The filter bank contains "numChannels" channels that extend from
    half the sampling rate (fs) to "lowFreq". Alternatively, if the numChannels
    input argument is a vector, then the values of this vector are taken to be
    the center frequency of each desired filter. (The lowFreq argument is
    ignored in this case.)
    
    Note this implementation fixes a problem in the original code by
    computing four separate second order filters. This avoids a big problem with
    round off errors in cases of very small cfs (100Hz) and large sample rates
    (44kHz). The problem is caused by roundoff error when a number of poles are
    combined, all very close to the unit circle. Small errors in the eigth order
    coefficient, are multiplied when the eigth root is taken to give the pole
    location. These small errors lead to poles outside the unit circle and
    instability. Thanks to Julius Smith for leading me to the proper
    explanation.
    
    Execute the following code to evaluate the frequency response of a 10
    channel filterbank::
    
        fcoefs = MakeERBFilters(16000,10,100);
        y = ERBFilterBank([1 zeros(1,511)], fcoefs);
        resp = 20*log10(abs(fft(y')));
        freqScale = (0:511)/512*16000;
        semilogx(freqScale(1:255),resp(1:255,:));
        axis([100 16000 -60 0])
        xlabel('Frequency (Hz)'); ylabel('Filter Response (dB)');
    
    | Rewritten by Malcolm Slaney@Interval.  June 11, 1998.
    | (c) 1998 Interval Research Corporation
    |
    | (c) 2012 Jason Heeris (Python implementation)
    """
    T = 1 / fs
    # Change the followFreqing three parameters if you wish to use a different
    # ERB scale. Must change in ERBSpace too.
    # TODO: factor these out
    ear_q = 9.26449 # Glasberg and Moore Parameters
    min_bw = 24.7
    order = 1

    erb = width*((centre_freqs / ear_q) ** order + min_bw ** order) ** ( 1 /order)
    B = 1.019 * 2 * np.pi * erb

    arg = 2 * centre_freqs * np.pi * T
    vec = np.exp(2j * arg)

    A0 = T
    A2 = 0
    B0 = 1
    B1 = -2 * np.cos(arg) / np.exp(B * T)
    B2 = np.exp(-2 * B * T)
    
    rt_pos = np.sqrt(3 + 2 ** 1.5)
    rt_neg = np.sqrt(3 - 2 ** 1.5)
    
    common = -T * np.exp(-(B * T))
    
    # TODO: This could be simplified to a matrix calculation involving the
    # constant first term and the alternating rt_pos/rt_neg and +/-1 second
    # terms
    k11 = np.cos(arg) + rt_pos * np.sin(arg)
    k12 = np.cos(arg) - rt_pos * np.sin(arg)
    k13 = np.cos(arg) + rt_neg * np.sin(arg)
    k14 = np.cos(arg) - rt_neg * np.sin(arg)

    A11 = common * k11
    A12 = common * k12
    A13 = common * k13
    A14 = common * k14

    gain_arg = np.exp(1j * arg - B * T)

    gain = np.abs(
            (vec - gain_arg * k11)
          * (vec - gain_arg * k12)
          * (vec - gain_arg * k13)
          * (vec - gain_arg * k14)
          * (  T * np.exp(B * T)
             / (-1 / np.exp(B * T) + 1 + vec * (1 - np.exp(B * T)))
            )**4
        )

    allfilts = np.ones_like(centre_freqs)
    
    fcoefs = np.column_stack([
        A0 * allfilts, A11, A12, A13, A14, A2*allfilts,
        B0 * allfilts, B1, B2,
        gain
    ])
    
    return fcoefs


def erb_filterbank(wave, coefs):
    """
    :param wave: input data (one dimensional sequence)
    :param coefs: gammatone filter coefficients
    
    Process an input waveform with a gammatone filter bank. This function takes
    a single sound vector, and returns an array of filter outputs, one channel
    per row.
    
    The fcoefs parameter, which completely specifies the Gammatone filterbank,
    should be designed with the :func:`make_erb_filters` function.
    
    | Malcolm Slaney @ Interval, June 11, 1998.
    | (c) 1998 Interval Research Corporation
    | Thanks to Alain de Cheveigne' for his suggestions and improvements.
    |
    | (c) 2013 Jason Heeris (Python implementation)
    """
    output = np.zeros((coefs[:,9].shape[0], wave.shape[0]))
    
    gain = coefs[:, 9]
    # A0, A11, A2
    As1 = coefs[:, (0, 1, 5)]
    # A0, A12, A2
    As2 = coefs[:, (0, 2, 5)]
    # A0, A13, A2
    As3 = coefs[:, (0, 3, 5)]
    # A0, A14, A2
    As4 = coefs[:, (0, 4, 5)]
    # B0, B1, B2
    Bs = coefs[:, 6:9]
    
    # Loop over channels
    for idx in range(0, coefs.shape[0]):
        # These seem to be reversed (in the sense of A/B order), but that's what
        # the original code did...
        # Replacing these with polynomial multiplications reduces both accuracy
        # and speed.
        y1 = sgn.lfilter(As1[idx], Bs[idx], wave)
        y2 = sgn.lfilter(As2[idx], Bs[idx], y1)
        y3 = sgn.lfilter(As3[idx], Bs[idx], y2)
        y4 = sgn.lfilter(As4[idx], Bs[idx], y3)
        output[idx, :] = y4 / gain[idx]
        
    return output
