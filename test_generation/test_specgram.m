% Copyright 2014 Jason Heeris, jason.heeris@gmail.com
% 
% This file is part of the gammatone toolkit, and is licensed under the 3-clause
% BSD license: https://github.com/detly/gammatone/blob/master/COPYING
function test_specgram()
    % Need:
    %  wave
    %  nfft
    %  fs
    %  window_size
    %  hop (technically the function takes the overlap, but only to recalculate this)
    
    % Ensure reproducible tests
    rand('state', [3 1 4 1 5 9 2 7]);
    
    specgram_inputs = {
        'sawtooth_01', sawtooth(2*pi*10100*[0:22050 - 1]'/22050, 0.5), 2048, 22050, 551, 221; ...
        'sin220_01'  , sin(2*pi*220*[0:4800 - 1]'/48000), 1024, 48000, 480, 480; ...
        'sin220_02'  , sin(2*pi*220*[0:4800 - 1]'/48000), 4096, 48000, 1200, 480; ...
        'rand_01'    , rand([1, 4410 - 1]), 2048, 44100, 882, 662; ...
        'rand_02'    , rand([1, 9600 - 1]), 2048, 96000, 960, 480; ...
        'rand_03'    , rand([1, 4800 - 1]), 1024, 48000, 480, 480; ...
    };
    
    % Mocked intermediate results for unit testing
    specgram_mocks = {};
    
    % Actual results
    specgram_results = {};
    
    for tnum=1:size(specgram_inputs)(1)
        [name, wave, nfft, fs, nwin, nhop] = deal(specgram_inputs{tnum,:});

        % Mock out windowing function
        window = gtgram_window(nfft, nwin);

        res = specgram( ...
            wave, ...
            nfft, ...
            fs, ...
            nwin, ...
            nwin - nhop ...
        );
        
        specgram_mocks(tnum, :) = { ...
            window, ...
        };
    
        specgram_results(tnum, :) = { ...
            res, ...
        };
    
    end;
    
    results_file = fullfile('..', 'tests', 'data', 'test_specgram_data.mat');
    save(results_file, 'specgram_inputs', 'specgram_mocks', 'specgram_results');
end;


function win = gtgram_window(n, w)
    % Reproduction of Dan Ellis' windowing function built in to specgram.m
    halflen = w/2;
    halff = n/2;   % midpoint of win
    acthalflen = min(halff, halflen);

    halfwin = 0.5 * ( 1 + cos( pi * (0:halflen)/halflen));
    win = zeros(1, n);
    win((halff+1):(halff+acthalflen)) = halfwin(1:acthalflen);
    win((halff+1):-1:(halff-acthalflen+2)) = halfwin(1:acthalflen);
end;