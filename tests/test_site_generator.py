import json
import tempfile
import unittest
from pathlib import Path

from src.site_generator import build_payload, parse_report, write_site_data


SAMPLE_REPORT = """<!-- poppk-ai-selection -->

# 母集団PK × AI 方法論文献アラート

実行日時: 2026-09-01 07:02 JST
新着採択: **0件**
過去論文の紹介: **1件**（2020年以降・未紹介）

## 1. [Federated learning for population pharmacokinetics](https://doi.org/10.1/example)

- **区分:** 2020年以降の過去論文（新着がない日の補完）
- **著者:** A Author, B Author
- **掲載誌・公開元:** Journal
- **公開日:** 2023-05-01
- **DOI:** 10.1/example

### 研究の位置づけ（抄録ベース）

- **従来の課題:** 個票を共有できなかった。
- **今回の方法・新規性:** 連合推定法を提案した。
- **新たに可能になったこと:** 個票を移動せず推定できる。
- **研究上の意義:** 多施設解析を実施しやすくなる。

*要約方法: ルールベース*

<details>
<summary>自動判定の根拠と抄録を表示</summary>

- **優先度:** High（スコア 18）
- **取得元:** Europe PMC
- **母集団PK関連語:** population pharmacokinetic, \\bpop[- ]?pk\\b
- **AI関連語:** federated learning
- **方法論関連語:** framework, estimation
- **抄録抜粋:** We propose a federated estimation framework.

</details>
"""


class SiteGeneratorTests(unittest.TestCase):
    def test_parse_historical_article(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "2026-09-01.md"
            path.write_text(SAMPLE_REPORT, encoding="utf-8")
            articles, latest_scan = parse_report(path)

        self.assertEqual(latest_scan, "2026-09-01 07:02 JST")
        self.assertEqual(len(articles), 1)
        article = articles[0]
        self.assertEqual(article["selection_type"], "historical")
        self.assertEqual(article["doi"], "10.1/example")
        self.assertEqual(article["priority"], "High")
        self.assertEqual(article["score"], 18)
        self.assertEqual(article["terms"]["ai"], ["federated learning"])
        self.assertEqual(
            article["insights"]["new_capability"],
            "個票を移動せず推定できる。",
        )

    def test_ignores_latest_alias_and_empty_reports(self):
        with tempfile.TemporaryDirectory() as temporary:
            report_dir = Path(temporary) / "reports"
            report_dir.mkdir()
            (report_dir / "2026-09-01.md").write_text(
                SAMPLE_REPORT, encoding="utf-8"
            )
            (report_dir / "latest.md").write_text(
                SAMPLE_REPORT, encoding="utf-8"
            )
            (report_dir / "2026-09-02.md").write_text(
                "# Report\n\n実行日時: 2026-09-02 07:03 JST\n"
                "新着採択: **0件**\n",
                encoding="utf-8",
            )
            payload = build_payload(report_dir)

        self.assertEqual(payload["article_count"], 1)
        self.assertEqual(payload["historical_count"], 1)
        self.assertEqual(payload["last_scan_at"], "2026-09-02 07:03 JST")

    def test_write_site_data_is_valid_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report_dir = root / "reports"
            output = root / "docs" / "articles.json"
            report_dir.mkdir()
            (report_dir / "2026-09-01.md").write_text(
                SAMPLE_REPORT, encoding="utf-8"
            )
            write_site_data(report_dir, output)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["article_count"], 1)
        self.assertEqual(
            payload["articles"][0]["title"],
            "Federated learning for population pharmacokinetics",
        )


if __name__ == "__main__":
    unittest.main()
