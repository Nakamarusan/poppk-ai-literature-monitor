# 母集団PK × AI 方法論文献モニター

母集団薬物動態解析（population pharmacokinetics、NLME、pharmacometrics）とAI・機械学習の両方に関係する**新しい方法論論文・プレプリント**を自動検索し、該当文献がある場合だけGitHub Issueで通知します。

## 実行時刻

- 本実行：毎日 **07:00（日本時間、Asia/Tokyo）**
- 予備実行：毎日 **07:20（日本時間）**
- 07:00の処理が成功していれば、07:20の処理は検索せず終了します。
- GitHub側の混雑により、実際の開始が数分遅れる場合があります。

## 検索対象

- Europe PMC：PubMedを含む生物医学文献
- Crossref：出版社が登録した論文とプレプリント
- arXiv：関連プレプリント

収載遅延を考慮し、既定では直近8日間を毎日再検索します。DOI、arXiv ID、データベースID、正規化タイトルで重複を除外し、通知済み文献を `state/seen.json` で管理します。

## 採択条件

次の3条件をすべて満たす文献を通知します。

1. PopPK、NLME、pharmacometrics、MIPD、QSPなどとの明確な関連がある
2. 機械学習、連合学習、強化学習、Neural ODE、normalizing flow、差分プライバシーなどとの関連がある
3. 推定法、最適化法、モデル評価、共変量選択、アルゴリズム、ソフトウェアなどの方法論的要素がある

単に機械学習を特定薬剤へ適用した研究、通常の薬剤別PopPK解析、レビュー、解説、症例報告は原則として除外します。判定はキーワード規則に基づくため、研究上の重要性は本文で確認してください。

## 通知と保存

- 新着文献がある場合、リポジトリ所有者をメンションし、担当者に指定したIssueを作成します。
- 一部または全部のデータソースに障害がある場合もIssueで警告します。
- 同じ通知内容のIssueは重複作成しません。
- 毎日の結果は `reports/YYYY-MM-DD.md` と `reports/latest.md` に保存します。
- GitHubの通知設定に応じて、Web、モバイル、またはメールで通知を受け取れます。

## 手動実行

GitHubの **Actions** タブで `Daily PopPK × AI literature monitor` を選択し、**Run workflow** を実行します。検索期間は1～90日に変更できます。

ローカルでテストする場合：

```bash
python -m unittest discover -s tests -v
```

通知せずに検索する場合：

```bash
python -m src.literature_monitor --no-notify
```

## 設定

`config.json` で検索語、対象データソース、検索期間、除外語を変更できます。CrossrefとEurope PMCへ連絡先を付ける場合は、任意で **Settings → Secrets and variables → Actions → Variables** に `CONTACT_EMAIL` を登録します。未登録でも動作します。

## GitHub Actionsの権限

日次レポートと通知履歴を保存し、Issueを作成するため、ワークフローは次の権限を使用します。

```yaml
permissions:
  contents: write
  issues: write
```

## 構成

```text
.github/workflows/daily-literature-monitor.yml  毎朝の検索、テスト、通知、結果保存
config.json                                    検索語と選定条件
src/core.py                                    データ構造、選定、重複除外、状態管理
src/sources.py                                 Europe PMC・Crossref・arXivの取得
src/literature_monitor.py                      レポート、Issue通知、実行制御
state/seen.json                                通知済み文献と最終成功時刻
reports/                                       日次レポート
tests/test_monitor.py                          単体テスト
```
