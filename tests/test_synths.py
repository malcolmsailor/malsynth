import os
import sys
import traceback
import wave

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import malsynth

SAMPLE_RATE = 44100


def test_envelope():
    # I wrote these tests while trying to debug the source of some pops and
    #   clicks. They are pretty elementary, but harmless!
    attack_dur = 0.005
    decay_dur = 0.05
    amp = 1
    base_synth = malsynth.Sine(
        SAMPLE_RATE, attack=attack_dur, decay=decay_dur, sustain=0.5, amp=amp
    )
    try:
        for n in [450, 12395, 23, 128]:
            # we add the length of the release to the length of the note,
            # as is done in BaseSynth.__call__()
            n += base_synth.release_i
            envelope = base_synth.get_envelope(n)
            attack_i = int(base_synth.sample_rate * attack_dur)
            if n >= base_synth.attack_decay_i + base_synth.release_i:
                assert envelope[0] == base_synth.min_amp
                assert envelope[attack_i - 1] == amp
                assert envelope[attack_i] == amp
                assert (
                    envelope[base_synth.attack_decay_i - 1]
                    == base_synth.sustain
                )
                assert envelope[-base_synth.release_i] == base_synth.sustain
                assert envelope[-1] == base_synth.min_amp
                for i, j in zip(envelope, envelope[1:]):
                    assert abs(i - j) < 10e-2
            else:
                abbrev_i = n - base_synth.release_i
                assert envelope[0] == base_synth.min_amp
                assert envelope[-1] == base_synth.min_amp
                if abbrev_i > attack_i:
                    assert envelope[attack_i - 1] == amp
                    assert envelope[attack_i] == amp
                assert envelope[abbrev_i - 1] == envelope[abbrev_i]
                for i, j in zip(envelope, envelope[1:]):
                    assert abs(i - j) < 10e-2

    except:  # pylint: disable=bare-except

        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(
            exc_type, exc_value, exc_traceback, file=sys.stdout
        )
        breakpoint()


def write_mono_wav(np_array, out_path_or_f, sample_rate):
    audio = (np_array * (2 ** 15 - 1)).astype("<h")
    with wave.open(out_path_or_f, "wb") as f:
        # 2 Channels.
        f.setnchannels(1)
        # 2 bytes per sample.
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio.tobytes())


if __name__ == "__main__":
    test_envelope()
