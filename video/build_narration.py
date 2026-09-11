"""Build a two-speaker English narration with open-weight speech synthesis.

This optional production helper never runs in the daily literature monitor.
It uses standard Kokoro voices, not recordings or clones of identifiable people.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "video" / "output"
SR = 24000


def main() -> None:
    torch.set_num_threads(2)
    torch.manual_seed(17)
    OUT.mkdir(parents=True, exist_ok=True)
    script = json.loads((ROOT / "video" / "narration.json").read_text())
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cpu")
    voices = {"male": ("am_michael", 0.94), "female": ("af_heart", 1.03)}
    timings = []
    audio_parts = [np.zeros(int(SR * 1.0), dtype=np.float32)]
    clock = 1.0
    for index, line in enumerate(script["lines"]):
        voice, speed = voices[line["speaker"]]
        segments = [result.audio.detach().cpu().numpy() for result in
                    pipeline(line["spoken"], voice=voice, speed=speed)]
        if not segments:
            raise RuntimeError(f"No speech generated for line {index + 1}")
        audio = np.concatenate(segments)
        raw = OUT / f"line_{index:02d}_raw.wav"
        target = OUT / f"line_{index:02d}.wav"
        sf.write(raw, audio, SR)
        # Small pitch/formant-preserving shift adds weight to the male voice.
        effects = ("rubberband=pitch=0.94,highpass=f=65,equalizer=f=150:t=q:w=0.8:g=1.5,"
                   if line["speaker"] == "male" else "highpass=f=90,")
        effects += "loudnorm=I=-17:TP=-1.5:LRA=9"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(raw), "-af", effects, "-ar", str(SR),
                        "-ac", "1", str(target)], check=True)
        audio, rate = sf.read(target, dtype="float32")
        assert rate == SR
        duration = len(audio) / SR
        timings.append({**line, "voice": voice, "start": round(clock, 4),
                        "end": round(clock + duration, 4), "file": target.name})
        audio_parts += [audio, np.zeros(int(SR * 0.55), dtype=np.float32)]
        clock += duration + 0.55
        print(f"Line {index + 1}: {voice}; {duration:.2f}s", flush=True)
    audio_parts.append(np.zeros(int(SR * 2.0), dtype=np.float32))
    combined = np.concatenate(audio_parts)
    sf.write(OUT / "narration.wav", combined, SR)
    (OUT / "timing.json").write_text(json.dumps({"sample_rate": SR,
        "duration": len(combined) / SR, "lines": timings}, indent=2))
    (OUT / "VOICE_CREDITS.txt").write_text(
        "Synthetic English speech: Kokoro-82M by hexgrad (Apache-2.0 model weights).\n"
        "Left capsule: am_michael, slower delivery and a small downward pitch shift.\n"
        "Right tablet: af_heart, brighter delivery.\n"
        "No celebrity impersonation, custom voice cloning, or third-party music.\n"
        "Model documentation: https://huggingface.co/hexgrad/Kokoro-82M\n"
        "Speech library: https://github.com/hexgrad/kokoro\n")
    print(f"Created narration.wav: {len(combined)/SR:.2f}s", flush=True)


if __name__ == "__main__":
    main()
