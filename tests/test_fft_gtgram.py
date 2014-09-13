#!/usr/bin/env python3
# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
#
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
from mock import patch
import nose
import numpy as np
import scipy.io
from pkg_resources import resource_stream

import gammatone.fftweight

REF_DATA_FILENAME = 'data/test_fft_gammatonegram_data.mat'

INPUT_KEY  = 'fft_gammatonegram_inputs'
MOCK_KEY   = 'fft_gammatonegram_mocks'
RESULT_KEY = 'fft_gammatonegram_results'

INPUT_COLS  = ('name', 'wave', 'fs', 'twin', 'thop', 'channels', 'fmin')
MOCK_COLS   = ('wts',)
RESULT_COLS = ('res', 'window', 'nfft', 'nwin', 'nhop')


def load_reference_data():
    """ Load test data generated from the reference code """
    # Load test data
    with resource_stream(__name__, REF_DATA_FILENAME) as test_data:
        data = scipy.io.loadmat(test_data, squeeze_me=False)

    zipped_data = zip(data[INPUT_KEY], data[MOCK_KEY], data[RESULT_KEY])
    for inputs, mocks, refs in zipped_data:
        input_dict = dict(zip(INPUT_COLS, inputs))
        mock_dict  = dict(zip(MOCK_COLS, mocks))
        ref_dict = dict(zip(RESULT_COLS, refs))

        yield (input_dict, mock_dict, ref_dict)


def test_fft_specgram_window():
    for inputs, mocks, refs in load_reference_data():
        args = (
            refs['nfft'],
            refs['nwin'],
        )

        expected = (
            refs['window'],
        )

        yield FFTGtgramWindowTester(inputs['name'], args, expected)

class FFTGtgramWindowTester:

    def __init__(self, name, args, expected):
        self.nfft = args[0].squeeze()
        self.nwin = args[1].squeeze()
        self.expected = expected[0].squeeze()

        self.description = (
            "FFT gammatonegram window for nfft = {:f}, nwin = {:f}".format(
                float(self.nfft), float(self.nwin)
            ))

    def __call__(self):
        result = gammatone.fftweight.specgram_window(self.nfft, self.nwin)
        max_diff = np.max(np.abs(result - self.expected))
        diagnostic = "Maximum difference: {:6e}".format(max_diff)
        assert np.allclose(result, self.expected, rtol=1e-6, atol=1e-12), diagnostic


def test_fft_gtgram():
    for inputs, mocks, refs in load_reference_data():
        args = (
            inputs['fs'],
            inputs['twin'],
            inputs['thop'],
            inputs['channels'],
            inputs['fmin']
        )

        yield FFTGammatonegramTester(
            inputs['name'][0],
            args,
            inputs['wave'],
            mocks['wts'],
            refs['window'],
            refs['res']
        )

class FFTGammatonegramTester:
    """ Testing class for gammatonegram calculation """

    def __init__(self, name, args, sig, fft_weights, window, expected):
        self.signal = np.asarray(sig).squeeze()
        self.expected = np.asarray(expected).squeeze()
        self.fft_weights = np.asarray(fft_weights)
        self.args = args
        self.window = window.squeeze()

        self.description = "FFT gammatonegram for {:s}".format(name)

    def __call__(self):
        # Note that the second return value from fft_weights isn't actually used
        with patch(
                'gammatone.fftweight.fft_weights',
                return_value=(self.fft_weights, None)), \
            patch(
                'gammatone.fftweight.specgram_window',
                return_value=self.window):

            result = gammatone.fftweight.fft_gtgram(self.signal, *self.args)

            max_diff = np.max(np.abs(result - self.expected))
            diagnostic = "Maximum difference: {:6e}".format(max_diff)

            assert np.allclose(result, self.expected, rtol=1e-6, atol=1e-12), diagnostic

if __name__ == '__main__':
    nose.main()
