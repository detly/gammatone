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

REF_DATA_FILENAME = 'data/test_specgram_data.mat'

INPUT_KEY  = 'specgram_inputs'
MOCK_KEY   = 'specgram_mocks'
RESULT_KEY = 'specgram_results'

INPUT_COLS  = ('name', 'wave', 'nfft', 'fs', 'nwin', 'nhop')
MOCK_COLS   = ('window',)
RESULT_COLS = ('res',)


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


def test_specgram():
    for inputs, mocks, refs in load_reference_data():
        args = (
            inputs['nfft'],
            inputs['fs'],
            inputs['nwin'],
            inputs['nhop'],
        )

        yield SpecgramTester(
            inputs['name'][0],
            args,
            inputs['wave'],
            mocks['window'],
            refs['res']
        )

class SpecgramTester:
    """ Testing class for specgram replacement calculation """

    def __init__(self, name, args, sig, window, expected):
        self.signal = np.asarray(sig).squeeze()
        self.expected = np.asarray(expected).squeeze()
        self.args = [int(a.squeeze()) for a in args]
        self.window = window.squeeze()
        self.description = "Specgram for {:s}".format(name)


    def __call__(self):
        with patch(
                'gammatone.fftweight.specgram_window',
                return_value=self.window):
            result = gammatone.fftweight.specgram(self.signal, *self.args)

            max_diff = np.max(np.abs(result - self.expected))
            diagnostic = "Maximum difference: {:6e}".format(max_diff)

            assert np.allclose(result, self.expected, rtol=1e-6, atol=1e-12), diagnostic

if __name__ == '__main__':
    nose.main()
