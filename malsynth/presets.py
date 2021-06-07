import types
from .base import (
    Oscillator,
    Sine,
    Saw,
    Square,
    FollowSaw,
    FollowSquare,
    FilteredSynth,
    FilteredSaw,
    FilteredSquare,
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
    def __init__(self, *args, amp=0.3, detune=0.15, **kwargs):
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
    def __init__(self, *args, decay=0.1, sustain=0.2, **kwargs):
        super().__init__(*args, decay=decay, sustain=sustain, **kwargs)


class ShortDoubleSaw(DoubleSaw):
    def __init__(self, *args, amp=0.4, decay=0.3, sustain=0, **kwargs):
        super().__init__(*args, amp=amp, decay=decay, sustain=sustain, **kwargs)


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
    def __init__(self, *args, amp=0.8, decay=0.2, sustain=0, **kwargs):
        super().__init__(*args, amp=amp, decay=decay, sustain=sustain, **kwargs)


class ShortDoubleFollowSquare(DoubleFollowSquare):
    def __init__(self, *args, amp=0.7, decay=0.15, sustain=0, **kwargs):
        super().__init__(*args, amp=amp, decay=decay, sustain=sustain, **kwargs)


class FilteredDoubleSaw(DoubleSaw, FilteredSynth):
    def __init__(self, *args, amp=0.3, order=3, cutoff=2500, **kwargs):
        super().__init__(*args, amp=amp, order=order, cutoff=cutoff, **kwargs)


SYNTHS = {
    0: Sine,
    1: Saw,
    2: Square,
    3: FilteredSaw,
    4: FollowSaw,
    5: FilteredSquare,
    6: FollowSquare,
    7: FilteredDoubleSaw,
    8: DoubleFollowSaw,
    9: DoubleFollowSquare,
    10: ShortDoubleFollowSaw,
    11: ShortDoubleFollowSquare,
    12: DoubleSaw,
    13: DoubleSquare,
    14: TripleSine,
    15: ShortSine,
    16: ShortSaw,
    17: ShortSquare,
    18: ShortDoubleSaw,
}

synths = types.MappingProxyType(SYNTHS)
