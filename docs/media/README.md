# Illustrated site walkthrough

The video explains the publicly documented behavior of the PopPK × AI Methodology Atlas. It is an illustrated overview, not a recording of the live website. It does not display invented paper titles, publication counts, or scientific-quality scores.

## Production

The capsule and tablet characters, their white lab coats, and the presentation environment come from an image generated for this project. The supplied draft was re-edited into six scenes with original interface diagrams, short English captions, a speech-driven mouth animation, and a single shared scene. No split-screen layout or left/right audio panning is used.

The left character uses the stock `am_michael` English voice with a small pitch adjustment and gentle bass emphasis. The right uses the stock `af_heart` English voice. Neither is a voice clone or an impersonation of a named person. Dialogue levels are balanced and the combined track is normalized for web playback. No music, sound-effect library, third-party character artwork, journal logos, or product branding is intentionally incorporated.

Speech is generated using [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), whose model card specifies Apache-2.0, through [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), whose runtime is MIT-licensed. The build downloads models and stock voice data from the runtime project's model-files-v1.0 release. Model and font files are not distributed in this repository's media output. System DejaVu Sans or Liberation Sans is used for rasterized titles and captions.

The text and diagrams describe this project. Names such as Science, Cell, Nature, Europe PMC, Crossref, and arXiv identify the relevant journals or services; no affiliation or endorsement is claimed. These source notes are not a blanket license for redistributing the artwork or a legal guarantee of clearance in every jurisdiction.

## Files

`atlas-explainer.mp4` is the web-ready H.264/AAC video. `atlas-explainer-poster.jpg` is the README thumbnail. English captions are visible in the video, with separate SRT and VTT copies and a text transcript. `manifest.json` records the duration, format, voice assignment, file size, and checksum.

The script is in `explainer/dialogue.json`. Rendering is implemented in `explainer/voiceover.py` and `explainer/render.py`. The **Build site explainer video** workflow regenerates the media only when its inputs change or when manually requested. It does not run with every daily literature search. Successful builds commit media to `docs/media/`, after which the existing Pages deployment publishes the updated site.
