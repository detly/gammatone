% Copyright 2014 Jason Heeris, jason.heeris@gmail.com
% 
% This file is part of the gammatone toolkit, and is licensed under the 3-clause
% BSD license: https://github.com/detly/gammatone/blob/master/COPYING
function test_fft_gammatonegram()
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
    
    fft_gammatonegram_inputs = {
        'sawtooth_01', sawtooth(2*pi*10100*[0:22050 - 1]'/22050, 0.5), 22050, 0.025, 0.010, 64, 50; ...
        'sin220_01'  , sin(2*pi*220*[0:4800 - 1]'/48000), 48000, 0.01, 0.01, 64, 50; ...
        'sin220_02'  , sin(2*pi*220*[0:4800 - 1]'/48000), 48000, 0.025, 0.01, 32, 50; ...
        'rand_01'    , rand([1, 4410 - 1]), 44100, 0.02, 0.015, 128, 500; ...
        'rand_02'    , rand([1, 9600 - 1]), 96000, 0.01, 0.005, 256, 20; ...
        'rand_03'    , rand([1, 4800 - 1]), 48000, 0.01, 0.010, 256, 20; ...
    };
    
    % Mocked intermediate results for unit testing
    fft_gammatonegram_mocks = {};
    
    % Actual results
    fft_gammatonegram_results = {};
    
    for tnum=1:size(fft_gammatonegram_inputs)(1)
        [name, wave, fs, twin, thop, chs, fmin] = deal(fft_gammatonegram_inputs{tnum,:});

        % This is for mocking the output of the equivalent Python functions
        nfft = 2^(ceil(log(2*twin*fs)/log(2)));
        nwin = round(twin * fs);    
        nhop = round(thop * fs);
        
        % Mock out the FFT weights as well
        wts = fft2gammatonemx( ...
            nfft, ...
            fs, ...
            chs, ...
            1, ... % width is always 1 in the Python implementation
            fmin, ...
            fs/2, ...
            nfft/2+1 ...
        );

        % Mock out windowing function
        window = gtgram_window(nfft, nwin);

        res = gammatonegram( ...
            wave, ...
            fs, ...
            twin, ...
            thop, ...
            chs, ...
            fmin, ...
            fs/2, % fmax is always fs/2 in the Python version
            1     % Use FFT method
        );
        
        fft_gammatonegram_mocks(tnum, :) = { ...
            wts ...
        };
    
        fft_gammatonegram_results(tnum, :) = { ...
            res, ...
            window, ...
            nfft, ...
            nwin, ...
            nhop ...
        };
    
    end;
    
    results_file = fullfile('..', 'tests', 'data', 'test_fft_gammatonegram_data.mat');
    save(results_file, 'fft_gammatonegram_inputs', 'fft_gammatonegram_mocks', 'fft_gammatonegram_results');
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