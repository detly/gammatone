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

import gammatone.gtgram

REF_DATA_FILENAME = 'data/test_gammatonegram_data.mat'

INPUT_KEY  = 'gammatonegram_inputs'
MOCK_KEY   = 'gammatonegram_mocks'
RESULT_KEY = 'gammatonegram_results'

INPUT_COLS  = ('name', 'wave', 'fs', 'twin', 'thop', 'channels', 'fmin')
MOCK_COLS   = ('erb_fb', 'erb_fb_cols')
RESULT_COLS = ('gtgram', 'nwin', 'hopsamps', 'ncols')


def load_reference_data():
    """ Load test data generated from the reference code """
    # Load test data
    with resource_stream(__name__, REF_DATA_FILENAME) as test_data:
        data = scipy.io.loadmat(test_data, squeeze_me=True)

    zipped_data = zip(data[INPUT_KEY], data[MOCK_KEY], data[RESULT_KEY])
    for inputs, mocks, refs in zipped_data:
        input_dict = dict(zip(INPUT_COLS, inputs))
        mock_dict  = dict(zip(MOCK_COLS, mocks))
        ref_dict = dict(zip(RESULT_COLS, refs))
        yield (input_dict, mock_dict, ref_dict)


def test_nstrides():
    """ Test gamamtonegram stride calculations """
    for inputs, mocks, refs in load_reference_data():
        args = (
            inputs['fs'],
            inputs['twin'],
            inputs['thop'],
            mocks['erb_fb_cols']
        )

        expected = (
            refs['nwin'],
            refs['hopsamps'],
            refs['ncols']
        )

        yield GTGramStrideTester(inputs['name'], args, expected)


class GTGramStrideTester:
    """ Testing class for gammatonegram stride calculation """

    def __init__(self, name, inputs, expected):
        self.inputs      = inputs
        self.expected    = expected
        self.description = "Gammatonegram strides for {:s}".format(name)

    def __call__(self):
        results = gammatone.gtgram.gtgram_strides(*self.inputs)

        diagnostic = (
            "result: {:s}, expected: {:s}".format(
                str(results),
                str(self.expected)
            )
        )

        # These are integer values, so use direct equality
        assert results == self.expected


# TODO: possibly mock out gtgram_strides

def test_gtgram():
    for inputs, mocks, refs in load_reference_data():
        args = (
            inputs['fs'],
            inputs['twin'],
            inputs['thop'],
            inputs['channels'],
            inputs['fmin']
        )

        yield GammatonegramTester(
            inputs['name'],
            args,
            inputs['wave'],
            mocks['erb_fb'],
            refs['gtgram']
        )

class GammatonegramTester:
    """ Testing class for gammatonegram calculation """

    def __init__(self, name, args, sig, erb_fb_out, expected):
        self.signal = np.asarray(sig)
        self.expected = np.asarray(expected)
        self.erb_fb_out = np.asarray(erb_fb_out)
        self.args = args

        self.description = "Gammatonegram for {:s}".format(name)

    def __call__(self):
        with patch(
            'gammatone.gtgram.erb_filterbank',
            return_value=self.erb_fb_out):

            result = gammatone.gtgram.gtgram(self.signal, *self.args)

            max_diff = np.max(np.abs(result - self.expected))
            diagnostic = "Maximum difference: {:6e}".format(max_diff)

            assert np.allclose(result, self.expected, rtol=1e-6, atol=1e-12), diagnostic

if __name__ == '__main__':
    nose.main()
