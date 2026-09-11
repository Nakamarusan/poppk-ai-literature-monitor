"""Render stock English voices for the two existing illustrated characters.

No voice cloning. Kokoro-82M: Apache-2.0; kokoro-onnx: MIT.
Model and font files are build dependencies, not publication assets.
"""
from pathlib import Path
import argparse
import json
import subprocess


def main():
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', type=Path, default=Path('.models'))
    parser.add_argument('--output', type=Path, default=Path('build/explainer'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    script = json.loads(Path('explainer/dialogue.json').read_text(encoding='utf-8'))
    tts = Kokoro(str(args.models / 'kokoro-v1.0.onnx'), str(args.models / 'voices-v1.0.bin'))
    timeline, cursor = [], 0.45
    for index, line in enumerate(script['lines']):
        speaker = line['speaker']
        cast = script['cast'][speaker]
        audio, rate = tts.create(line['text'], voice=cast['voice'], speed=cast['speed'], lang='en-us')
        raw = args.output / f'raw_{index:02}.wav'
        sf.write(raw, audio, rate)
        target = args.output / f'line_{index:02}.wav'
        chain = 'highpass=f=65'
        if speaker == 'left':
            # Deepen the stock voice slightly without slowing the dialogue.
            chain += f',asetrate={round(rate * .95)},aresample={rate},atempo={1/.95},bass=g=2:f=140'
        chain += ',acompressor=threshold=0.16:ratio=2:attack=8:release=120'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-af',chain,str(target)], check=True)
        samples, rate = sf.read(target, dtype='float32')
        active = np.flatnonzero(np.abs(samples) > .001)
        if not len(active):
            raise RuntimeError(f'No speech generated for line {index}')
        samples = samples[max(0, int(active[0]) - int(rate*.05)):min(len(samples), int(active[-1]) + int(rate*.1))]
        rms = float(np.sqrt(np.mean(samples**2)))
        gain = min(.12/max(rms,1e-6), .92/max(float(np.max(np.abs(samples))),1e-6))
        samples *= gain
        sf.write(target, samples, rate, subtype='PCM_16')
        duration = len(samples)/rate
        timeline.append({**line, 'index': index, 'label': cast['label'], 'voice': cast['voice'],
                         'start': round(cursor,4), 'end': round(cursor+duration,4), 'file': target.name})
        cursor += duration + .35
        raw.unlink()
        print(f'{index}: {speaker}, {duration:.2f} seconds', flush=True)
    rate = 24000
    duration = cursor + 1.25
    combined = np.zeros(round(duration*rate), dtype=np.float32)
    for line in timeline:
        samples, actual_rate = sf.read(args.output / line['file'], dtype='float32')
        if actual_rate != rate:
            raise RuntimeError('Unexpected speech rate')
        start = round(line['start']*rate)
        combined[start:start+len(samples)] += samples
    sf.write(args.output/'narration.wav', combined, rate, subtype='PCM_16')
    (args.output/'timeline.json').write_text(json.dumps({'duration': duration,'sample_rate':rate,'dialogue':timeline},indent=2)+'\n')
    print(f'Dialogue duration: {duration:.2f} seconds', flush=True)


if __name__ == '__main__':
    main()
