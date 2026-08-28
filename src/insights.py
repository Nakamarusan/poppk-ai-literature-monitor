"""Evidence-grounded summaries of each paper's methodological contribution."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from .core import Match, MonitorError, clean, request_json

SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=(?:[A-Z0-9(\[]|[\"']))")
CODE_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)
LIMITATION_CUES = (
    "no objective", "has not been established", "have not been established",
    "not been established", "remains unclear", "remain unclear",
    "remains unknown", "remain unknown", "is unknown", "are unknown",
    "however", "lack of", "lacking", "limited", "challenge", "difficult",
    "cannot", "unable", "insufficient", "scarce", "few studies",
)
CONTRIBUTION_CUES = (
    "this study aimed", "this study aims", "we aimed", "we propose",
    "we present", "we developed", "we introduce", "objective was",
    "purpose was", "developed and validated", "framework", "algorithm",
    "method", "approach",
)
CAPABILITY_CUES = (
    "enabled", "enables", "allow", "allows", "demonstrated", "showed",
    "achieved", "improved", "outperformed", "reduced", "prediction error",
    "accurately", "feasible", "performance", "can be used", "could be used",
)


@dataclass(frozen=True)
class ResearchInsight:
    prior_limitation: str
    contribution: str
    new_capability: str
    significance: str
    source: str


def _sentences(text: str) -> list[str]:
    value = clean(text)
    if not value:
        return []
    parts = [clean(part) for part in SENTENCE_BOUNDARY.split(value)]
    return [part for part in parts if len(part) >= 20]


def _best_sentence(sentences: list[str], cues: tuple[str, ...],
                   excluded: set[str] | None = None) -> str:
    excluded = excluded or set()
    scored: list[tuple[int, int, str]] = []
    for index, sentence in enumerate(sentences):
        if sentence in excluded:
            continue
        lowered = sentence.casefold()
        score = sum(1 + int(len(cue) > 12) for cue in cues if cue in lowered)
        if score:
            scored.append((score, -index, sentence))
    return max(scored, default=(0, 0, ""))[2]


def _clip(value: str, limit: int = 180) -> str:
    value = clean(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip(" ,;:") + "…"


def _category(match: Match) -> str:
    text = " ".join([
        match.paper.title, match.paper.abstract,
        *match.ai_hits, *match.method_hits,
    ]).casefold()
    if "federated learning" in text or "distributed optimization" in text:
        return "federated"
    if ("differential privacy" in text or "privacy-preserving" in text
            or "privacy preserving" in text):
        return "privacy"
    if "model selection" in text and (
        "machine learning" in text or "artificial intelligence" in text
    ):
        return "model_selection"
    if "covariate selection" in text or "automated covariate selection" in text:
        return "covariate_selection"
    if "reinforcement learning" in text:
        return "reinforcement_learning"
    if ("neural ordinary differential equation" in text or "neural ode" in text
            or "neural differential equation" in text):
        return "neural_ode"
    if "normalizing flow" in text:
        return "normalizing_flow"
    if ("mechanistic machine learning" in text or "hybrid mechanistic" in text
            or "physics-informed" in text):
        return "hybrid"
    if "model evaluation" in text or "benchmark" in text:
        return "model_evaluation"
    if "bayesian optimization" in text:
        return "bayesian_optimization"
    return "generic"


TEMPLATES: dict[str, tuple[str, str, str, str]] = {
    "federated": (
        "患者レベルデータを施設外へ共有できない環境では、中央集約型のPopPK解析をそのまま実施できなかった。",
        "各施設内の計算結果だけを統合する連合学習・分散最適化の方法を提示した。",
        "個票を中央に集めずに、複数施設のPopPK推定または評価を共同で行えるようになる。",
        "データ共有制約下でも解析対象を拡大し、多施設研究や希少疾患研究への適用可能性を高める。",
    ),
    "privacy": (
        "多施設データの統合では、個人情報保護と解析精度を同時に確保することが難しかった。",
        "プライバシー保護技術をPopPK・ファーマコメトリクス解析へ組み込む方法を提示した。",
        "患者情報の漏えいリスクを抑えながら、施設横断的な解析を実施できる可能性が生じる。",
        "データ利用の制約を守りつつ、より大きく多様な集団からモデルを構築できる点に意義がある。",
    ),
    "model_selection": (
        "複数の既存PopPKモデルから、患者ごとに適切なモデルを選ぶ客観的基準が不足していた。",
        "臨床変数と予測誤差を用い、機械学習で適切なPopPKモデルを選択する手順を構築・検証した。",
        "初回投与時から、患者ごとに予測誤差が小さいと見込まれるモデルを選べるようになる。",
        "固定した単一モデルへの依存を減らし、モデル選択自体を個別化投与設計の一部として扱える。",
    ),
    "covariate_selection": (
        "共変量探索は候補数の増加に伴って計算量と恣意性が増し、再現性の確保が難しかった。",
        "機械学習または自動化手法を用いて、共変量候補を選別する方法を提示した。",
        "多数の候補から、有用な共変量を一貫した基準で効率的に絞り込めるようになる。",
        "モデル構築者への依存を減らし、共変量モデル開発の再現性と拡張性を高める。",
    ),
    "reinforcement_learning": (
        "従来の投与設計は、単一時点の推奨量や固定ルールにとどまり、経時的な治療調整を直接扱いにくかった。",
        "患者状態と治療履歴に応じた行動を学習する強化学習の枠組みを導入した。",
        "継続、増減、切替、併用などの連続的な治療方針を時系列で選択できる可能性が生じる。",
        "静的な用量予測から、将来の反応を考慮した治療戦略の設計へ拡張できる点に意義がある。",
    ),
    "neural_ode": (
        "あらかじめ固定した構造モデルでは、複雑または未知の時間変化を十分に表現できない場合があった。",
        "薬物動態の時間発展をニューラル常微分方程式として学習する方法を提示した。",
        "構造を過度に固定せず、データから非線形な時間変化を連続時間モデルとして表現できる。",
        "機序モデルの解釈性と機械学習の柔軟性を接続する選択肢を増やす。",
    ),
    "normalizing_flow": (
        "個体間変動を正規分布などの単純な分布に限定すると、非対称性や多峰性を表現しにくかった。",
        "normalizing flowを用いて、潜在的なパラメータ分布を柔軟に推定する方法を提示した。",
        "従来の分布仮定では捉えにくい患者間変動を、より柔軟な形でモデル化できる。",
        "母集団分布の誤指定による推定・予測への影響を減らせる可能性がある。",
    ),
    "hybrid": (
        "機序モデルだけでは未知の関係を表現しにくく、純粋な機械学習だけでは薬理学的解釈が難しかった。",
        "機序モデルと機械学習を組み合わせ、既知の構造とデータ駆動成分を同時に扱う方法を提示した。",
        "薬理学的制約を保ちながら、未記述の非線形関係や個人差を学習できるようになる。",
        "予測性能だけでなく、外挿可能性と解釈可能性を両立させる方向性を示す。",
    ),
    "model_evaluation": (
        "複雑なAI・PopPKモデルを、共通条件で比較し妥当性を判断する評価枠組みが不足していた。",
        "再現可能な評価指標またはベンチマークを用いて、モデル性能を比較する方法を提示した。",
        "異なるモデルの長所と限界を同じ基準で確認し、用途に応じて選択できるようになる。",
        "予測精度だけに依存せず、一般化性能や実装可能性を含めて方法を評価できる点に意義がある。",
    ),
    "bayesian_optimization": (
        "投与条件やモデル設定の探索空間が大きい場合、総当たり探索には多くの計算が必要だった。",
        "ベイズ最適化を用いて、有望な条件を逐次的に探索する方法を提示した。",
        "評価回数を抑えながら、より良い投与条件またはモデル設定を探索できる。",
        "計算負荷の高いシミュレーションを伴う最適化の実用性を高める。",
    ),
    "generic": (
        "従来法では、複雑な患者差や非線形関係を一貫して解析へ取り込むことが難しかった。",
        "PopPK・ファーマコメトリクスにAI手法を組み込む方法を提示し、その性能を評価した。",
        "従来の固定的または手作業中心の解析を、データ駆動で補助・自動化できる可能性が生じる。",
        "モデル構築・予測・意思決定のいずれかを再現可能かつ効率的にする点に意義がある。",
    ),
}


def heuristic_insight(match: Match) -> ResearchInsight:
    category = _category(match)
    prior, contribution, capability, significance = TEMPLATES[category]
    if not clean(match.paper.abstract):
        return ResearchInsight(
            "抄録が取得できないため、従来の課題は自動判定できない。",
            f"タイトルと判定語から、{contribution}",
            "抄録が取得できないため、何が可能になったかは本文確認が必要である。",
            "研究上の意義は本文を確認して判断する必要がある。",
            "ルールベース（タイトル・キーワードのみ）",
        )
    sentences = _sentences(match.paper.abstract)
    limitation_evidence = _best_sentence(sentences, LIMITATION_CUES)
    contribution_evidence = _best_sentence(sentences, CONTRIBUTION_CUES)
    capability_evidence = _best_sentence(
        sentences, CAPABILITY_CUES,
        {sentence for sentence in (limitation_evidence, contribution_evidence)
         if sentence},
    )
    evidence = [sentence for sentence in (
        limitation_evidence, contribution_evidence, capability_evidence
    ) if sentence]
    source = "ルールベース（抄録・キーワード）"
    if evidence:
        source += "／根拠文あり"
    return ResearchInsight(
        _clip(prior), _clip(contribution), _clip(capability),
        _clip(significance), source,
    )


def _response_text(data: dict[str, Any]) -> str:
    direct = data.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    chunks: list[str] = []
    output = data.get("output")
    for item in output if isinstance(output, list) else []:
        if not isinstance(item, dict):
            continue
        content_items = item.get("content")
        for content in content_items if isinstance(content_items, list) else []:
            if isinstance(content, dict) and content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    return "\n".join(chunks).strip()


def parse_insight_json(text: str, source: str = "AI要約") -> ResearchInsight:
    value = CODE_FENCE.sub("", text.strip())
    start, end = value.find("{"), value.rfind("}")
    if start < 0 or end <= start:
        raise MonitorError("Insight response did not contain a JSON object")
    try:
        data = json.loads(value[start:end + 1])
    except json.JSONDecodeError as exc:
        raise MonitorError("Insight response was not valid JSON") from exc
    required = (
        "prior_limitation", "contribution", "new_capability", "significance"
    )
    if not all(clean(data.get(key)) for key in required):
        raise MonitorError("Insight response was missing required fields")
    return ResearchInsight(
        *(_clip(str(data[key])) for key in required),
        source=source,
    )


def openai_insight(match: Match, config: dict[str, Any],
                   api_key: str) -> ResearchInsight:
    settings = config.get("insights", {})
    model = (
        clean(os.getenv("OPENAI_MODEL"))
        or clean(settings.get("model"))
        or "gpt-5.6-luna"
    )
    abstract_limit = int(settings.get("max_abstract_chars", 7000))
    output_limit = int(settings.get("max_output_tokens", 700))
    prompt_data = {
        "title": match.paper.title,
        "abstract": match.paper.abstract[:abstract_limit],
        "venue": match.paper.venue,
        "publication_date": match.paper.date,
        "matched_popPK_terms": match.pk_hits,
        "matched_AI_terms": match.ai_hits,
        "matched_method_terms": match.method_hits,
    }
    instructions = (
        "You are an editor specializing in pharmacometrics and methodological "
        "research. Using only the supplied title and abstract, write a concise "
        "Japanese assessment. Do not use outside knowledge and do not overstate "
        "clinical benefit. Separate: (1) the prior limitation, (2) the "
        "methodological contribution, (3) what became newly possible, and (4) "
        "why it matters for population PK, pharmacometrics, or model-informed "
        "dosing. If the abstract does not support a claim, state "
        "'抄録では明示されていない。'. Each value must be one sentence, normally "
        "45-110 Japanese characters. Return only one JSON object with exactly "
        "these string keys: prior_limitation, contribution, new_capability, "
        "significance."
    )
    payload = {
        "model": model,
        "instructions": instructions,
        "input": json.dumps(prompt_data, ensure_ascii=False),
        "max_output_tokens": output_limit,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = request_json(
        "https://api.openai.com/v1/responses",
        method="POST", payload=payload, headers=headers, retries=2,
    )
    text = _response_text(data)
    if not text:
        raise MonitorError("OpenAI response did not contain output text")
    return parse_insight_json(text, f"AI要約（{model}、抄録のみ）")


def summarize_research(match: Match,
                       config: dict[str, Any]) -> ResearchInsight:
    settings = config.get("insights", {})
    enabled = bool(settings.get("enabled", True))
    api_key = clean(os.getenv("OPENAI_API_KEY"))
    if enabled and api_key:
        try:
            return openai_insight(match, config, api_key)
        except Exception as exc:
            print(
                f"Insight API failed for {match.paper.title}: {clean(exc)}; "
                "using fallback."
            )
    return heuristic_insight(match)
