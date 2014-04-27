#!/usr/bin/env python3
# Copyright 2014 Jason Heeris, jason.heeris@gmail.com
# 
# This file is part of the gammatone toolkit, and is licensed under the 3-clause
# BSD license: https://github.com/detly/gammatone/blob/master/COPYING
import nose
from mock import patch

import gammatone.filters

EXPECTED_PARAMS = (
    ((0, 0, 0), (0, 0, 0)),
    ((22050, 100, 100), (100, 11025, 100)),
    ((44100, 100, 100), (100, 22050, 100)),
    ((44100, 100, 20), (20, 22050, 100)),
    ((88200, 100, 20), (20, 44100, 100)),
    ((22050, 100, 10), (10, 11025, 100)),
    ((22050, 1000, 100), (100, 11025, 1000)),
    ((160000, 500, 200), (200, 80000, 500)),
)


def test_centre_freqs():
    for args, params in EXPECTED_PARAMS:
        yield CentreFreqsTester(args, params)


class CentreFreqsTester:

    def __init__(self, args, params):
        self.args = args
        self.params = params
        self.description = "Centre freqs for {:g} {:d} {:g}".format(*args)


    @patch('gammatone.filters.erb_space')
    def __call__(self, erb_space_mock):
        gammatone.filters.centre_freqs(*self.args)
        erb_space_mock.assert_called_with(*self.params)


if __name__ == '__main__':
    nose.main()
