function cfArray = ERBSpace(lowFreq, highFreq, N)
% function cfArray = ERBSpace(lowFreq, highFreq, N)
% This function computes an array of N frequencies uniformly spaced between
% highFreq and lowFreq on an ERB scale.  N is set to 100 if not specified.
%
% See also linspace, logspace, MakeERBCoeffs, MakeERBFilters.
%
% For a definition of ERB, see Moore, B. C. J., and Glasberg, B. R. (1983).
% "Suggested formulae for calculating auditory-filter bandwidths and
% excitation patterns," J. Acoust. Soc. Am. 74, 750-753.

if nargin < 1
	lowFreq = 100;
end

if nargin < 2
	highFreq = 44100/4;
end

if nargin < 3
	N = 100;
end

% Change the following three parameters if you wish to use a different
% ERB scale.  Must change in MakeERBCoeffs too.
EarQ = 9.26449;				%  Glasberg and Moore Parameters
minBW = 24.7;
order = 1;

% All of the followFreqing expressions are derived in Apple TR #35, "An
% Efficient Implementation of the Patterson-Holdsworth Cochlear
% Filter Bank."  See pages 33-34.
cfArray = -(EarQ*minBW) + exp((1:N)'*(-log(highFreq + EarQ*minBW) + ...
		log(lowFreq + EarQ*minBW))/N) * (highFreq + EarQ*minBW);

