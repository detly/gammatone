#!/usr/bin/env python3
# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
# 
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
import nose
import numpy as np
import scipy.io
from pkg_resources import resource_stream

import gammatone.filters

REF_DATA_FILENAME = 'data/test_filterbank_data.mat'

INPUT_KEY  = 'erb_filterbank_inputs'
RESULT_KEY = 'erb_filterbank_results'

INPUT_COLS  = ('fcoefs', 'wave')
RESULT_COLS = ('filterbank',)

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


def test_ERB_filterbank_known_values():
    for inputs, refs in load_reference_data():
        args = (
            inputs['wave'],
            inputs['fcoefs'],
        )
        
        expected = (refs['filterbank'],)
        
        yield ERBFilterBankTester(args, expected)


class ERBFilterBankTester:
    
    def __init__(self, args, expected):
        self.signal = args[0]
        self.fcoefs = args[1]
        self.expected = expected[0]
        
        self.description = (
            "Gammatone filterbank result for {:.1f} ... {:.1f}".format(
                self.fcoefs[0][0],
                self.fcoefs[0][1]
        ))
    
    def __call__(self):
        result = gammatone.filters.erb_filterbank(self.signal, self.fcoefs)
        assert np.allclose(result, self.expected, rtol=1e-5, atol=1e-12)


if __name__ == '__main__':
    nose.main()
