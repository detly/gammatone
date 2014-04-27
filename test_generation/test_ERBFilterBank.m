% Copyright 2014 Jason Heeris, jason.heeris@gmail.com
% 
% This file is part of the gammatone toolkit, and is licensed under the 3-clause
% BSD license: https://github.com/detly/gammatone/blob/master/COPYING
function test_ERBFilterBank()

    erb_space_inputs = { ...
        100, 11025,  10, sin(2*pi*220*[0:22050/100]'/22050); ...
         20, 22050,  10, square(2*pi*150*[0:44100/200]'/44100); ...
         20, 44100,  40, square(2*pi*12000*[0:88200/400]'/88200); ...
        100, 11025, 1000, sawtooth(2*pi*10100*[0:22050/100]'/22050, 0.5); ...
        500, 80000,  200, sawtooth(2*pi*3333*[0:160000/400]'/160000, 0.5); ...
    };
    
    erb_filter_inputs = { ...
        44100, [22050; 2205; 220], square(2*pi*220*[0:44100/200]'/44100); ...
        16000, [8000; 7000; 6000; 5000; 4000; 3000; 2000; 1000], square(2*pi*2000*[0:16000/50]'/16000); ...
        16000, [16000; 8000; 1], square(2*pi*880*[0:16000/50]'/16000); ...
    };
    
    num_tests = size(erb_space_inputs)(1) ...
                + size(erb_filter_inputs)(1);
    
    erb_filterbank_inputs = {};
    
    erb_filterbank_results = {};
    
    % This will ONLY generate tests that use the centre frequency inputs
    
    % ERBSpace generated inputs
    for tnum=1:size(erb_space_inputs)(1)
        [f_low, f_high, num_f, wave] = deal(erb_space_inputs{tnum,:});
        fs = f_high*2;
        f_arr = ERBSpace(f_low, f_high, num_f);
        fcoefs = MakeERBFilters(fs, f_arr, 0);
        erb_filterbank_inputs(tnum, :) = {fcoefs, wave};
    end
    
    % MakeERBFilters generated inputs
    for tnum=1:size(erb_filter_inputs)
        [fs, f_arr, wave] = deal(erb_filter_inputs{tnum,:});
        fcoefs = MakeERBFilters(fs, f_arr, 0);
        offset = size(erb_space_inputs)(1);
        erb_filterbank_inputs(offset+tnum, :) = {fcoefs, wave};
    end
    
    for tnum=1:num_tests
        fcoefs = erb_filterbank_inputs{tnum, 1};
        wave = erb_filterbank_inputs{tnum, 2};
        erb_filterbank_results(tnum, :) = ERBFilterBank(wave, fcoefs);
    end

    results_file = fullfile('..', 'tests', 'data', 'test_filterbank_data.mat');
    save(results_file, 'erb_filterbank_inputs', 'erb_filterbank_results');
end
