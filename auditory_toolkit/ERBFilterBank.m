function output = ERBFilterBank(x, fcoefs)
% function output = ERBFilterBank(x, fcoefs)
% Process an input waveform with a gammatone filter bank. This function 
% takes a single sound vector, and returns an array of filter outputs, one 
% channel per row.
%
% The fcoefs parameter, which completely specifies the Gammatone filterbank,
% should be designed with the MakeERBFilters function.  If it is omitted,
% the filter coefficients are computed for you assuming a 22050Hz sampling
% rate and 64 filters regularly spaced on an ERB scale from fs/2 down to 100Hz.
%

% Malcolm Slaney @ Interval, June 11, 1998.
% (c) 1998 Interval Research Corporation  
% Thanks to Alain de Cheveigne' for his suggestions and improvements.

if nargin < 1
	error('Syntax: output_array = ERBFilterBank(input_vector[, fcoefs]);');
end

if nargin < 2
	fcoefs = MakeERBFilters(22050,64,100);
end

if size(fcoefs,2) ~= 10
	error('fcoefs parameter passed to ERBFilterBank is the wrong size.');
end

if size(x,2) < size(x,1)
	x = x';
end

A0  = fcoefs(:,1);
A11 = fcoefs(:,2);
A12 = fcoefs(:,3);
A13 = fcoefs(:,4);
A14 = fcoefs(:,5);
A2  = fcoefs(:,6);
B0  = fcoefs(:,7);
B1  = fcoefs(:,8);
B2  = fcoefs(:,9);
gain= fcoefs(:,10);	

output = zeros(size(gain,1), length(x));
for chan = 1: size(gain,1)
	y1=filter([A0(chan)/gain(chan) A11(chan)/gain(chan) ...
		   A2(chan)/gain(chan)], ...
				[B0(chan) B1(chan) B2(chan)], x);
	y2=filter([A0(chan) A12(chan) A2(chan)], ...
				[B0(chan) B1(chan) B2(chan)], y1);
	y3=filter([A0(chan) A13(chan) A2(chan)], ...
				[B0(chan) B1(chan) B2(chan)], y2);
	y4=filter([A0(chan) A14(chan) A2(chan)], ...
				[B0(chan) B1(chan) B2(chan)], y3);
	output(chan, :) = y4;
end

if 0
	semilogx((0:(length(x)-1))*(fs/length(x)),20*log10(abs(fft(output))));
end
