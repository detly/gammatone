function [Y,F] = gammatonegram(X,SR,TWIN,THOP,N,FMIN,FMAX,USEFFT,WIDTH)
% [Y,F] = gammatonegram(X,SR,N,TWIN,THOP,FMIN,FMAX,USEFFT,WIDTH)
%    Calculate a spectrogram-like time frequency magnitude array
%    based on Gammatone subband filters.  Waveform X (at sample
%    rate SR) is passed through an N (default 64) channel gammatone 
%    auditory model filterbank, with lowest frequency FMIN (50) 
%    and highest frequency FMAX (SR/2).  The outputs of each band 
%    then have their energy integrated over windows of TWIN secs 
%    (0.025), advancing by THOP secs (0.010) for successive
%    columns.  These magnitudes are returned as an N-row
%    nonnegative real matrix, Y.
%    If USEFFT is present and zero, revert to actual filtering and
%    summing energy within windows.
%    WIDTH (default 1.0) is how to scale bandwidth of filters 
%    relative to ERB default (for fast method only).
%    F returns the center frequencies in Hz of each row of Y
%    (uniformly spaced on a Bark scale).
%
% 2009-02-18 DAn Ellis dpwe@ee.columbia.edu
% Last updated: $Date: 2009/02/23 21:07:09 $

if nargin < 2;  SR = 16000; end
if nargin < 3;  TWIN = 0.025; end
if nargin < 4;  THOP = 0.010; end
if nargin < 5;  N = 64; end
if nargin < 6;  FMIN = 50; end
if nargin < 7;  FMAX = SR/2; end
if nargin < 8;  USEFFT = 1; end
if nargin < 9;  WIDTH = 1.0; end


if USEFFT == 0 

  % Use malcolm's function to filter into subbands
  %%%% IGNORES FMAX! *****
  [fcoefs,F] = MakeERBFilters(SR, N, FMIN);
  fcoefs = flipud(fcoefs);

  XF = ERBFilterBank(X,fcoefs);

  nwin = round(TWIN*SR);
% Always use rectangular window for now
%  if USEHANN == 1
    window = hann(nwin)';
%  else
%    window = ones(1,nwin);
%  end
%  window = window/sum(window);
%  XE = [zeros(N,round(nwin/2)),XF.^2,zeros(N,round(nwin/2))];
  XE = [XF.^2];

  hopsamps = round(THOP*SR);

  ncols = 1 + floor((size(XE,2)-nwin)/hopsamps);

  Y = zeros(N,ncols);

%  winmx = repmat(window,N,1);

  for i = 1:ncols
%    Y(:,i) = sqrt(sum(winmx.*XE(:,(i-1)*hopsamps + [1:nwin]),2));
    Y(:,i) = sqrt(mean(XE(:,(i-1)*hopsamps + [1:nwin]),2));
  end

else 
  % USEFFT version
  % How long a window to use relative to the integration window requested
  winext = 1;
  twinmod = winext * TWIN;
  % first spectrogram
  nfft = 2^(ceil(log(2*twinmod*SR)/log(2)));
  nhop = round(THOP*SR);
  nwin = round(twinmod*SR);
  [gtm,F] = fft2gammatonemx(nfft, SR, N, WIDTH, FMIN, FMAX, nfft/2+1);
  % perform FFT and weighting in amplitude domain
  Y = 1/nfft*gtm*abs(specgram(X,nfft,SR,nwin,nwin-nhop));
  % or the power domain?  doesn't match nearly as well
  %Y = 1/nfft*sqrt(gtm*abs(specgram(X,nfft,SR,nwin,nwin-nhop).^2));
end



