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

REF_DATA_FILENAME = 'data/test_erbspace_data.mat'

INPUT_KEY  = 'erbspace_inputs'
RESULT_KEY = 'erbspace_results'

INPUT_COLS  = ('f_low', 'f_high', 'num_f')
RESULT_COLS = ('cfs',)


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
    

def test_ERB_space_known_values():
    for inputs, refs in load_reference_data():
        args = (
            inputs['f_low'],
            inputs['f_high'],
            inputs['num_f'],
        )
        
        expected = (refs['cfs'],)
        
        yield ERBSpaceTester(args, expected)


class ERBSpaceTester:
    
    def __init__(self, args, expected):
        self.args = args
        self.expected = expected[0]
        self.description = (
            "ERB space for {:.1f} {:.1f} {:d}".format(
                float(self.args[0]),
                float(self.args[1]),
                int(self.args[2]),
            )
        )
    
    def __call__(self):
        result = gammatone.filters.erb_space(*self.args)
        assert np.allclose(result, self.expected, rtol=1e-6, atol=1e-10)

if __name__ == '__main__':
    nose.main()
