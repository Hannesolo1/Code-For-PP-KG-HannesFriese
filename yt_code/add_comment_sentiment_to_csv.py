from __future__ import annotations

import argparse
import configparser
import json
import os
from pathlib import Path
from typing import Callable

import pandas as pd
from openai import OpenAI
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def label_from_score(score: float) -> str:
    if score >= 0.2:
        return "positive"
    if score <= -0.2:
        return "negative"
    return "neutral"


def _parse_json_text(text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Empty JSON payload")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def load_dance_records(json_path: Path) -> list[dict]:
    records: list[dict] = []

    if json_path.suffix.lower() == ".jsonl":
        with json_path.open("r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                parsed = json.loads(raw)
                if "videos" in parsed:
                    records.append(parsed)
                else:
                    records.extend(v for v in parsed.values() if isinstance(v, dict) and "videos" in v)
        return records

    with json_path.open("r", encoding="utf-8") as f:
        parsed = json.load(f)

    if isinstance(parsed, dict) and "videos" in parsed:
        return [parsed]
    if isinstance(parsed, dict):
        return [v for v in parsed.values() if isinstance(v, dict) and "videos" in v]
    if isinstance(parsed, list):
        return [v for v in parsed if isinstance(v, dict) and "videos" in v]

    raise ValueError(f"Unsupported data structure in {json_path}")


def _resolve_openai_key(root: Path) -> str:
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    for candidate in [
        root / "data" / "GPT4oKEY.txt",
        root / "data" / "LLM_key.txt",
    ]:
        if candidate.exists():
            key = candidate.read_text(encoding="utf-8").strip()
            if key:
                return key

    raise RuntimeError("OPENAI_API_KEY not set and no local key file found.")


def _model_from_cfg(cfg_path: Path) -> tuple[str, float]:
    default_model = "gpt-4o-mini"
    default_temperature = 0.0

    if not cfg_path.exists():
        return default_model, default_temperature

    parser = configparser.ConfigParser()
    parser.read(cfg_path)

    section = "components.llm_sentiment.model"
    model_name = parser.get(section, "name", fallback=default_model)

    raw_config = parser.get(section, "config", fallback='{"temperature": 0.0}')
    try:
        temp = float(json.loads(raw_config).get("temperature", 0.0))
    except Exception:
        temp = default_temperature

    return model_name, temp


def gpt_comment_scorer(root: Path, cfg_path: Path, model_override: str | None = None) -> Callable[[str], float]:
    api_key = _resolve_openai_key(root)
    model_name, temperature = _model_from_cfg(cfg_path)
    model_name = model_override or model_name

    client = OpenAI(api_key=api_key)

    def score_comment(text: str) -> float:
        response = client.chat.completions.create(
            model=model_name,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You classify sentiment of YouTube comments. "
                        "Return strict JSON only: {\"score\": number, \"label\": \"positive|neutral|negative\"}. "
                        "score must be in [-1, 1]."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Comment: {text}",
                },
            ],
        )
        payload = _parse_json_text(response.choices[0].message.content or "")
        score = float(payload["score"])
        return max(-1.0, min(1.0, score))

    return score_comment


def vader_comment_scorer() -> Callable[[str], float]:
    analyzer = SentimentIntensityAnalyzer()

    def score_comment(text: str) -> float:
        return float(analyzer.polarity_scores(text)["compound"])

    return score_comment


def build_video_sentiment_table(json_path: Path, scorer: Callable[[str], float]) -> pd.DataFrame:
    dance_records = load_dance_records(json_path)
    rows: list[dict] = []

    for style_data in dance_records:
        for video in style_data.get("videos", []):
            comments = video.get("comments", [])
            if not comments:
                continue

            video_id = (
                video.get("basic_info", {}).get("video_id")
                or video.get("comprehensive_info", {}).get("video_id")
                or comments[0].get("video_id")
            )
            if not video_id:
                continue

            scores: list[float] = []
            labels: list[str] = []

            for comment in comments:
                text = str(comment.get("text", "")).strip()
                if not text:
                    continue

                score = scorer(text)
                scores.append(score)
                labels.append(label_from_score(score))

            if not scores:
                continue

            pos_count = sum(1 for x in labels if x == "positive")
            neg_count = sum(1 for x in labels if x == "negative")
            neu_count = sum(1 for x in labels if x == "neutral")

            if pos_count >= neg_count and pos_count >= neu_count:
                majority = "positive"
            elif neg_count >= pos_count and neg_count >= neu_count:
                majority = "negative"
            else:
                majority = "neutral"

            rows.append(
                {
                    "video_id": video_id,
                    "comment_sentiment": majority,
                    "comment_sentiment_avg_score": round(sum(scores) / len(scores), 4),
                    "comment_sentiment_comment_count": len(scores),
                }
            )

    sentiment_df = pd.DataFrame(rows)
    if sentiment_df.empty:
        return sentiment_df

    return sentiment_df.sort_values(
        by=["comment_sentiment_comment_count", "comment_sentiment_avg_score"],
        ascending=[False, False],
    ).drop_duplicates(subset=["video_id"], keep="first")


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["gpt", "vader"], default="gpt")
    parser.add_argument("--model", default=None, help="Override model from sentiment config.")
    parser.add_argument("--json-path", default=None, help="Path to dance_youtube_data.json or .jsonl")
    parser.add_argument("--csv-path", default=str(root / "data" / "yt_data" / "dance_videos.csv"))
    parser.add_argument("--cfg-path", default=str(root / "kg_code" / "sentiment_config.cfg"))
    args = parser.parse_args()

    default_jsonl = root / "data" / "yt_data" / "dance_youtube_data.jsonl"
    default_json = root / "data" / "yt_data" / "dance_youtube_data.json"

    if args.json_path:
        json_path = Path(args.json_path)
    else:
        json_path = default_jsonl if default_jsonl.exists() else default_json

    csv_path = Path(args.csv_path)
    cfg_path = Path(args.cfg_path)

    if not json_path.exists():
        raise FileNotFoundError(f"Missing input file: {json_path}")
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV file: {csv_path}")

    if args.method == "gpt":
        scorer = gpt_comment_scorer(root=root, cfg_path=cfg_path, model_override=args.model)
    else:
        scorer = vader_comment_scorer()

    sentiment_df = build_video_sentiment_table(json_path=json_path, scorer=scorer)

    videos_df = pd.read_csv(csv_path)
    if sentiment_df.empty:
        print("No comment sentiment rows were produced; CSV left unchanged.")
        return

    merged = videos_df.drop(
        columns=[
            c
            for c in [
                "comment_sentiment",
                "comment_sentiment_avg_score",
                "comment_sentiment_comment_count",
            ]
            if c in videos_df.columns
        ],
        errors="ignore",
    ).merge(sentiment_df, on="video_id", how="left")

    merged.to_csv(csv_path, index=False, encoding="utf-8")

    print(f"Updated: {csv_path}")
    print(f"Rows in CSV: {len(merged)}")
    print(f"Unique videos with sentiment: {sentiment_df['video_id'].nunique()}")


if __name__ == "__main__":
    main()

