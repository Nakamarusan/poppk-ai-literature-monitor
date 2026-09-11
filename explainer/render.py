"""Compose the approved illustration, moving UI, two voices and English captions.

This is an illustrated walkthrough, not a recording of the live website.
Only original functional diagrams are shown; no fabricated papers or metrics.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import math
import subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
INK, MUTED, PAPER, TEAL, COPPER = '#24282a', '#656d70', '#faf8f2', '#29646a', '#c96a3f'
URL = 'https://nakamarusan.github.io/poppk-ai-literature-monitor/'


def prepare_art():
    """Verify the approved still; decode transport fragments only on first build."""
    path = Path('explainer/scene.webp')
    if not path.exists():
        fragments = [Path(f'explainer/art.part{i}.b64') for i in range(1, 4)]
        encoded = ''.join(p.read_text(encoding='ascii').strip() for p in fragments)
        content = base64.b64decode(encoded, validate=True)
    else:
        content = path.read_bytes()
    blob = b'blob ' + str(len(content)).encode() + b'\0' + content
    if hashlib.sha1(blob).hexdigest() != 'c507311f2d4073ed7ae082051c038c687ebfde72':
        raise RuntimeError('The illustration checksum differs from the approved source')
    path.write_bytes(content)
    return path


@lru_cache(maxsize=32)
def font(size, bold=False):
    family = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    candidates = [Path('/usr/share/fonts/truetype/dejavu') / family,
                  Path('/usr/share/fonts/truetype/liberation2') / ('LiberationSans-Bold.ttf' if bold else 'LiberationSans-Regular.ttf')]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise RuntimeError('Install DejaVu Sans or Liberation Sans; fonts are not bundled.')


def text(d, xy, value, size=22, color=INK, bold=False, anchor='la'):
    d.text(xy, value, font=font(size,bold), fill=color, anchor=anchor)


def box(d, xy, fill='#ffffff', outline='#e0ded6', width=1, radius=15):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def orbit(d, t):
    cx, cy = 812, 409
    for i in range(3):
        points=[]
        angle = t*.38+i*math.pi/3
        for k in range(121):
            a=k*math.tau/120
            x,y=84*math.cos(a),31*math.sin(a)
            points.append((cx+x*math.cos(angle)-y*math.sin(angle),cy+x*math.sin(angle)+y*math.cos(angle)))
        d.line(points, fill=(TEAL,COPPER,'#bca67d')[i], width=2)
    d.ellipse((cx-5,cy-5,cx+5,cy+5), fill=COPPER)


def frame(base, t, total, index, speaker, caption, amplitude, progress):
    im=base.copy()
    d=ImageDraw.Draw(im)
    text(d,(357,199),'PopPK × AI',18,bold=True)
    text(d,(951,201),'ILLUSTRATED WALKTHROUGH',10,MUTED,anchor='ra')
    d.line((354,232,950,232),fill='#dfddd5',width=1)
    titles=['A focused reading queue.','From search to your library.',
            'Four questions. One brief.','Relevance is not quality.',
            'One more perspective.','Read. Compare. Verify.']
    text(d,(652,255),titles[index],29,bold=True,anchor='ma')
    if index==0:
        text(d,(401,331),'Pharmacometrics',26,bold=True)
        text(d,(401,372),'× artificial intelligence',22,TEAL,bold=True)
        text(d,(401,446),'Methods. Models. Evidence.',18,MUTED)
        text(d,(401,483),'A reading queue, not a quality verdict.',14,MUTED)
        orbit(d,t)
    elif index==1:
        text(d,(652,302),'SCHEDULED DAILY · 07:00 JST',13,MUTED,anchor='ma')
        for i,label in enumerate(['Search','Screen','Interpret','Publish']):
            x=397+i*137
            active=int(progress*4)%4==i
            box(d,(x,348,x+119,426), '#eaf2ef' if active else '#fffefd', TEAL if active else '#dfddd5',2)
            text(d,(x+59,358),f'0{i+1}',18,COPPER,True,'ma')
            text(d,(x+59,395),label,15,INK,True,'ma')
        text(d,(652,458),'Europe PMC · Crossref · optional arXiv',17,TEAL,anchor='ma')
        text(d,(652,495),'No new match? An unreported paper from 2020 onward.',13,MUTED,anchor='ma')
    elif index==2:
        items=[('01  THE PROBLEM','What gap is identified?'),('02  CONTRIBUTION','What does the study add?'),
               ('03  NEW POSSIBILITIES','What becomes possible?'),('04  SIGNIFICANCE','Why might it matter?')]
        for i,(label,sub) in enumerate(items):
            x,y=402+(i%2)*274,319+(i//2)*85
            box(d,(x,y,x+250,y+69), '#edf4f0' if int(progress*4)%4==i else '#fffefd')
            text(d,(x+14,y+11),label,13,COPPER,True)
            text(d,(x+14,y+35),sub,15)
        text(d,(652,507),'Interpretation stops at the abstract.',17,TEAL,True,'ma')
    elif index==3:
        cx,cy=509,412
        d.arc((cx-67,cy-67,cx+67,cy+67),-90,270,fill='#dfddd5',width=10)
        d.arc((cx-67,cy-67,cx+67,cy+67),-90,-90+300*min(1,progress*2),fill=COPPER,width=10)
        text(d,(cx,386),'0–100',26,bold=True,anchor='ma')
        text(d,(cx,425),'TOPIC FIT',12,TEAL,True,'ma')
        for i,label in enumerate(['Search keywords','Filter by year','Compare topic alignment']):
            y=348+i*53
            d.ellipse((634,y+4,641,y+11),fill=TEAL)
            text(d,(656,y),label,18,bold=i==2)
        text(d,(652,514),'Not a measure of validity, novelty, or clinical benefit.',13,MUTED,anchor='ma')
    elif index==4:
        text(d,(652,304),'RESEARCH SPOTLIGHT',13,COPPER,True,'ma')
        for i,name in enumerate(['Science','Cell','Nature']):
            x=404+i*181
            box(d,(x,351,x+154,405), '#edf4f0' if int(progress*3)%3==i else '#fffefd')
            text(d,(x+77,366),name,22,bold=True,anchor='ma')
        text(d,(652,433),'One relevant paper across three flagship journals.',15,TEAL,True,'ma')
        text(d,(652,470),'Findings and proposed uses stay separate.',16,MUTED,anchor='ma')
        text(d,(652,505),'Recent first · 2020+ fallback · when an eligible match is available',11,MUTED,anchor='ma')
    else:
        text(d,(652,329),'Find your next paper.',24,bold=True,anchor='ma')
        box(d,(510,393,794,448),TEAL,TEAL,radius=26)
        text(d,(652,407),'Explore the Atlas  →',21,'#ffffff',True,'ma')
        text(d,(652,476),'Abstract-only. Read critically.',18,COPPER,True,'ma')
        text(d,(652,516),URL.replace('https://',''),12,MUTED,anchor='ma')
    # Speech activates the corresponding character, not a split screen or
    # hard-panned audio channel. Both voices remain centered.
    if speaker and amplitude>.009:
        level=min(1,amplitude/.18)
        cx,cy=(247,409) if speaker=='left' else (1075,473)
        rx,ry=(13,4+6*level) if speaker=='left' else (15,5+7*level)
        d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill='#3a201d')
        d.arc((cx-rx+3,cy-ry,cx+rx-3,cy+ry-2),5,170,fill='#bc6957',width=2)
    d.rectangle((0,625,W,H),fill='#202526')
    label='CAPSULE' if speaker=='left' else 'TABLET' if speaker=='right' else 'ILLUSTRATED SITE WALKTHROUGH'
    color='#e9a16b' if speaker=='left' else '#9bcccb'
    text(d,(W/2,636),label,12,color,True,'ma')
    if caption:
        text(d,(W/2,660),caption,22,'#ffffff',anchor='ma')
    else:
        text(d,(W/2,663),'PopPK × AI Methodology Atlas',19,'#ffffff',anchor='ma')
    d.rectangle((0,715,int(W*t/total),719), fill=color)
    for i in range(6):
        x=620+i*13
        d.ellipse((x,551,x+4,555),fill=COPPER if i==index else '#d1cfc6')
    return im


def timestamp(seconds, sep='.'):
    ms=round(seconds*1000)
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'


def caption_cues(timeline):
    cues=[]
    for line in timeline:
        weights=[len(c.split()) for c in line['captions']]
        cursor=line['start']
        for value,weight in zip(line['captions'],weights):
            end=cursor+(line['end']-line['start'])*weight/sum(weights)
            cues.append({'start':cursor,'end':end,'text':value,'speaker':line['speaker'],'label':line['label']})
            cursor=end
    return cues


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=Path('build/explainer'))
    parser.add_argument('--output',type=Path,default=Path('docs/media'))
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    base=Image.open(prepare_art()).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    data=json.loads((args.input/'timeline.json').read_text())
    lines=data['dialogue'];total=data['duration'];cues=caption_cues(lines)
    if args.preview:
        for i in range(6):
            frame(base,lines[i]['start']+.6,total,i,lines[i]['speaker'],lines[i]['captions'][0],.08,.4).save(args.output/f'preview_{i}.jpg',quality=90)
        return
    import numpy as np
    import soundfile as sf
    samples,rate=sf.read(args.input/'narration.wav',dtype='float32')
    silent=args.input/'visual.mp4'
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-an','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-threads','2',str(silent)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(math.ceil(total*FPS)):
            t=n/FPS
            index=max([i for i,line in enumerate(lines) if line['start']<=t] or [0])
            line=lines[index]
            speaking=line['start']<=t<=line['end']
            speaker=line['speaker'] if speaking else None
            current=next((cue['text'] for cue in cues if cue['start']<=t<cue['end']), '')
            segment=samples[int(t*rate):int((t+.045)*rate)]
            amp=float(np.sqrt(np.mean(segment**2))) if segment.size else 0
            progress=max(0,min(1,(t-line['start'])/max(.1,line['end']-line['start'])))
            im=frame(base,t,total,index,speaker,current,amp,progress)
            proc.stdin.write(im.tobytes())
    finally:
        proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError('Video encoding failed')
    output=args.output/'atlas-explainer.mp4'
    # Balanced speech levels; H.264/AAC plus faststart for web playback.
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(args.input/'narration.wav'),
        '-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=7,afade=t=in:d=0.08',
        '-c:a','aac','-b:a','112k','-ar','48000','-ac','1','-movflags','+faststart',
        '-metadata','title=PopPK x AI — illustrated site walkthrough','-metadata:s:a:0','language=eng','-shortest',str(output)],check=True)
    vtt=['WEBVTT',''];srt=[]
    for n,cue in enumerate(cues,1):
        vtt += [f"{timestamp(cue['start'])} --> {timestamp(cue['end'])}",f"{cue['label']}: {cue['text']}",'']
        srt += [str(n),f"{timestamp(cue['start'],',')} --> {timestamp(cue['end'],',')}",f"{cue['label']}: {cue['text']}",'']
    (args.output/'atlas-explainer.vtt').write_text('\n'.join(vtt),encoding='utf-8')
    (args.output/'atlas-explainer.srt').write_text('\n'.join(srt),encoding='utf-8')
    transcript=['# Video transcript','','An illustrated walkthrough with stock synthetic English voices.','']
    for line in lines:
        transcript += [f"**{line['label']} ({line['speaker']} character):** "+' '.join(line['captions']),'']
    (args.output/'transcript.md').write_text('\n'.join(transcript),encoding='utf-8')
    poster=frame(base,0,total,0,None,'',0,0)
    pd=ImageDraw.Draw(poster)
    box(pd,(456,621,824,700), '#ffffff','#ffffff',radius=37)
    pd.polygon([(483,642),(483,679),(511,660)],fill=TEAL)
    text(pd,(529,647),f'Watch the overview · {round(total)}s',19,INK,True)
    poster.save(args.output/'atlas-explainer-poster.jpg',quality=91,optimize=True)
    manifest={'duration_seconds':round(total,3),'resolution':[W,H],'fps':FPS,
              'voices':{'left':'am_michael','right':'af_heart'},'audio':'mono; both speakers centered',
              'captions':'English; burned in; SRT and VTT supplied',
              'video_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'video_bytes':output.stat().st_size,
              'scene_sha256':hashlib.sha256(Path('explainer/scene.webp').read_bytes()).hexdigest(),
              'evidence_policy':'Site functionality only. No fabricated paper examples or scientific quality claims.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2),flush=True)


if __name__=='__main__':
    main()
