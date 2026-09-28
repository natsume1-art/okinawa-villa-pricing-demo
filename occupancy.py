"""予約データから日付ごとの稼働率を算出するモジュール。

本番ではPMS/サイトコントローラーのDB・APIから取得する想定だが、
このデモではCSV（date,room_id,status）を読み込む形にしている。
"""
import csv
from collections import defaultdict
from pathlib import Path
from typing import Optional

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
DEFAULT_FIXTURE = FIXTURES_DIR / "reservations_sample.csv"


def load_occupancy(fixture_path: Optional[Path] = None) -> dict:
    """日付をキーとした稼働率（0.0〜1.0）の辞書を返す。"""
    path = fixture_path or DEFAULT_FIXTURE
    booked_counts = defaultdict(int)
    total_counts = defaultdict(int)

    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = row["date"]
            total_counts[d] += 1
            if row["status"] == "booked":
                booked_counts[d] += 1

    return {
        d: booked_counts[d] / total_counts[d]
        for d in total_counts
        if total_counts[d] > 0
    }


if __name__ == "__main__":
    occ = load_occupancy()
    for d in sorted(occ)[:5]:
        print(d, f"{occ[d]:.0%}")
