#!/usr/bin/env python3
# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
# 
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
from __future__ import division
import nose
import numpy as np
import scipy.io
from pkg_resources import resource_stream

import gammatone.fftweight

REF_DATA_FILENAME = 'data/test_fft2gtmx_data.mat'

INPUT_KEY  = 'fft2gtmx_inputs'
RESULT_KEY = 'fft2gtmx_results'

INPUT_COLS  = ('nfft', 'sr', 'nfilts', 'width', 'fmin', 'fmax', 'maxlen')
RESULT_COLS = ('weights', 'gain',)

def load_reference_data():
    """ Load test data generated from the reference code """
    # Load test data
    with resource_stream(__name__, REF_DATA_FILENAME) as test_data:
        data = scipy.io.loadmat(test_data, squeeze_me=False)
    
    zipped_data = zip(data[INPUT_KEY], data[RESULT_KEY])
    
    for inputs, refs in zipped_data:
        input_dict = dict(zip(INPUT_COLS, map(np.squeeze, inputs)))
        ref_dict = dict(zip(RESULT_COLS, map(np.squeeze, refs)))
        yield (input_dict, ref_dict)


def fft_weights_funcs(args, expected):
    """
    Construct a pair of unit tests for the gains and weights of the FFT to
    gammatonegram calculation. Returns two functions: test_gains, test_weights.
    """
    args = list(args)
    expected_weights = expected[0]
    expected_gains = expected[1]
    
    # Convert nfft, nfilts, maxlen to ints
    args[0] = int(args[0])
    args[2] = int(args[2])
    args[6] = int(args[6])
    
    weights, gains = gammatone.fftweight.fft_weights(*args)
    
    (test_weights_desc, test_gains_desc) = (
        "FFT weights {:s} for nfft = {:d}, fs = {:d}, nfilts = {:d}".format(
            label,
            int(args[0]),
            int(args[1]),
            int(args[2]),
    ) for label in ("weights", "gains"))
    
    def test_gains():
        assert gains.shape == expected_gains.shape 
        assert np.allclose(gains, expected_gains, rtol=1e-6, atol=1e-12)
 
    def test_weights():
        assert weights.shape == expected_weights.shape
        assert np.allclose(weights, expected_weights, rtol=1e-6, atol=1e-12)
 
    test_gains.description = test_gains_desc
    test_weights.description = test_weights_desc
    
    return test_gains, test_weights


def test_fft_weights():
    for inputs, refs in load_reference_data():
        args = tuple(inputs[col] for col in INPUT_COLS)        
        expected = (refs['weights'], refs['gain'])
        test_gains, test_weights = fft_weights_funcs(args, expected)
        yield test_gains
        yield test_weights


if __name__ == '__main__':
    nose.main()
