% Copyright 2014 Jason Heeris, jason.heeris@gmail.com
% 
% This file is part of the gammatone toolkit, and is licensed under the 3-clause
% BSD license: https://github.com/detly/gammatone/blob/master/COPYING
function test_ERBSpace()
    
    % Low freq, high freq, N
    erbspace_inputs = { ...
        100, 11025,  100; ...
        100, 22050,  100; ...
         20, 22050,  100; ...
         20, 44100,  100; ...
        100, 11025,   10; ...
        100, 11025, 1000; ...
        500, 80000,  200; ...
    };
    
    erbspace_results = {};
    
    num_tests = size(erbspace_inputs)(1);
    
    for tnum=1:num_tests
        [f_low, f_high, num_f] = deal(erbspace_inputs{tnum,:});
        erbspace_results(tnum, :) = ERBSpace(f_low, f_high, num_f);
    end
    
    results_file = fullfile('..', 'tests', 'data', 'test_erbspace_data.mat');
    save(results_file, 'erbspace_inputs', 'erbspace_results');
end
