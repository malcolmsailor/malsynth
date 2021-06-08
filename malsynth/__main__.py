import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

from . import synths

SAMPLE_RATE = 44100


def welcome():
    welcome_str = "malsynth demo"
    print(welcome_str)
    print("-" * len(welcome_str))
    print()


def input_loop():
    for i, synth in synths.items():
        print(f"{i:>3}: {synth.__name__}")
    print(f"{len(synths):>3}: Play all synths")
    while True:
        a = input(
            "\nEnter the number corresponding to the synth you would like to "
            "hear ('q' to quit): "
        ).strip()
        if a == "q":
            return None
        if a == str(len(synths)):
            return list(synths.values())
        try:
            return synths[int(a)]
        except (TypeError, ValueError):
            print("Invalid input, try again.")


def write_mono_wav(np_array, out_path_or_f, sample_rate):
    audio = (np_array * (2 ** 15 - 1)).astype("<h")
    with wave.open(out_path_or_f, "wb") as f:
        # 2 Channels.
        f.setnchannels(1)
        # 2 bytes per sample.
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio.tobytes())


def play(synth_cls, wav_path):
    synth = synth_cls(SAMPLE_RATE)
    # pitch, dur, wait
    loop = [
        (60, 1, 1),
        (65, 0.5, 0.5),
        (67, 0.25, 0.25),
        (72, 0.25, 0.25),
        (48, 0.25, 0.5),
        (58, 0.25, 0.5),
        (60, 0.125, 0.25),
        (72, 0.125, 0.25),
    ]
    total_dur = sum(inc for _, _, inc in loop) + 1
    t = np.linspace(
        0, total_dur, int(math.ceil(total_dur * SAMPLE_RATE)), False
    )
    out = np.zeros_like(t)
    now = 0
    for pitch, dur, increment in loop:
        synth(t, out, pitch, now, now + dur)
        now += increment
    # to avoid overflow
    out /= 1.1

    write_mono_wav(out, wav_path, SAMPLE_RATE)
    print(f"Playing {type(synth).__name__} (ctrl-C to interrupt playback)")
    subprocess.run(["afplay", wav_path], check=True)


def demo():
    welcome()
    while True:
        synth = input_loop()
        if synth is None:
            sys.exit()

        _, wav_path = tempfile.mkstemp(suffix=".wav")
        try:
            if isinstance(synths := synth, list):
                for synth_ in synths:
                    play(synth_, wav_path)
            else:
                play(synth, wav_path)
        except KeyboardInterrupt:
            pass
        os.remove(wav_path)
        print("")


if __name__ == "__main__":
    demo()
