"""Build two distinct English voice tracks and their timed dialogue.

Original script. Stock synthetic voices, not impersonations of real people.
Kokoro-82M model: Apache-2.0; kokoro-onnx runtime: MIT. Models are not published.
"""
from pathlib import Path
import argparse
import json
import subprocess
import numpy as np
import soundfile as sf

DIALOGUE = [
    ("left", "Meet the Pop P K and A I Methodology Atlas. A focused reading queue for population pharmacokinetics, pharmacometrics, and artificial intelligence."),
    ("right", "It checks the literature every morning. No new match? It selects an unreported paper from twenty twenty onward."),
    ("left", "Each brief explains the problem, the contribution, what becomes possible, and why it matters. Interpretations use the abstract only."),
    ("right", "Search by keyword, filter by year, and sort by relevance. Open the source record for a closer look."),
    ("left", "A relevance score measures topic alignment, not scientific quality. It is not a substitute for reading the paper."),
    ("right", "Research Spotlight adds one relevant paper from Science, Cell, or Nature. Recent papers come first, with older papers as a fallback."),
    ("left", "Findings and proposed research connections stay separate. Notifications, saved reports, and the website follow the same update workflow."),
    ("right", "Read. Compare. Track. Explore the atlas, and see exactly how it works."),
]

def main():
    from kokoro_onnx import Kokoro
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", type=Path, default=Path(".models"))
    parser.add_argument("--output", type=Path, default=Path("build/explainer"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    kokoro = Kokoro(str(args.models / "kokoro-v1.0.onnx"), str(args.models / "voices-v1.0.bin"))
    voices = {"left": "am_michael", "right": "af_heart"}
    timeline, cursor = [], 0.8
    for i, (speaker, text) in enumerate(DIALOGUE):
        audio, rate = kokoro.create(text, voice=voices[speaker], speed=0.94 if speaker == "left" else 1.02, lang="en-us")
        raw = args.output / f"raw_{i:02}.wav"
        sf.write(raw, audio, rate)
        target = args.output / f"line_{i:02}.wav"
        # A small pitch shift and gentle low-frequency boost deepen the male
        # delivery without slowing the dialogue or imitating a named person.
        chain = "highpass=f=65"
        if speaker == "left":
            chain += f",asetrate={round(rate * 0.94)},aresample={rate},atempo={1 / 0.94},bass=g=2:f=140"
        chain += ",acompressor=threshold=0.16:ratio=2:attack=8:release=120"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", chain, str(target)], check=True)
        samples, rate = sf.read(target, dtype="float32")
        # Trim only near-silent edges and keep a short breathing margin.
        nz = np.flatnonzero(np.abs(samples) > 0.001)
        if not len(nz):
            raise RuntimeError(f"Empty audio for dialogue {i}")
        samples = samples[max(0, int(nz[0]) - int(rate * .06)):min(len(samples), int(nz[-1]) + int(rate * .12))]
        rms = float(np.sqrt(np.mean(samples ** 2)))
        gain = min(0.13 / max(rms, 1e-6), 0.94 / max(float(np.max(np.abs(samples))), 1e-6))
        samples *= gain
        sf.write(target, samples, rate, subtype="PCM_16")
        duration = len(samples) / rate
        timeline.append({"index": i, "speaker": speaker, "voice": voices[speaker], "text": text,
                         "start": round(cursor, 4), "end": round(cursor + duration, 4), "file": target.name})
        cursor += duration + .55
        print(f"{i}: {speaker}, {duration:.2f}s, voice={voices[speaker]}", flush=True)
        raw.unlink()
    total = cursor + 1.0
    rate = 24000
    combined = np.zeros(int(total * rate) + 1, dtype=np.float32)
    for line in timeline:
        samples, sample_rate = sf.read(args.output / line["file"], dtype="float32")
        if sample_rate != rate:
            raise RuntimeError("Unexpected speech sample rate")
        start = round(line["start"] * rate)
        combined[start:start + len(samples)] += samples
    sf.write(args.output / "narration.wav", combined, rate, subtype="PCM_16")
    (args.output / "timeline.json").write_text(json.dumps({"duration": total, "sample_rate": rate, "dialogue": timeline}, indent=2) + "\n")
    print(f"Total duration: {total:.2f} seconds", flush=True)

if __name__ == "__main__":
    main()
