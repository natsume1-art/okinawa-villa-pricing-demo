"""デモ用のサンプルデータ（予約状況・競合相場スナップショット）を生成する。

実サイトへのスクレイピングは許可なく行うべきではないため、
このデモでは「競合サイトから取得したHTML」を模したfixtureをローカルに生成し、
scraper.py がそれを解析するオフライン完結構成にしている。
"""
import random
from datetime import date, timedelta
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

ROOM_COUNT = 12
DAYS = 30
# 実行時点から14日後を起点にする（lead_time計算が常に未来日程になるようにするため）
START_DATE = date.today() + timedelta(days=14)

COMPETITOR_VILLAS = [
    {"name": "コーラルヴィラ恩納", "base": 22000},
    {"name": "オーシャンテラス読谷", "base": 19500},
    {"name": "ブルーサンズ北谷", "base": 17800},
    {"name": "リーフコテージ名護", "base": 20500},
    {"name": "サザンヴィラ南城", "base": 16800},
]


def generate_reservations_csv() -> None:
    random.seed(42)
    rows = ["date,room_id,status"]
    for day_offset in range(DAYS):
        current = START_DATE + timedelta(days=day_offset)
        # 週末・ハイシーズンほど埋まりやすいという傾向を再現
        is_weekend = current.weekday() in (4, 5)  # 金・土
        base_fill_rate = 0.75 if is_weekend else 0.45
        for room_id in range(1, ROOM_COUNT + 1):
            booked = random.random() < base_fill_rate
            status = "booked" if booked else "available"
            rows.append(f"{current.isoformat()},room-{room_id:02d},{status}")

    out_path = FIXTURES_DIR / "reservations_sample.csv"
    out_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")


def generate_competitor_html() -> None:
    random.seed(7)
    cards = []
    for day_offset in range(DAYS):
        current = START_DATE + timedelta(days=day_offset)
        is_weekend = current.weekday() in (4, 5)
        for villa in COMPETITOR_VILLAS:
            fluctuation = random.uniform(-0.08, 0.10)
            weekend_bump = 1.15 if is_weekend else 1.0
            price = round(villa["base"] * weekend_bump * (1 + fluctuation), -2)
            cards.append(
                f'<div class="rate-card" data-date="{current.isoformat()}" '
                f'data-villa="{villa["name"]}" data-price="{int(price)}"></div>'
            )

    html = (
        "<html><body><div id=\"listing\">\n"
        + "\n".join(cards)
        + "\n</div></body></html>\n"
    )
    out_path = FIXTURES_DIR / "competitor_rates_sample.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    generate_reservations_csv()
    generate_competitor_html()
