import types

from .base import (
    FilteredSaw,
    FilteredSquare,
    FilteredSynth,
    FollowSaw,
    FollowSquare,
    Noise,
    Oscillator,
    Saw,
    Sine,
    Square,
)


class DoubleSaw(Saw):
    def __init__(self, *args, amp=0.2, detune=0.1, **kwargs):
        super().__init__(
            *args,
            amp=amp,
            oscillators=[Oscillator(), Oscillator(detune=detune)],
            **kwargs
        )


class DoubleSquare(Square):
    def __init__(self, *args, amp=0.2, detune=0.25, **kwargs):
        super().__init__(
            *args,
            amp=amp,
            oscillators=[Oscillator(), Oscillator(detune=detune)],
            **kwargs
        )


class TripleSine(Sine):
    def __init__(self, *args, amp=0.5, detune=0.15, **kwargs):
        super().__init__(
            *args,
            amp=amp,
            oscillators=[
                Oscillator(),
                Oscillator(detune=detune),
                Oscillator(detune=-detune),
            ],
            **kwargs
        )


class ShortSine(Sine):
    def __init__(self, *args, decay=0.15, sustain=0, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, **kwargs)


class ShortSaw(Saw):
    def __init__(self, *args, decay=0.2, sustain=0, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, **kwargs)


class ShortSquare(Square):
    def __init__(self, *args, decay=0.1, sustain=0, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, **kwargs)


class ShortFollowSaw(FollowSaw):
    def __init__(self, *args, decay=0.1, sustain=0, release=0.1, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, release=release, **kwargs)


class ShortFollowSquare(FollowSquare):
    def __init__(self, *args, decay=0.1, sustain=0, release=0.1, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, release=release, **kwargs)


class ShortDoubleSaw(DoubleSaw):
    def __init__(self, *args, amp=0.4, decay=0.3, sustain=0, release=0.15, **kwargs):
        super().__init__(
            *args, amp=amp, decay=decay, sustain=sustain, release=release, **kwargs
        )


class DoubleFollowSaw(FollowSaw):
    def __init__(self, *args, factor=0.75, detune=0.1, **kwargs):
        super().__init__(
            *args,
            oscillators=[Oscillator(), Oscillator(detune=detune)],
            factor=factor,
            **kwargs
        )


class DoubleFollowSquare(FollowSquare):
    def __init__(self, *args, amp=0.3, factor=1.5, detune=0.1, **kwargs):
        super().__init__(
            *args,
            amp=amp,
            oscillators=[Oscillator(), Oscillator(detune=detune)],
            factor=factor,
            **kwargs
        )


class ShortDoubleFollowSaw(DoubleFollowSaw):
    def __init__(self, *args, amp=0.8, decay=0.2, sustain=0, release=0.15, **kwargs):
        super().__init__(
            *args, amp=amp, decay=decay, sustain=sustain, release=release, **kwargs
        )


class ShortDoubleFollowSquare(DoubleFollowSquare):
    def __init__(self, *args, amp=0.7, decay=0.15, sustain=0, release=0.15, **kwargs):
        super().__init__(
            *args, amp=amp, decay=decay, sustain=sustain, release=release, **kwargs
        )


class ShortTripleSine(TripleSine):
    def __init__(self, *args, decay=0.15, sustain=0, release=0.08, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, release=release, **kwargs)


class FilteredDoubleSaw(DoubleSaw, FilteredSynth):
    def __init__(self, *args, amp=0.3, order=3, cutoff=2500, **kwargs):
        super().__init__(*args, amp=amp, order=order, cutoff=cutoff, **kwargs)


class ShortNoise(Noise):
    def __init__(self, *args, decay=0.1, sustain=0, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, **kwargs)


class FilteredShortNoise(Noise, FilteredSynth):
    def __init__(self, *args, decay=0.1, sustain=0, order=3, cutoff=4000, **kwargs):
        super().__init__(
            *args, decay=decay, sustain=sustain, order=order, cutoff=cutoff, **kwargs
        )


SYNTH_LIST = [
    Sine,
    Saw,
    Square,
    FilteredSaw,
    FollowSaw,
    FilteredSquare,
    FollowSquare,
    FilteredDoubleSaw,
    DoubleFollowSaw,
    DoubleFollowSquare,
    DoubleSaw,
    DoubleSquare,
    TripleSine,
    ShortSine,
    ShortSaw,
    ShortSquare,
    ShortFollowSaw,
    ShortFollowSquare,
    ShortDoubleSaw,
    ShortDoubleFollowSaw,
    ShortDoubleFollowSquare,
    ShortTripleSine,
    Noise,
    ShortNoise,
    FilteredShortNoise,
]

SYNTHS = {i: synth for (i, synth) in enumerate(SYNTH_LIST)}


synths = types.MappingProxyType(SYNTHS)
synths = types.MappingProxyType(SYNTHS)
