Gammatone Filterbank Toolkit
============================

Jason Heeris, 2013

Summary
-------

This is a port of Malcolm Slaney's and Dan Ellis' gammatone filterbank MATLAB
code, detailed below, to Python 3 using Numpy and Scipy.

Using the Code
--------------

At the moment there are only library functions (ie. no CLI entry points). The
module is named `gammatone`.

```python3
from matplotlib import pyplot as plt
import numpy as np

from gammatone import gtgram

# 48kHz sampling rate
fs = 48000
ts = np.linspace(0, 1, num=fs, endpoint=False)

# 220Hz sine wave modulated by +/- 40 Hz
cfreq = 220
mfreq = 40
modulated = np.cos(2 * np.pi * mfreq * ts)
signal = np.cos(2 * np.pi * cfreq * ts + modulated)

# Gammatone-based spectrogram
twin = 0.008
thop = twin/2
channels = 256
fmin = 20
fmax = fs/2

gtg = gtgram(signal, fs, twin, thop, channels, fmin, fmax)
Z = np.flipud(20 * np.log10(gtg))
plt.imshow(Z)
plt.show()
```

Basis
-----

This project is based on research into how humans perceive audio, originally
published by Malcolm Slaney:

[Malcolm Slaney (1998) "Auditory Toolbox Version 2", Technical Report #1998-010,
Interval Research Corporation, 1998.][slaney-1998]

[slaney-1998] : http://cobweb.ecn.purdue.edu/~malcolm/interval/1998-010/

Slaney's report describes a way of modelling how the human ear perceives,
emphasises and separates different frequencies of sound. A series of gammatone
filters are constructed whose width increases with increasing centre frequency,
and this bank of filters is applied to a time-domain signal. The result of this
is a spectrum that should represent the human experience of sound better than,
say, a Fourier-domain spectrum would.

A gammatone filter has an impulse response that is a sine wave multiplied by a
gamma distribution function. It is a common approach to modelling the auditory
system.

The gammatone filterbank approach can be considered analogous (but not
equivalent) to a discrete Fourier transform where the frequency axis is
logarithmic. For example, a series of notes spaced an octave apart would appear
to be roughly linearly spaced; or a sound that was distributed across the same
linear frequency range would appear to have more spread at lower frequencies.

The real goal of this toolkit is to allow easy computation of the gammatone
equivalent of a spectrogram — a time-varying spectrum of energy over audible
frequencies based on a gammatone filterbank.

Slaney demonstrated his research with an initial implementation in MATLAB. This
implementation was later extended by Dan Ellis, who found a way to approximate a
"gammatone-gram" by using the fast Fourier transform. Ellis' code calculates a
matrix of weights that can be applied to the output of a FFT so that a
Fourier-based spectrogram can easily be transformed into such an approximation.

Ellis' code and documentation is here: [Gammatone-like spectrograms][ellis-2009]

[ellis-2009] : http://labrosa.ee.columbia.edu/matlab/gammatonegram/

Interest
--------

I became interested in this because of my background in science communication
and my general interest in the teaching of signal processing. I find that the
spectrogram approach to visualising signals is adequate for illustrating
abstract systems or the mathematical properties of transforms, but bears little
correspondence to a person's own experience of sound. If someone wants to see
what their favourite piece of music "looks like," a normal Fourier transform
based spectrogram is actually quite a poor way to visualise it. Features of the
audio seem to be oddly spaced or unnaturally emphasised or de-emphasised
depending on where they are in the frequency domain.

The gammatone filterbank approach seems to be closer to what someone might
intuitively expect a visualisation of sound to look like, and can help develop
an intuition about alternative representations of signals.
