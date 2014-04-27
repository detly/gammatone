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

REF_DATA_FILENAME = 'data/test_erb_filter_data.mat'

INPUT_KEY  = 'erb_filter_inputs'
RESULT_KEY = 'erb_filter_results'

INPUT_COLS  = ('fs', 'cfs')
RESULT_COLS = ('fcoefs',)

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


def test_make_ERB_filters_known_values():
    for inputs, refs in load_reference_data():
        args = (
            inputs['fs'],
            inputs['cfs'],
        )
        
        expected = (refs['fcoefs'],)
        
        yield MakeERBFiltersTester(args, expected)


class MakeERBFiltersTester:
    
    def __init__(self, args, expected):
        self.fs = args[0]
        self.cfs = args[1]
        self.expected = expected[0]
        self.description = (
            "Gammatone filters for {:f}, {:.1f} ... {:.1f}".format(
                float(self.fs),
                float(self.cfs[0]),
                float(self.cfs[-1])
        ))
    
    def __call__(self):
        result = gammatone.filters.make_erb_filters(self.fs, self.cfs)
        assert np.allclose(result, self.expected, rtol=1e-6, atol=1e-12)

if __name__ == '__main__':
    nose.main()
