"""Validate published walkthrough assets without installing media dependencies."""
import ast
import hashlib
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VideoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.video = None
        self.sources = []
        self.tracks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'video':
            self.video = attrs
        elif tag == 'source':
            self.sources.append(attrs)
        elif tag == 'track':
            self.tracks.append(attrs)


class ExplainerTests(unittest.TestCase):
    def test_dialogue_has_six_alternating_speakers(self):
        script = json.loads((ROOT / 'explainer/dialogue.json').read_text())
        self.assertEqual(script['cast']['left']['voice'], 'am_michael')
        self.assertEqual(script['cast']['right']['voice'], 'af_heart')
        self.assertEqual([line['speaker'] for line in script['lines']], ['left', 'right'] * 3)
        for line in script['lines']:
            self.assertTrue(line['text'].strip())
            self.assertTrue(line['captions'])
            self.assertTrue(all(caption.strip() for caption in line['captions']))

    def test_render_sources_parse_without_media_imports(self):
        for name in ('voiceover.py', 'render.py'):
            ast.parse((ROOT / 'explainer' / name).read_text(), filename=name)

    def test_player_has_controls_captions_and_no_autoplay(self):
        parser = VideoParser()
        parser.feed((ROOT / 'docs/explainer.html').read_text())
        self.assertIsNotNone(parser.video)
        self.assertIn('controls', parser.video)
        self.assertIn('playsinline', parser.video)
        self.assertNotIn('autoplay', parser.video)
        self.assertEqual(parser.video['poster'], './media/atlas-explainer-poster.jpg')
        self.assertTrue(any(item.get('src') == './media/atlas-explainer.mp4' for item in parser.sources))
        self.assertTrue(any(item.get('srclang') == 'en' and item.get('kind') == 'captions' for item in parser.tracks))

    def test_readme_links_the_poster_to_the_player(self):
        readme = (ROOT / 'README.md').read_text()
        self.assertIn('docs/media/atlas-explainer-poster.jpg', readme)
        self.assertIn('https://nakamarusan.github.io/poppk-ai-literature-monitor/explainer.html', readme)
        self.assertIn('docs/media/transcript.md', readme)

    def test_video_build_triggers_pages_publication(self):
        workflow = (ROOT / '.github/workflows/pages.yml').read_text()
        self.assertIn('workflow_run:', workflow)
        self.assertIn('Build site explainer video', workflow)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow)

    def test_published_media_match_the_manifest(self):
        media = ROOT / 'docs/media'
        manifest = json.loads((media / 'manifest.json').read_text())
        video = media / 'atlas-explainer.mp4'
        self.assertEqual(hashlib.sha256(video.read_bytes()).hexdigest(), manifest['video_sha256'])
        self.assertEqual(video.stat().st_size, manifest['video_bytes'])
        self.assertGreater(manifest['duration_seconds'], 20)
        self.assertLess(manifest['duration_seconds'], 70)
        self.assertEqual(manifest['resolution'], [1280, 720])
        self.assertEqual(manifest['voices'], {'left': 'am_michael', 'right': 'af_heart'})
        self.assertTrue((media / 'atlas-explainer.vtt').read_text().startswith('WEBVTT'))
        for name in ('atlas-explainer-poster.jpg', 'atlas-explainer.srt', 'transcript.md'):
            self.assertGreater((media / name).stat().st_size, 0)


if __name__ == '__main__':
    unittest.main()
