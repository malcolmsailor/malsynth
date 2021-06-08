import dataclasses
import numbers
import numpy as np
from scipy import signal


class PitchToHz:
    def __init__(self):
        self.two_pi = 2 * np.pi
        self._data = {}

    def __call__(self, pitch):
        """Technically doesn't return hz but instead hz * 2 * pi.

        Args:
            pitch: midinumber.
            phase: float, in radians
        """
        if pitch in self._data:
            return self._data[pitch]
        hz = pitch = 440.0 * (2 ** ((pitch - 69) / 12.0)) * (self.two_pi)
        self._data[pitch] = hz
        return hz


pitch_to_hz = PitchToHz()


@dataclasses.dataclass
class Oscillator:
    phase: numbers.Number = 0
    detune: numbers.Number = 0


class BaseSynth:
    """Base class for synths.

    Args:
        sample_rate: int.

    Keyword args:
        amp: max amplitude, float in interval [0, 1] Default 1.
        attack: duration of attack envelope. Default 0.005.
        decay: duration of decay envelope. Default 0.
        sustain: sustain amplitude as proportion of amp. Float in interval
            [0, 1]. If sustain != 1, then decay must be non-zero. Default: 1.
        release: duration of release envelope. Default 0.005.
        memoize_envelopes: when working with quantized data, the same
            note durations are likely to reoccur frequently (e.g., eighth-notes,
            quarter-notes, etc.). If this argument is True, then the envelopes
            for these durations will be memoized, which will save some
            calculation in the case of quantized data. With human performance
            or unquantized data, should probably be False.

    Methods:
        __call__()
    """

    min_amp = 0

    def __init__(
        self,
        sample_rate,
        oscillators=None,
        amp=1,
        attack=0.005,
        decay=0,
        sustain=1.0,
        release=0.005,
        memoize_envelopes=True,
    ):

        try:
            assert sustain == 1 or decay != 0
        except AssertionError:
            raise ValueError("`decay` must be non-zero if `sustain` is not 1")

        if oscillators is None:
            self.oscillators = (Oscillator(),)
        else:
            self.oscillators = oscillators
        attack_i = int(sample_rate * attack)
        decay_i = int(sample_rate * decay)
        self.sustain = sustain * amp
        self.attack_decay_i = attack_i + decay_i
        self.attack_envelope = np.concatenate(
            (
                np.linspace(self.min_amp, amp, attack_i),
                np.linspace(amp, self.sustain, decay_i),
            )
        )

        self.release_dur = release
        self.release_i = int(sample_rate * release)
        self.release_envelope = np.linspace(
            self.sustain, self.min_amp, self.release_i
        )

        self.sample_rate = sample_rate
        self.memoize_envelopes = memoize_envelopes
        if memoize_envelopes:
            self._envelopes = {}

    def __call__(self, t, out, pitch, note_onset, note_release, velocity=64):
        """Adds a synthesized note to out.

        The motivation for having the synth add to the output itself (rather
        than returning the waveform of the note and then doing as we like with
        it) is that the caller then doesn't have to keep track of how long
        the synth's `release_dur` is.

        Args:
            t: 'time' array, e.g., result of a call like `np.linspace(
                0, total_dur, int(math.ceil(total_dur) * sample_rate))`
            out: np array to which the note will be added.
            pitch: midi number. (Could be fractional to indicate tuning.)
            note_onset: time
            note_release: time

        Keyword args:
            velocity: 0--127, default 64

        Returns:
            None
        """
        start_i = np.searchsorted(t, note_onset)
        end_i = np.searchsorted(t, note_release + self.release_dur)
        x = t[start_i:end_i]
        x = self._synth(x, pitch)
        try:
            x = self._filter(x)
        except AttributeError:
            pass
        x = self._envelope(x)
        out[start_i:end_i] += x * velocity / 127

    def get_envelope(self, n):
        out = np.empty(n)
        if n >= self.attack_decay_i + self.release_i:
            out[: self.attack_decay_i] = self.attack_envelope
            out[self.attack_decay_i : -self.release_i] = self.sustain
            out[-self.release_i :] = self.release_envelope
        else:
            abbrev_i = n - self.release_i
            out[:abbrev_i] = self.attack_envelope[:abbrev_i]
            out[abbrev_i:] = np.linspace(out[abbrev_i - 1], 0, n - abbrev_i)
        if self.memoize_envelopes:
            self._envelopes[n] = out
        return out

    def _envelope(self, t):
        if self.memoize_envelopes and len(t) in self._envelopes:
            envelope = self._envelopes[len(t)]
        else:
            envelope = self.get_envelope(len(t))
        return t * envelope

    def _synth(self, t, pitch):
        osc = self.oscillators[0]
        out = self._waveform(t, pitch, phase=osc.phase, detune=osc.detune)
        for osc in self.oscillators[1:]:
            out += self._waveform(t, pitch, phase=osc.phase, detune=osc.detune)
        return out


class Sine(BaseSynth):
    @staticmethod
    def _waveform(t, pitch, phase=0, detune=0):
        return np.sin(t * pitch_to_hz(pitch + detune) + phase)


class Saw(BaseSynth):
    def __init__(self, *args, amp=0.3, **kwargs):
        super().__init__(*args, amp=amp, **kwargs)

    @staticmethod
    def _waveform(t, pitch, phase=0, detune=0):
        return signal.sawtooth(t * pitch_to_hz(pitch + detune) + phase)


class Square(BaseSynth):
    def __init__(self, *args, amp=0.3, **kwargs):
        super().__init__(*args, amp=amp, **kwargs)

    @staticmethod
    def _waveform(t, pitch, phase=0, detune=0):
        return signal.square(t * pitch_to_hz(pitch + detune) + phase)


# after https://stackoverflow.com/a/25192640/10155119
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff)
    return b, a


class FilteredSynth(BaseSynth):
    def __init__(self, *args, cutoff=440, order=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.cutoff = cutoff
        self.order = order
        self.b, self.a = butter_lowpass(cutoff, self.sample_rate, self.order)

    def _filter(self, t):
        y = signal.filtfilt(self.b, self.a, t)
        return y


class FollowFilterSynth(BaseSynth):
    def __init__(self, *args, factor=0.5, order=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.factor = factor
        self.order = order

    def _filter(self, t, pitch):
        cutoff = pitch_to_hz(pitch) * self.factor
        b, a = butter_lowpass(cutoff, self.sample_rate, self.order)
        y = signal.filtfilt(b, a, t)
        return y

    def __call__(self, t, out, pitch, note_onset, note_release, velocity=64):
        # the only reason we have to override __call__ is because we need to
        # call self._filter(x, pitch) rather than self._filter(x)
        start_i = np.searchsorted(t, note_onset)
        end_i = np.searchsorted(t, note_release + self.release_dur)
        x = t[start_i:end_i]
        x = self._synth(x, pitch)
        try:
            x = self._filter(x, pitch)
        except AttributeError:
            pass
        x = self._envelope(x)
        out[start_i:end_i] += x * velocity / 127


class FilteredSaw(Saw, FilteredSynth):
    def __init__(self, *args, amp=1.0, **kwargs):
        super().__init__(*args, amp=amp, **kwargs)


class FollowSaw(Saw, FollowFilterSynth):
    """A saw wave with a filter that 'follows' the pitch of the note.

    Keyword args:
        factor: cutoff frequency will be the frequency of the note, multiplied
            by this factor. E.g., if the note is A440, and factor = 0.5, the
            cutoff will be 220; if factor = 2, it will be 880.
            Default: 0.5.
    """

    def __init__(self, *args, amp=0.6, **kwargs):
        super().__init__(*args, amp=amp, **kwargs)


class FilteredSquare(Square, FilteredSynth):
    def __init__(self, *args, amp=1.0, **kwargs):
        super().__init__(*args, amp=amp, **kwargs)


class FollowSquare(Square, FollowFilterSynth):
    def __init__(self, *args, amp=0.6, **kwargs):
        super().__init__(*args, amp=amp, **kwargs)


# Commented out class below is an attempt to create a filter with a dynamic
#   envelope. Doesn't seem to work, yet anyway.
# class FilteredSaw2(Saw):
#     def __init__(
#         self,
#         *args,
#         filter_decay=0.25,
#         start_cutoff=5000,
#         stop_cutoff=200,
#         **kwargs
#     ):
#         super().__init__(*args, **kwargs)
#         self.start_cutoff = start_cutoff
#         self.stop_cutoff = stop_cutoff
#         self.filter_decay = filter_decay
#         # self.b, self.a = butter_lowpass(cutoff, self.sample_rate)

#     def _filter(self, t):
#         window_length = 50
#         window = np.hanning(window_length)
#         out = np.empty_like(t)
#         n_steps = math.floor(len(t) / window_length)
#         # for i in range(0, len(t) - window_length, window_length):
#         cutoff_step_size = (self.start_cutoff - self.stop_cutoff) / n_steps
#         for j in range(0, n_steps):
#             cutoff = self.start_cutoff - j * cutoff_step_size
#             start_i, end_i = j * window_length, min(
#                 (j + 1) * window_length, len(t)
#             )
#             b, a = butter_lowpass(cutoff, self.sample_rate)
#             out[start_i:end_i] = signal.filtfilt(
#                 b, a, t[start_i:end_i] * window[: end_i - start_i]
#             )
#         return out
