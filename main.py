"""価格自動算出パイプラインのエントリポイント。

使い方:
  python main.py                       # 通知・確認モード（既定）
  python main.py --mode push           # OTA連携まで実行（dry-run）
  python main.py --days 7              # 対象日数を変更
"""
import argparse
from datetime import date, timedelta

from config import PricingConfig
from notifier import build_report, notify
from occupancy import load_occupancy
from ota_connector import NeppanConnector, RateUpdate
from pricing_engine import suggest_price
from scraper import fetch_competitor_rates

CURRENT_FLAT_PRICE = 18000  # 現行運用（コンサル委託時点の固定価格）との比較用


def run(start_date: date, days: int, mode: str) -> None:
    cfg = PricingConfig()
    occupancy_by_date = load_occupancy()
    market_by_date = fetch_competitor_rates()

    suggestions = []
    for offset in range(days):
        target_date = start_date + timedelta(days=offset)
        key = target_date.isoformat()

        suggestion = suggest_price(
            target_date=target_date,
            occupancy_rate=occupancy_by_date.get(key, 0.5),
            lead_time_days=(target_date - date.today()).days,
            market_summary=market_by_date.get(key),
            cfg=cfg,
        )
        suggestions.append(suggestion)

    report = build_report(CURRENT_FLAT_PRICE, suggestions)
    notify(report)

    if mode == "push":
        connector = NeppanConnector(dry_run=True)
        updates = [
            RateUpdate(target_date=s.target_date, price=s.suggested_price)
            for s in suggestions
        ]
        results = connector.push_rates(updates)
        print("\n=== OTA連携結果（dry-run） ===")
        for r in results:
            print(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="宿泊価格自動算出デモ")
    parser.add_argument(
        "--start-date",
        default=None,
        help="YYYY-MM-DD（未指定時は本日+14日。fixture生成時の起点と合わせている）",
    )
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--mode", choices=["notify", "push"], default="notify")
    args = parser.parse_args()

    start = (
        date.fromisoformat(args.start_date)
        if args.start_date
        else date.today() + timedelta(days=14)
    )
    run(start_date=start, days=args.days, mode=args.mode)
