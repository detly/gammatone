% Copyright 2014 Jason Heeris, jason.heeris@gmail.com
% 
% This file is part of the gammatone toolkit, and is licensed under the 3-clause
% BSD license: https://github.com/detly/gammatone/blob/master/COPYING
function test_gammatonegram()
    % Need:
    %  wave
    %  fs
    %  window_time
    %  hop_time
    %  channels
    %  f_min
    %  f_max
    
    % Need to mock out:
    %  make_erb_filters output (elide)
    %  centre_freqs (elide)
    %  erb_filterbank (depends on X, SR, N, FMIN)
    
    % Ensure reproducible tests
    rand('state', [3 1 4 1 5 9 2 7]);
    
    gammatonegram_inputs = {
        'sawtooth_01', sawtooth(2*pi*10100*[0:22050 - 1]'/22050, 0.5), 22050, 0.025, 0.010, 64, 50; ...
        'sin220_01'  , sin(2*pi*220*[0:4800 - 1]'/48000), 48000, 0.01, 0.01, 64, 50; ...
        'sin220_02'  , sin(2*pi*220*[0:4800 - 1]'/48000), 48000, 0.025, 0.01, 32, 50; ...
        'rand_01'    , rand([1, 4410 - 1]), 44100, 0.02, 0.015, 128, 500; ...
        'rand_02'    , rand([1, 9600 - 1]), 96000, 0.01, 0.005, 256, 20; ...
        'rand_03'    , rand([1, 4800 - 1]), 48000, 0.01, 0.010, 256, 20; ...
    };
    
    % Mocked intermediate results for unit testing
    gammatonegram_mocks = {};
    
    % Actual results
    gammatonegram_results = {};
    
    for tnum=1:size(gammatonegram_inputs)(1)
        [name, wave, fs, twin, thop, chs, fmin] = deal(gammatonegram_inputs{tnum,:});
        res = gammatonegram( ...
                  wave, ...
                  fs, ...
                  twin, ...
                  thop, ...
                  chs, ...
                  fmin, ...
                  0, % fmax is ignored
                  0 % Don't use FFT method
              );
    
        % This is for mocking the output of the equivalent Python functions
        nwin     = round(twin * fs);    
        hopsamps = round(thop * fs);
        f_coefs  = flipud(MakeERBFilters(fs, chs, fmin));
        x_f      = ERBFilterBank(wave, f_coefs);
        x_e      = [x_f .^ 2];
        x_e_cols = size(x_e, 2);
        ncols    = 1 + floor((x_e_cols - nwin) / hopsamps);
       
        % Mock out the ERB filter functions too
        fcoefs = flipud(MakeERBFilters(fs, chs, fmin));
        erb_fb_output = ERBFilterBank(wave, fcoefs);
    
        gammatonegram_mocks(tnum, :) = { ...
            erb_fb_output, ...
            x_e_cols ...
        };
    
        gammatonegram_results(tnum, :) = { ...
            res, ...
            nwin, ...
            hopsamps, ...
            ncols ...
        };
    
    end;
    
    results_file = fullfile('..', 'tests', 'data', 'test_gammatonegram_data.mat');
    save(results_file, 'gammatonegram_inputs', 'gammatonegram_mocks', 'gammatonegram_results');
end;
