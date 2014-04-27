% Copyright 2014 Jason Heeris, jason.heeris@gmail.com
% 
% This file is part of the gammatone toolkit, and is licensed under the 3-clause
% BSD license: https://github.com/detly/gammatone/blob/master/COPYING
function test_MakeERBFilters()
    
    erb_space_inputs = { ...
        100, 11025,  100; ...
        100, 22050,  100; ...
         20, 22050,  100; ...
         20, 44100,  100; ...
        100, 11025,   10; ...
        100, 11025, 1000; ...
        500, 80000,  200; ...
    };
    
    extra_inputs = { ...
        44100, [22050; 2205; 220]; ...
        16000, [8000; 7000; 6000; 5000; 4000; 3000; 2000; 1000]; ...
        16000, [16000; 8000; 1]; ...
    };
     
    num_tests = size(erb_space_inputs)(1) + size(extra_inputs)(1);
    
    erb_filter_inputs = {};
    
    erb_filter_results = {};
    
    % This will ONLY generate tests that use the centre frequency inputs
    
    % ERBSpace generated inputs
    for tnum=1:size(erb_space_inputs)(1)
        [f_low, f_high, num_f] = deal(erb_space_inputs{tnum,:});
        fs = f_high*2;
        cfs = ERBSpace(f_low, f_high, num_f);
        erb_filter_inputs(tnum, :) = {fs, cfs};
    end
    
    erb_filter_inputs = cat(1, erb_filter_inputs, extra_inputs);
    
    for tnum=1:num_tests
        fs = erb_filter_inputs{tnum, 1};
        cfs = erb_filter_inputs{tnum, 2};
        fcoefs = MakeERBFilters(fs, cfs, 0);
        erb_filter_results(tnum, :) = fcoefs;
    end

    results_file = fullfile('..', 'tests', 'data', 'test_erb_filter_data.mat');
    save(results_file, 'erb_filter_inputs', 'erb_filter_results');
end
