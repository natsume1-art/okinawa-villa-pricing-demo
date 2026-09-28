"""算出済み価格を社内向けに通知・確認できる形にするモジュール。

案件要件の「まずは通知・確認ベースの半自動運用から着手」に対応。
コンソール出力に加え、環境変数 SLACK_WEBHOOK_URL が設定されていれば
Slack Incoming Webhook にも通知する（未設定時はスキップし、デモ実行を妨げない）。
"""
import os
from typing import Iterable

from pricing_engine import PriceSuggestion

CHANGE_THRESHOLD = 0.03  # 現行価格からの変動率がこれ未満の場合は「変更なし」扱い


def _format_row(current_price: int, suggestion: PriceSuggestion) -> str:
    diff = suggestion.suggested_price - current_price
    diff_pct = diff / current_price if current_price else 0
    flag = "→" if abs(diff_pct) < CHANGE_THRESHOLD else ("▲" if diff > 0 else "▼")
    return (
        f"{suggestion.target_date} | 現行 {current_price:,}円 "
        f"{flag} 提案 {suggestion.suggested_price:,}円 "
        f"({diff_pct:+.1%}){'  ※周辺相場でクランプ' if suggestion.clamped_by_market else ''}"
    )


def build_report(current_price: int, suggestions: Iterable[PriceSuggestion]) -> str:
    lines = ["=== 価格改定提案レポート（確認用） ==="]
    for s in suggestions:
        lines.append(_format_row(current_price, s))
    lines.append(
        "\n※本レポートは確認・承認用です。反映するにはOTA連携（--mode push）を実行してください。"
    )
    return "\n".join(lines)


def notify(report: str) -> None:
    print(report)

    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    import requests

    try:
        requests.post(webhook_url, json={"text": report}, timeout=5)
    except requests.RequestException as exc:
        print(f"[warn] Slack通知に失敗しました: {exc}")
