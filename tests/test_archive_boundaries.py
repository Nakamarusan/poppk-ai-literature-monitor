"""Boundary conditions for persisted archive coverage."""
import copy
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.archive import search_archive
from src.core import load_json
from src.sources import SourcePage


class ArchiveBoundaryTests(unittest.TestCase):
    def config(self, **options):
        config = copy.deepcopy(json.loads(Path('config.json').read_text()))
        config['historical_fallback']['sources'] = ['europe_pmc']
        config['historical_fallback']['retrieval'] = options
        return config

    @patch('src.archive.europe_pmc_page', return_value=SourcePage([], 0, 25, None))
    def test_empty_page_with_remaining_hits_is_not_exhaustion(self, fetch):
        with tempfile.TemporaryDirectory() as directory:
            result = search_archive(self.config(max_requests=1), Path(directory) / 'archive.json',
                                    set(), dt.date(2026, 9, 30))
        self.assertEqual(result.diagnostics['completed_windows'], 0)
        self.assertEqual(result.diagnostics['split_windows'], 1)
        self.assertGreater(result.diagnostics['pending_windows'], 0)
        self.assertFalse(result.diagnostics['exhausted'])

    @patch('src.archive.europe_pmc_page', return_value=SourcePage([], 0, 0, None))
    def test_daily_tail_does_not_postpone_full_archive_recheck(self, fetch):
        config = self.config()
        first_day = dt.date(2026, 9, 30)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'archive.json'
            search_archive(config, path, set(), first_day)
            self.assertEqual(load_json(path)['cycle_completed'], str(first_day))
            search_archive(config, path, set(), first_day + dt.timedelta(days=1))
            self.assertEqual(load_json(path)['cycle_completed'], str(first_day))
            fetch.reset_mock()
            search_archive(config, path, set(), first_day + dt.timedelta(days=7))
            self.assertEqual(fetch.call_args_list[0].args[1], dt.date(2026, 1, 1))
            self.assertEqual(load_json(path)['cycle_started'], '2026-10-07')


if __name__ == '__main__':
    unittest.main()
